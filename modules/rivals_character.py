import re, os, shutil, glob

class RivalsCharacter():
    AnimationNames = ['idle', 'walk', 'walkturn', 'jump', 'jumpstart', 'walljump', 'doublejump',
        'airdodge', 'airdodge_forward', 'airdodge_back', 'airdodge_up', 'airdodge_upforward', 'airdodge_upback', 'airdodge_down', 'airdodge_downforward', 'airdodge_downback',
        'plat', 'dash', 'dashstart', 'dashstop', 'dashturn', 'land', 'landinglag', 'waveland', 'pratfall', 'crouch', 'tech', 'roll_forward', 'roll_backward', 'parry',
        'hurt', 'bighurt', 'hurtground', 'bouncehurt', 'spinhurt', 'uphurt', 'downhurt', 'jab', 'dattack', 'nspecial', 'fspecial', 'uspecial',
        'dspecial', 'fstrong', 'ustrong', 'dstrong', 'ftilt', 'utilt',
        'dtilt', 'nair', 'fair', 'bair', 'dair', 'uair', 'taunt']

    # Creates the object with empty values
    def __init__(self):
        self.base_folder = None
        self.config_ini = {}
        self.init_script = {}
        self.animations = {anim_name : RivalsAnimation(anim_name) for anim_name in RivalsCharacter.AnimationNames}

    # Reads from the mugen character file to create the object
    def parse(self, base_folder):
        self.base_folder = base_folder
        self.parse_config_ini()
        self.parse_load_gml()
        self.parse_init_gml()
        self.parse_attack_scripts()

    # Converts the object's data back into the original files and folder structure
    def unparse_character(self, output_folder):
        self.unparse_config_ini(output_folder)
        self.parse_animations()
        self.unparse_load_gml(output_folder)
        self.unparse_init_gml(output_folder)
        self.unparse_attack_scripts(output_folder)
        self.unparse_spritesheets(output_folder)

    # Returns itself if the conversion type is Rivals
    def convert_to_rivals(self, output_folder):
        print("Converting in place from Rivals to Rivals")
        os.mkdir(output_folder + "/character")
        os.mkdir(output_folder + "/character/scripts")
        os.mkdir(output_folder + "/character/scripts/attacks")
        os.mkdir(output_folder + "/character/sprites")
        self.unparse_character(output_folder)

    def parse_config_ini(self):
        f = open(self.base_folder + "/config.ini", encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if "=" in line:
                line = line.split(";")[0].strip()
                key, value = line.split("=")
                self.config_ini[key] = value

    def parse_animations(self):
        for anim in self.animations.values():
            for filename in os.listdir(self.base_folder + "/sprites/"):
                if filename.startswith(anim.name):
                    if "hurt" in filename:
                        anim.hurt_animation_filepath = "/sprites/" + filename
                    else:
                        anim.animation_filepath = "/sprites/" + filename

    
    # Parses the load.gml file and finds all the animation offset values
    def parse_load_gml(self):
        f = open(self.base_folder + "/scripts/load.gml", encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if line.startswith("sprite_change_offset"):
                line = re.search( "\((.*)\)" , line).group(1)
                anim_name, offset_x, offset_y = line.split(",") # extract the values from the line
                anim_name = anim_name.replace('"', '').replace("'", '')
                if anim_name in self.animations:
                    self.animations.get(anim_name).offset = (offset_x, offset_y)
        f.close()

    # Parses the content of the init.gml file
    def parse_init_gml(self):
        f = open(self.base_folder + "/scripts/init.gml", encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if '=' in line:
                name = line.split('=')[0].strip()
                value = line.split('=')[1].replace(';', '')
                value = value.strip().split("//")[0]
                self.init_script[name] = value
        f.close()

    # Parses the content of the scripts found in the /scripts/attacks/ folder
    def parse_attack_scripts(self):
        for file in os.listdir(self.base_folder + "/scripts/attacks/"):
            anim_name = file.rstrip(".gml")
            if anim_name in self.animations:
                f = open(self.base_folder + "/scripts/attacks/" + file)
                lines = f.readlines()
                for line in lines:
                    if line.startswith("set_"):
                        command_type = line.split("(")[0].strip()
                        line = re.search( "\((.*)\)" , line).group(1)
                        values = line.split(",")
                        if command_type == 'set_attack_value':
                            index = values[1].strip()
                            value = values[2].strip()
                            self.animations.get(anim_name).attack_values[index] = value
                        elif command_type == 'set_window_value':
                            window_number = values[1].strip()
                            index = values[2].strip()
                            value = values[3].strip()
                            if not window_number in self.animations.get(anim_name).windows:
                                self.animations.get(anim_name).windows[window_number] = {}
                            self.animations.get(anim_name).windows[window_number][index] = value
                        elif command_type == 'set_num_hitboxes':
                            value = values[1].strip()
                            self.animations.get(anim_name).num_hitboxes = value
                        elif command_type == 'set_hitbox_value':
                            hitbox_number = values[1].strip()
                            index = values[2].strip()
                            value = values[3].strip()
                            if not hitbox_number in self.animations.get(anim_name).hitboxes:
                                self.animations.get(anim_name).hitboxes[hitbox_number] = {}
                            self.animations.get(anim_name).hitboxes[hitbox_number][index] = value
                self.animations.get(anim_name).filepath = "/character_files/scripts/attacks/"

    # Writes a new config.ini file based on the character data
    def unparse_config_ini(self, output_folder):
        f = open(output_folder + "/character_files/config.ini", "x")
        f.write("[general]")
        for key, value in self.config_ini.items():
            f.write(key + "=" + value + "\n")
        f.close()

    # Writes a new load.gml file in the output folder based on the character data
    def unparse_load_gml(self, output_folder):
        f = open(output_folder + "/character_files/scripts/load.gml", "x")
        for animation in self.animations.values():
        #    if animation.name == 'idle'
            if animation.offset[0] or animation.offset[1]:
                line = 'sprite_change_offset("' + animation.name + '"' + ", " + str(animation.offset[0]) + ", " + str(animation.offset[1]) + ");\n"
                f.write(line)
        f.write("\n")
        f.close()

    # Writes a new init.gml file in the output folder based on the character data
    def unparse_init_gml(self, output_folder):
        f = open(output_folder + "/character_files/scripts/init.gml", "x")
        for name, value in self.init_script.items():
            line = name + ' = ' + value + ';\n'
            f.write(line)
        f.close()

    #Writes new attack .gml scripts to the output /scripts/attacks folder based on character data
    def unparse_attack_scripts(self, output_folder):
        # TODO: UPDATE THIS
        # The attack/animation dictonaries should be 1 large dict. It should include both the mapped and raw items.
        # All the information on where to output them, and under what name, should be contained in the object
        for anim_nb, animation in self.animations.items():
            if animation.filepath and animation.attack_values:
                f = open(output_folder + animation.filepath + animation.name + ".gml", "x")
                for key, value in animation.attack_values.items():
                    line = ("set_attack_value(AT_" + str(anim_nb).upper() +
                        ", " + key + ", " + value + ");\n")
                    f.write(line)
                f.write("\n")
                for nb, window in animation.windows.items():
                    for key, value in window.items():
                        line = ("set_window_value(AT_" + str(anim_nb).upper() +
                                ", " + nb + ", " + key + ", " + value + ");\n")
                        f.write(line)
                    f.write("\n")
                line = "set_num_hitboxes(AT_" + str(anim_nb).upper() + ", " + animation.num_hitboxes + ");\n"
                f.write(line)
                for nb, hitbox in animation.hitboxes.items():
                    for key, value in hitbox.items():
                        line = ("set_hitbox_value(AT_" + str(anim_nb).upper() + ", " + nb + ", " +
                            key + ", " + value + ");\n")
                        f.write(line)
                    f.write("\n")
                f.close

    # Copy converted spritesheets to the /sprites/ output folder
    def unparse_spritesheets(self, output_folder):
        for anim in self.animations.values():
            if anim.animation_filepath:
                shutil.copy2(anim.animation_filepath,
                    output_folder + "/character/sprites/" + os.path.basename(anim.animation_filepath))
            if anim.hurt_animation_filepath:
                shutil.copy2(output_folder + anim.hurt_animation_filepath,
                    output_folder + "/character/sprites/" + os.path.basename(anim.hurt_animation_filepath))


    def create_character_folder(self, output_folder, mapping):
        # 1. Have it create a dict of rivals animations with the right name and folder, replacing the one already used
        # 2. final_character.unparse_spritesheets()

        os.mkdir(output_folder + "/character")
        os.mkdir(output_folder + "/character/scripts")
        os.mkdir(output_folder + "/character/scripts/attacks")
        os.mkdir(output_folder + "/character/sprites")

        mapped_anims = {}
        f = open(mapping.strip(), encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if "=" in line:
                line = line.replace(" ", "").replace("\n", "")
                rivals_anim_name = line.split("=")[0]
                anim_number = line.split("=")[1]
                image_filename = glob.glob(output_folder + "/raw_output/" + anim_number + "_strip*.png")
                if image_filename:
                    image_filename = image_filename[0]
                    frame_count = image_filename.split("_strip")[1].split(".")[0]
                    output_filename = output_folder + "/character/sprites/" + rivals_anim_name + "_strip" + frame_count + ".png"
                    shutil.copy2(image_filename, output_filename)
                hurt_filename = glob.glob(output_folder + "/raw_output/" + anim_number + "_hurt_strip*.png")
                if hurt_filename:
                    hurt_filename = hurt_filename[0]
                    frame_count = hurt_filename.split("_strip")[1].split(".")[0]
                    output_filename = output_folder + "/character/sprites/" + rivals_anim_name + "_hurt_strip" + frame_count + ".png"
                    shutil.copy2(hurt_filename, output_filename)

                    


class RivalsAnimation:
    def __init__(self, name):
        self.name = name
        self.offset = (0, 0)
        self.filepath = None
        self.animation_filepath = None
        self.hurt_animation_filepath = None
        self.attack_values = {}
        self.windows = {}
        self.num_hitboxes = '0'
        self.hitboxes = {}
