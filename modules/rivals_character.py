import re, os, shutil, glob

import modules.options as options

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
    def parse(self):
        self.base_folder = options.input_folder
        self.parse_config_ini()
        self.parse_load_gml()
        self.parse_init_gml()
        self.parse_attack_scripts()

    # Converts the object's data back into the original files and folder structure
    def unparse_character(self, out):
        self.unparse_config_ini(out)
        self.parse_animations()
        self.unparse_load_gml(out)
        self.unparse_init_gml(out)
        self.unparse_attack_scripts(out)

    # Returns itself if the conversion type is Rivals
    def convert_to_rivals(self):
        out = options.out
        print("Converting in place from Rivals to Rivals")
        os.mkdir(out + "/character")
        os.mkdir(out + "/character/scripts")
        os.mkdir(out + "/character/scripts/attacks")
        os.mkdir(out + "/character/sprites")
        self.unparse_character(out)

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
    def unparse_config_ini(self, out):
        f = open(out + "/character_files/config.ini", "x")
        f.write("[general]")
        for key, value in self.config_ini.items():
            f.write(key + "=" + value + "\n")
        f.close()

    # Writes a new load.gml file in the output folder based on the character data
    def unparse_load_gml(self, out):
        f = open(out + "/character_files/scripts/load.gml", "x")
        for animation in self.animations.values():
        #    if animation.name == 'idle'
            if animation.offset[0] or animation.offset[1]:
                line = 'sprite_change_offset("' + animation.name + '"' + ", " + str(animation.offset[0]) + ", " + str(animation.offset[1]) + ");\n"
                f.write(line)
        f.write("\n")
        f.close()

    # Writes a new init.gml file in the output folder based on the character data
    def unparse_init_gml(self, out):
        f = open(out + "/character_files/scripts/init.gml", "x")
        for name, value in self.init_script.items():
            line = name + ' = ' + value + ';\n'
            f.write(line)
        f.close()

    #Writes new attack .gml scripts to the output /scripts/attacks folder based on character data
    def unparse_attack_scripts(self, out):
        for anim_nb, animation in self.animations.items():
            if animation.filepath and animation.attack_values:
                f = open(out + animation.filepath + animation.name + ".gml", "x")
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

    def create_character_folder(self, out, mapping):
        # 1. Have it create a dict of rivals animations with the right name and folder, replacing the one already used
        # 2. final_character.unparse_spritesheets()

        mapped_anims = {}
        f = open(mapping.strip(), encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if "=" in line:
                line = line.replace(" ", "").replace("\n", "")
                rivals_anim_name = line.split("=")[0]
                anim_number = line.split("=")[1]
                image_filename = glob.glob(out + "/raw_output/" + anim_number + "_strip*.png")
                if image_filename:
                    image_filename = image_filename[0]
                    frame_count = image_filename.split("_strip")[1].split(".")[0]
                    output_filename = out + "/character/sprites/" + rivals_anim_name + "_strip" + frame_count + ".png"
                    shutil.copy2(image_filename, output_filename)
                hurt_filename = glob.glob(out + "/raw_output/" + anim_number + "_hurt_strip*.png")
                if hurt_filename:
                    hurt_filename = hurt_filename[0]
                    frame_count = hurt_filename.split("_strip")[1].split(".")[0]
                    output_filename = out + "/character/sprites/" + rivals_anim_name + "_hurt_strip" + frame_count + ".png"
                    shutil.copy2(hurt_filename, output_filename)
                attack_script = glob.glob(out + "/raw_output/" + anim_number + ".gml")
                if attack_script:
                    attack_script = attack_script[0]
                    output_filename = out + "/character/scripts/attacks/" + rivals_anim_name + ".gml"
                    shutil.copy2(attack_script, output_filename)
                    with open(output_filename, 'r') as file:
                        filedata = file.read()
                        filedata = filedata.replace(anim_number, rivals_anim_name)
                        filedata = filedata.replace("_" + rivals_anim_name, "_" + rivals_anim_name.upper())
                    with open(output_filename, 'w') as file:
                        file.write(filedata)

    def create_mapped_character(self, out):
        if options.button_mapping_file:
           input_mapping = options.parse_button_mapping()

           # Create the folder structure
           os.mkdir(out + "/character")
           print("Input mapping given, the converted character will be saved to '" + options.output_folder + "/character'")
           self.create_character_folders(out + "/character")

           for key, value in input_mapping.items():
                in_name = str(value[0])
                image_filename = glob.glob(out + "/raw_output/" + in_name + "_strip*.png")
                hurt_filename = glob.glob(out + "/raw_output/" + in_name + "_hurt_strip*.png")
                attack_script = glob.glob(out + "/raw_output/" + in_name + ".gml")

                if image_filename:
                    image_filename = image_filename[0]
                    frame_count = image_filename.split("_strip")[1].split(".")[0]
                    output_filename = out + "/character/sprites/" + key + "_strip" + frame_count + ".png"
                    shutil.copy2(image_filename, output_filename)

                    if hurt_filename:
                        hurt_filename = hurt_filename[0]
                        output_filename = out + "/character/sprites/" + key + "_hurt_strip" + frame_count + ".png"
                        shutil.copy2(hurt_filename, output_filename)
                        
                    if attack_script:
                        attack_script = attack_script[0]
                        output_filename = out + "/character/scripts/attacks/" + key + ".gml"
                        shutil.copy2(attack_script, output_filename)
                        with open(output_filename, 'r') as file:
                            filedata = file.read()
                            filedata = filedata.replace(in_name, key)
                            filedata = filedata.replace("_" + key, "_" + key.upper())
                        with open(output_filename, 'w') as file:
                            file.write(filedata)

    def create_character_folders(self, out):
        os.mkdir(out + "/scripts")
        os.mkdir(out + "/scripts/attacks")
        os.mkdir(out + "/sounds")
        os.mkdir(out + "/sprites")

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
