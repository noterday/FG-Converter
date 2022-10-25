from modules.rivals_character import RivalsCharacter, RivalsAnimation
from modules.sff import read_sff
import re, os, configparser, subprocess, copy
from PIL import Image

# Represents an animation as defined in the .air file
class MugenAnimation:
    def __init__(self, id):
        self.id = id
        self.clsn2default = [] # Default Collision Boxes (hurtbox)
        self.animation_elements = []
        self.converted_sheet = ''
        self.converted_hurt_sheet = ''
        self.extra_conversion_param = ''


# Represents a specific frame of a mugen animation
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


class MugenCharacter():
    # Creates a new character with empty values
    def __init__(self):
        self.def_file = {}
        self.palettes = {}
        self.sprites = {}
        self.animations = {}
    
    def convert_to_mugen(self, output_folder):
        pass

    # Reads from the mugen character file to create the object
    def parse(self, base_folder):
        self.base_folder = base_folder
        self.def_file = self.parse_def_file()
        self.parse_sff_file()
        self.animations = self.parse_air_file() # TODO: Let airfile parser handle loops

    # Parses the .def file to find the author information and path of other useful files
    def parse_def_file(self):
        def_file = {}
        config = configparser.ConfigParser(inline_comment_prefixes=';')
        for file in os.listdir(self.base_folder):
            if not file.startswith("intro") and not file.startswith("ending"):
                if file.endswith(".def"):
                    with open(self.base_folder + "/" + file, encoding="latin-1") as open_file:
                        if "[Info]" in open_file.read():
                            config.read(self.base_folder + "/" + file, encoding="latin-1")
                            def_file = config
        for file in os.listdir(self.base_folder):
            if not file.startswith("intro") and not file.startswith("ending"):
                if file.endswith(".sff"):
                    def_file["Files"]["sprite"] = file
                elif file.endswith(".air"):
                    def_file["Files"]["anim"] = file
        return def_file

    # Parses the .sff and palette files
    def parse_sff_file(self):
        sprite_file = self.base_folder + "/" + self.def_file["Files"]["sprite"]
        pal_files = []
        for key, value in self.def_file["Files"].items():
            if key.startswith("pal"):
                pal_files.append(self.base_folder + "/" + value)

        self.sprites, self.palettes = read_sff(sprite_file, pal_files)

    # Parse the content of the .air file (animation information)
    def parse_air_file(self):
        animations = {}
        f = open(self.base_folder + "/" + self.def_file["Files"]["anim"], encoding="latin-1")
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
                animations[current_action_nb] = MugenAnimation(current_action_nb)
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
                    animations[current_action_nb].clsn2default.append(collision_box_definition)
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
                animations[current_action_nb].animation_elements.append(MugenAnimationElement())
                animations[current_action_nb].animation_elements[-1].clsn1 = stored_clsn1
                animations[current_action_nb].animation_elements[-1].clsn2 = stored_clsn2
                #    self.optional_parameters = ""
                values = line.split(',')
                if (values[0], values[1]) in self.sprites:
                    animations[current_action_nb].animation_elements[-1].group_number = values[0]
                    animations[current_action_nb].animation_elements[-1].image_number = values[1]
                else:
                    animations[current_action_nb].animation_elements[-1].group_number = '0'
                    animations[current_action_nb].animation_elements[-1].image_number = '0'
                animations[current_action_nb].animation_elements[-1].x_offset = int(values[2])
                animations[current_action_nb].animation_elements[-1].y_offset = int(values[3])
                animations[current_action_nb].animation_elements[-1].length = int(values[4])
                additional_values = values[5:]
                if additional_values:
                    animations[current_action_nb].animation_elements[-1].optional_parameters = additional_values
                stored_clsn1 = []
                stored_clsn2 = []
        return animations

    # Parse the .cmd file (unused)
    def parse_cmd_file():
        pass

    # Parses the .cns file
    def parse_cns_file():
        pass

    # Creates a RivalsCharacter object using this object's data
    def convert_to_rivals(self, output_folder):
        # Create the rivals character object
        os.mkdir(output_folder + "/raw_output")

        path = os.path.dirname(__file__)
        final_character = RivalsCharacter()
        # Do all the conversion work here
        self.create_rivals_config_ini(final_character)
        load_gml_offset = self.create_rivals_animation_sheets(output_folder)
        self.convert_rivals_animations_and_attacks(final_character, load_gml_offset)
        final_character.unparse_attack_scripts(output_folder)
        return final_character

    # Converts the config.ini file based on information from the .def file
    def create_rivals_config_ini(self, final_character):
        def_file_info_section = dict(self.def_file["Info"].items())
        final_character.config_ini["name"] = def_file_info_section["name"]
        final_character.config_ini["author"] = def_file_info_section["author"]
        final_character.config_ini["description"] = (
            '"This character is a conversion from Mugen. Original author: ' + def_file_info_section["author"].replace('"', '') + '"')

    # Reads the input mapping file if one was given
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

    # Converts the animations to the Rivals spritesheet format
    def create_rivals_animation_sheets(self, output_folder):
        offsets = {}
        for id, animation in self.animations.items():
            if id == 9960:
                #find why this one crashes (on sf3 ryu)
                break
            biggest_image_dimensions = [0, 0]
            biggest_axis_position = [0, 0]
            images = []
            for element in animation.animation_elements:
                # This is iterating through 1 frame of the animation at a time
                sprite = self.sprites[(element.group_number, element.image_number)]
                image = sprite.final_image
                images.append(image)
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
                if sprite.axis[0] > biggest_axis_position[0]:
                    biggest_axis_position[0] = sprite.axis[0]
                if sprite.axis[1] > biggest_axis_position[1]:
                    biggest_axis_position[1] = sprite.axis[1]
                image_size = (images[-1].size[0]+10 + (biggest_axis_position[0] - sprite.axis[0]),
                            images[-1].size[1] + (biggest_axis_position[1] - sprite.axis[1]))
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
                sprite = self.sprites[(element.group_number, element.image_number)]
                # Fit any offset within the image
                if abs(element.x_offset) > biggest_image_dimensions[0]:
                    element.x_offset = (abs(element.x_offset) - biggest_image_dimensions[1]) * (abs(element.x_offset) / element.x_offset)
                if abs(element.y_offset) > biggest_image_dimensions[1]:
                    element.y_offset = (abs(element.y_offset) - biggest_image_dimensions[1]) * (abs(element.y_offset) / element.y_offset)
                position = [i * biggest_image_dimensions[0], 0]
                position[0] = position[0] + (biggest_axis_position[0] - sprite.axis[0]) + element.x_offset
                position[1] = position[1] + (biggest_axis_position[1] - sprite.axis[1]) + element.y_offset
                spritesheet.paste(add_alpha(image), (int(position[0]), int(position[1])), mask=0)
            alpha = spritesheet.getchannel("A")
            hurtboxsheet = Image.new('RGBA', (biggest_image_dimensions[0]*len(images), biggest_image_dimensions[1]), (0,255,0,255))
            hurtboxsheet.putalpha(alpha)
            filename = str(id) + "_strip" + str(len(images)) + '.png'
            hurt_filename = str(id)+ "_hurt_strip" + str(len(images)) + '.png'
            try:
                spritesheet.save(output_folder + "/raw_output/" + filename)
                hurtboxsheet.save(output_folder + "/raw_output/" + hurt_filename)
            except Exception:
                print("Failed to save the image " + filename)
            offsets[id] = biggest_axis_position
            animation.converted_sheet = "/raw_output/" + filename
            animation.converted_hurt_sheet ="/raw_output/" + hurt_filename
        return offsets

    # Converts the animation and attack scripts to Rivals formats
    def convert_rivals_animations_and_attacks(self, final_character, load_gml_offset):
        for animation_number, animation_obj in self.animations.items():
            if animation_number == 9960:
                break # todo: find why this one breaks
            rival_attack = RivalsAnimation(str(animation_number))
            rival_attack.offset = load_gml_offset[animation_number]
            rival_attack.filename = self.animations[animation_number].converted_sheet
            rival_attack.hurt_filename = self.animations[animation_number].converted_hurt_sheet
            current_window_length = 0
            frames_in_current_window = 0
            window_count = 0
            hitbox_count = 0
            for i in range(len(animation_obj.animation_elements)):
                element = animation_obj.animation_elements[i]
                if element.length != current_window_length:
                    window_count += 1
                    rival_attack.windows[str(window_count)] = {}
                    if i:
                        rival_attack.windows[str(window_count)]['AG_WINDOW_ANIM_FRAME_START'] = str(i)
                    current_window_length = element.length
                    frames_in_current_window = 0
                frames_in_current_window += 1
                rival_attack.attack_values['AG_SPRITE'] = 'sprite_get("' + rival_attack.name + '")'
                rival_attack.attack_values['AG_HURTBOX_SPRITE'] = 'sprite_get("' + rival_attack.name + '_hurt")'
                rival_attack.windows[str(window_count)]['AG_WINDOW_TYPE'] = '1'
                rival_attack.windows[str(window_count)]['AG_WINDOW_ANIM_FRAMES'] = str(frames_in_current_window)
                rival_attack.windows[str(window_count)]['AG_WINDOW_LENGTH'] = str(frames_in_current_window * current_window_length)
                # Convert the hitboxes
                for clsn1 in element.clsn1:
                    hitbox_count += 1
                    start_pos = clsn1[0], clsn1[1]
                    size = clsn1[2] - clsn1[0], clsn1[3] - clsn1[1]
                    rival_attack.hitboxes[str(hitbox_count)] = {}
                    rival_attack.hitboxes[str(hitbox_count)]['HG_HITBOX_TYPE'] = '1'
                    rival_attack.hitboxes[str(hitbox_count)]['HG_WINDOW'] = str(window_count)
                    rival_attack.hitboxes[str(hitbox_count)]['HG_LIFETIME'] = '2'
                    rival_attack.hitboxes[str(hitbox_count)]['HG_HITBOX_X'] = str(round(start_pos[0] + size[0]/2))
                    rival_attack.hitboxes[str(hitbox_count)]['HG_HITBOX_Y'] = str(round(start_pos[1] + size[1]/2))
                    rival_attack.hitboxes[str(hitbox_count)]['HG_WIDTH'] = str(size[0])
                    rival_attack.hitboxes[str(hitbox_count)]['HG_HEIGHT'] = str(size[1])
                    rival_attack.hitboxes[str(hitbox_count)]['HG_PRIORITY'] = '1'
                    rival_attack.hitboxes[str(hitbox_count)]['HG_DAMAGE'] = '1'
                    rival_attack.hitboxes[str(hitbox_count)]['HG_ANGLE'] = '1'
                    rival_attack.hitboxes[str(hitbox_count)]['HG_BASE_KNOCKBACK'] = '1'
                    rival_attack.hitboxes[str(hitbox_count)]['HG_BASE_HITPAUSE'] = '1'
            rival_attack.num_hitboxes = str(hitbox_count)
            rival_attack.attack_values['AG_NUM_WINDOWS'] = str(len(rival_attack.windows))
            rival_attack.filepath = "/raw_output/"
            rival_attack.animation_filepath = animation_obj.converted_sheet
            rival_attack.hurt_animation_filepath = animation_obj.converted_hurt_sheet
            final_character.animations[animation_number] = rival_attack
        # Get height at idle
        if final_character.animations['idle']:
            return # Todo needs to have handled sprite paths first
            if final_character.animations['idle'].filepath:
                idle_sprite = Image.open(final_character.animations['idle'].filename)
                height = idle_sprite.size[1]
                final_character.init_script['char_height'] = str(height)


# Modifies the given image to make it transparent (assuming the first pixel of the image is the background color)
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