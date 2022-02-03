from modules.generic_character import GenericCharacter
from modules.rivals_character import RivalsCharacter, RivalsAnimation, RivalsAttack

import re, os, configparser, subprocess, copy
from PIL import Image


AnimationNames = ['roll_forward', 'roll_backward']

class MugenCharacter(GenericCharacter):
    def __init__(self, base_folder):
        self.def_file = {}
        self.sff_sprites = {}
        self.animations = {}
        super().__init__(base_folder)

    # Reads from the mugen character file to create the object
    def parse_folder(self, output_folder):
        self.parse_def_file()
        self.parse_sff_file(output_folder)
        self.parse_air_file() # TODO: Let airfile parser handle loops

    def parse_def_file(self):
        config = configparser.ConfigParser(inline_comment_prefixes=';')
        for file in os.listdir(self.base_folder):
            if file.endswith(".def"):
                with open(self.base_folder + "/" + file) as open_file:
                    if "[Info]" in open_file.read():
                        config.read(self.base_folder + "/" + file)
                        self.def_file = config

    def parse_sff_file(self, output_folder):
        subprocess.run([os.path.dirname(__file__) + "/mugen/sff2png.exe", self.base_folder + "/" + self.def_file["Files"]["sprite"],
            output_folder + "/converted_actions/extracted_sprites/sprite", "-f 0"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        sprite_section = False
        f = open(output_folder + "/converted_actions/extracted_sprites/sprite-sff.def", encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if sprite_section:
                line = line.replace(" ", "").split(",")
                self.sff_sprites[(line[0], line[1])] = MugenSprite(line[0], line[1], line[2], int(line[3]), int(line[4]))
            elif line.startswith("[Sprite]"):
                sprite_section = True

    def parse_air_file(self):
        f = open(self.base_folder + "/" + self.def_file["Files"]["anim"])
        lines = f.readlines()
        current_action_nb = -1
        wanted_clsn2default_nb = 0
        wanted_clsn1 = 0
        wanted_clsn2 = 0
        stored_clsn1 = []
        stored_clsn2 = []
        for line in lines:
            line = line.strip().rstrip("\n").partition(";")[0]
            line = line.replace(" ", "")
            if re.match("[Begin Action [0-9]+]", line):
                # Matches the start of a new action
                current_action_nb = int(line.lstrip("[Begin Action").rstrip("]"))
                self.animations[current_action_nb] = MugenAnimation(current_action_nb)
                wanted_clsn2default_nb = 0
                stored_clsn1 = []
                stored_clsn2 = []
            elif re.match("Clsn2Default*", line):
                # Matches the line that defines the number of default clsn2 (hurtboxes used for the entire animation)
                wanted_clsn2default_nb = int(line.split(":")[1])
            elif re.match("Clsn1:", line):
                # Matches the line that defines the number of clsn1 for a frame (hitboxes)
                wanted_clsn1 = int(line.split(":")[1])
            elif re.match("Clsn2:", line):
                # Matches the line that defines the number of clsn2 for a frame (hurtboxes)
                wanted_clsn2 = int(line.split(":")[1])
            elif re.match("Clsn2\[.+\]=" , line):
                # Matches the definition of a Clsn2 box (hurtbox)
                collision_box_definition = [int(value) for value in line.split('=')[1].split(',')]
                if wanted_clsn2default_nb > 0: # If working on Clsn2Default
                    self.animations[current_action_nb].clsn2default.append(collision_box_definition)
                    wanted_clsn2default_nb -= 1
                else: # If working on normal Clsn2
                    if wanted_clsn2 > 0:
                        stored_clsn2.append(collision_box_definition)
                        wanted_clsn2 -= 1
            elif re.match("Clsn1\[.+\]=" , line):
                # Matches the definition of a Clsn1 box (hitbox)
                collision_box_definition = [int(value) for value in line.split('=')[1].split(',')]
                if wanted_clsn1 > 0:
                    stored_clsn1.append(collision_box_definition)
                    wanted_clsn1 -= 1
            elif re.match("[0-9]+,[0-9]+,-*[0-9]+,-*[0-9]+,-*[0-9]+,*.*", line):
                self.animations[current_action_nb].animation_elements.append(MugenAnimationElement())
                self.animations[current_action_nb].animation_elements[-1].clsn1 = stored_clsn1
                self.animations[current_action_nb].animation_elements[-1].clsn2 = stored_clsn2
                #    self.optional_parameters = ""
                values = line.split(',')
                self.animations[current_action_nb].animation_elements[-1].group_number = values[0]
                self.animations[current_action_nb].animation_elements[-1].image_number = values[1]
                self.animations[current_action_nb].animation_elements[-1].x_offset = int(values[2])
                self.animations[current_action_nb].animation_elements[-1].y_offset = int(values[3])
                self.animations[current_action_nb].animation_elements[-1].length = int(values[4])
                additional_values = values[5:]
                if additional_values:
                    self.animations[current_action_nb].animation_elements[-1].optional_parameters = additional_values
                stored_clsn1 = []
                stored_clsn2 = []

    def parse_cmd_file():
        pass

    # Creates a RivalsCharacter object using this object's data
    def convert_to_rivals(self, output_folder, input_mapping_file):
        # Create the rivals character object
        path = os.path.dirname(__file__)
        final_character = RivalsCharacter(path + "/base-character-files/Sandbert-Scripts")
        final_character.parse_folder()
        final_character.base_folder = self.base_folder
        # Do all the conversion work here
        self.create_rivals_config_ini(final_character)
        input_mapping = self.read_input_mapping_file(input_mapping_file)
        load_gml_offset = self.create_rivals_animation_sheets(final_character, output_folder, input_mapping)
        self.convert_rivals_animations_and_attacks(final_character, input_mapping, load_gml_offset)
        return final_character

    def create_rivals_config_ini(self, final_character):
        def_file_info_section = dict(self.def_file["Info"].items())
        final_character.config_ini["name"] = def_file_info_section["name"]
        final_character.config_ini["author"] = def_file_info_section["author"]
        final_character.config_ini["description"] = (
            '"This character is a conversion from Mugen. Original author: ' + def_file_info_section["author"].replace('"', '') + '"')

    def read_input_mapping_file(self, input_mapping_file):
        input_mapping = {}
        f = open(input_mapping_file)
        lines = f.readlines()
        for line in lines:
            line = line.split(';')[0].strip().replace(" ", "")
            if '=' in line:
                rival_name, mugen_number = line.split('=')
                mugen_number = mugen_number.split(',')
                mugen_number[0] = int(mugen_number[0])
                input_mapping[rival_name] = mugen_number
        return input_mapping

    def create_rivals_animation_sheets(self, final_character, output_folder, input_mapping):
        offsets = {}
        for mapping in input_mapping.values():
            if len(mapping) > 1:
                new_animation = copy.deepcopy(self.animations[mapping[0]])
                new_animation.extra_conversion_param = mapping[1]
                self.animations[str(mapping[0])+mapping[1]] = new_animation
        for id, animation in self.animations.items():
            biggest_image_dimensions = [0, 0]
            biggest_axis_position = [0, 0]
            images = []
            for element in animation.animation_elements:
                # This is iterating through 1 frame of the animation at a time
                sprite = self.sff_sprites[(element.group_number, element.image_number)]
                images.append(Image.open(sprite.fname).copy())
                # Flip image according to optional arguments
                image = images[-1]
                for param in element.optional_parameters:
                    for char in param:
                        if char == 'V':
                            images[-1] = image.transpose(Image.FLIP_TOP_BOTTOM)
                        if char == 'H':
                            images[-1] = image.transpose(Image.FLIP_LEFT_RIGHT)
                        if char == 'R':
                            images[-1] = image.rotate(90, expand=True)
                for char in animation.extra_conversion_param:
                    if char == 'V':
                        images[-1] = image.transpose(Image.FLIP_TOP_BOTTOM)
                    if char == 'H':
                        images[-1] = image.transpose(Image.FLIP_LEFT_RIGHT)
                    if char == 'R':
                        images[-1] = image.rotate(90, expand=True)
                if sprite.axisx > biggest_axis_position[0]:
                    biggest_axis_position[0] = sprite.axisx
                if sprite.axisy > biggest_axis_position[1]:
                    biggest_axis_position[1] = sprite.axisy
                image_size = (images[-1].size[0]+10 + (biggest_axis_position[0] - sprite.axisx),
                            images[-1].size[1] + (biggest_axis_position[1] - sprite.axisy))
                if image_size[0] > biggest_image_dimensions[0]:
                    biggest_image_dimensions[0] = image_size[0]
                if image_size[1] > biggest_image_dimensions[1]:
                    biggest_image_dimensions[1] = image_size[1]
            # Create the final image file
            spritesheet = Image.new('RGBA', (biggest_image_dimensions[0]*len(images), biggest_image_dimensions[1]), (0,0,0,0))
            # Paste the elements into the new spritesheet
            left_adjust = 0 # Idk~
            for i in range(len(animation.animation_elements)):
                image = images[i]
                element = animation.animation_elements[i]
                sprite = self.sff_sprites[(element.group_number, element.image_number)]
                # Fit any offset within the image
                if abs(element.x_offset) > biggest_image_dimensions[0]:
                    element.x_offset = (abs(element.x_offset) - biggest_image_dimensions[1]) * (abs(element.x_offset) / element.x_offset)
                if abs(element.y_offset) > biggest_image_dimensions[1]:
                    element.y_offset = (abs(element.y_offset) - biggest_image_dimensions[1]) * (abs(element.y_offset) / element.y_offset)
                position = [i * biggest_image_dimensions[0], 0]
                position[0] = position[0] + (biggest_axis_position[0] - sprite.axisx) + element.x_offset
                position[1] = position[1] + (biggest_axis_position[1] - sprite.axisy) + element.y_offset
                spritesheet.paste(add_alpha(image), (int(position[0]), int(position[1])), mask=0)

            alpha = spritesheet.getchannel("A")
            hurtboxsheet = Image.new('RGBA', (biggest_image_dimensions[0]*len(images), biggest_image_dimensions[1]), (0,255,0,255))
            hurtboxsheet.putalpha(alpha)
            filename = str(id) + "_strip" + str(len(images)) + '.png'
            hurt_filename = str(id)+ "_hurt_strip" + str(len(images)) + '.png'
            spritesheet.save(output_folder + "/converted_actions/" + filename)
            hurtboxsheet.save(output_folder + "/converted_actions/" + hurt_filename)
            offsets[id] = biggest_axis_position
            animation.converted_sheet = output_folder + "/" + "converted_actions/" + filename
            animation.converted_hurt_sheet = output_folder + "/" + "converted_actions/" + hurt_filename
        return offsets

    def convert_rivals_animations_and_attacks(self, final_character, input_mapping, load_gml_offset):
        for animation_name, animation in final_character.animations.items():
            if animation_name in input_mapping.keys():
                mugen_nb = int(input_mapping[animation_name][0])
                animation.offset = load_gml_offset[mugen_nb]
                animation.filename = self.animations[mugen_nb].converted_sheet
                animation.hurt_filename = self.animations[mugen_nb].converted_hurt_sheet
        for attack_name, attack in final_character.attacks.items():
            if attack_name in input_mapping.keys():
                mugen_nb = int(input_mapping[attack_name][0])
                attack.offset = load_gml_offset[mugen_nb]
                if len(input_mapping[attack_name]) > 1:
                    attack.filename = self.animations[str(mugen_nb) + input_mapping[attack_name][1]].converted_sheet
                    attack.hurt_filename = self.animations[str(mugen_nb) + input_mapping[attack_name][1]].converted_hurt_sheet
                else:
                    attack.filename = self.animations[mugen_nb].converted_sheet
                    attack.hurt_filename = self.animations[mugen_nb].converted_hurt_sheet
                # Convert the animation timings
                current_window_length = 0
                frames_in_current_window = 0
                window_count = 0
                hitbox_count = 0
                for i in range(len(self.animations[mugen_nb].animation_elements)):
                    element = self.animations[mugen_nb].animation_elements[i]
                    if element.length != current_window_length:
                        window_count += 1
                        attack.windows[str(window_count)] = {}
                        if i:
                            attack.windows[str(window_count)]['AG_WINDOW_ANIM_FRAME_START'] = str(i)
                        current_window_length = element.length
                        frames_in_current_window = 0
                    frames_in_current_window += 1
                    attack.windows[str(window_count)]['AG_WINDOW_TYPE'] = '1'
                    attack.windows[str(window_count)]['AG_WINDOW_ANIM_FRAMES'] = str(frames_in_current_window)
                    attack.windows[str(window_count)]['AG_WINDOW_LENGTH'] = str(frames_in_current_window * current_window_length)
                    # Convert the hitboxes
                    for clsn1 in element.clsn1:
                        hitbox_count += 1
                        start_pos = clsn1[0], clsn1[1]
                        size = clsn1[2] - clsn1[0], clsn1[3] - clsn1[1]
                        attack.hitboxes[str(hitbox_count)] = {}
                        attack.hitboxes[str(hitbox_count)]['HG_HITBOX_TYPE'] = '1'
                        attack.hitboxes[str(hitbox_count)]['HG_WINDOW'] = str(window_count)
                        attack.hitboxes[str(hitbox_count)]['HG_LIFETIME'] = '2'
                        attack.hitboxes[str(hitbox_count)]['HG_HITBOX_X'] = str(round(start_pos[0] + size[0]/2))
                        attack.hitboxes[str(hitbox_count)]['HG_HITBOX_Y'] = str(round(start_pos[1] + size[1]/2))
                        attack.hitboxes[str(hitbox_count)]['HG_WIDTH'] = str(size[0])
                        attack.hitboxes[str(hitbox_count)]['HG_HEIGHT'] = str(size[1])
                        attack.hitboxes[str(hitbox_count)]['HG_PRIORITY'] = '1'
                        attack.hitboxes[str(hitbox_count)]['HG_DAMAGE'] = '1'
                        attack.hitboxes[str(hitbox_count)]['HG_ANGLE'] = '1'
                        attack.hitboxes[str(hitbox_count)]['HG_BASE_KNOCKBACK'] = '1'
                        attack.hitboxes[str(hitbox_count)]['HG_BASE_HITPAUSE'] = '1'
                attack.num_hitboxes = str(hitbox_count)
                attack.attack_values['AG_NUM_WINDOWS'] = str(len(attack.windows))
                #attack.num_hitboxes = '0'
                #attack.hitboxes = {}

"""
    Modify a given image to make the color of the first pixel transparent
"""
def add_alpha(image):
    image = image.convert("RGBA")
    datas = image.getdata()
    newData = []
    r,g,b,a = image.getpixel((0,0))
    for item in datas:
        if item[0] == r and item[1] == g and item[2] == b:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    image.putdata(newData)
    return image

class MugenSprite:
    def __init__(self, group, itemno, fname, axisx, axisy):
        self.group = group
        self.itemno = itemno
        self.fname = fname
        self.axisx = axisx # This axis is equivalent to the offset defined in rivals characters. It's meant to indicate a point at the character's feet
        self.axisy = axisy

class MugenAnimation:
    def __init__(self, id):
        self.id = id
        self.clsn2default = [] # Default Collision Boxes (hurtbox)
        self.animation_elements = []
        self.converted_sheet = ''
        self.converted_hurt_sheet = ''
        self.extra_conversion_param = ''

class MugenAnimationElement:
    def __init__(self):
        self.group_number = -1
        self.image_number = -1
        self.x_offset = 0
        self.y_offset = 0
        self.length = 0
        self.optional_parameters = ""
        self.clsn1 = []
        self.clsn2 = []
