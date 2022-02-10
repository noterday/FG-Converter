import re, os, shutil
from modules.generic_character import GenericCharacter

class RivalsCharacter(GenericCharacter):
    AttackNames = ['jab', 'dattack', 'nspecial', 'fspecial', 'uspecial',
        'dspecial', 'fstrong', 'ustrong', 'dstrong', 'ftilt', 'utilt',
        'dtilt', 'nair', 'fair', 'bair', 'dair', 'uair', 'taunt']

    AnimationNames = ['idle', 'walk', 'walkturn', 'jump', 'jumpstart', 'walljump', 'doublejump',
        'airdodge', 'airdodge_forward', 'airdodge_back', 'airdodge_up', 'airdodge_upforward', 'airdodge_upback', 'airdodge_down', 'airdodge_downforward', 'airdodge_downback',
        'plat', 'dash', 'dashstart', 'dashstop', 'dashturn', 'land', 'landinglag', 'waveland', 'pratfall', 'crouch', 'tech', 'roll_forward', 'roll_backward', 'parry',
        'hurt', 'bighurt', 'hurtground', 'bouncehurt', 'spinhurt', 'uphurt', 'downhurt']

    # Creates the object with empty values
    def __init__(self, base_folder):
        super().__init__(base_folder)
        self.config_ini = {}
        self.init_script = {}
        self.converted_animations = {}
        self.animations = {anim_name : RivalsAnimation(anim_name) for anim_name in RivalsCharacter.AnimationNames}
        self.attacks = {move_name : RivalsAttack(move_name) for move_name in RivalsCharacter.AttackNames}

    # Reads from the mugen character file to create the object
    def parse_folder(self, _output_folder = ""):
        self.parse_config_ini()
        self.parse_load_gml()
        self.parse_init_gml()
        self.parse_attack_scripts()

    # Converts the object's data back into the original files and folder structure
    def unparse_character(self, output_folder):
        self.unparse_config_ini(output_folder)
        self.unparse_load_gml(output_folder)
        self.unparse_init_gml(output_folder)
        self.unparse_attack_scripts(output_folder)
        self.unparse_spritesheets(output_folder)

    # Returns itself if the conversion type is Rivals
    def convert_to_rivals(self, output_folder, input_mapping_file):
        return self

    def parse_config_ini(self):
        f = open(self.base_folder + "/config.ini", encoding="utf-8")
        lines = f.readlines()
        for line in lines:
            if "=" in line:
                line = line.split(";")[0].strip()
                key, value = line.split("=")
                self.config_ini[key] = value

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
                elif anim_name in self.attacks:
                    self.attacks.get(anim_name).offset = (offset_x, offset_y)
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
        for attack_name in RivalsCharacter.AttackNames:
            f = open(self.base_folder + "/scripts/attacks/" + attack_name + ".gml")
            lines = f.readlines()
            for line in lines:
                if line.startswith("set_"):
                    command_type = line.split("(")[0].strip()
                    line = re.search( "\((.*)\)" , line).group(1)
                    values = line.split(",")
                    if command_type == 'set_attack_value':
                        index = values[1].strip()
                        value = values[2].strip()
                        self.attacks.get(attack_name).attack_values[index] = value
                    elif command_type == 'set_window_value':
                        window_number = values[1].strip()
                        index = values[2].strip()
                        value = values[3].strip()
                        if not window_number in self.attacks.get(attack_name).windows:
                            self.attacks.get(attack_name).windows[window_number] = {}
                        self.attacks.get(attack_name).windows[window_number][index] = value
                    elif command_type == 'set_num_hitboxes':
                        value = values[1].strip()
                        self.attacks.get(attack_name).num_hitboxes = value
                    elif command_type == 'set_hitbox_value':
                        hitbox_number = values[1].strip()
                        index = values[2].strip()
                        value = values[3].strip()
                        if not hitbox_number in self.attacks.get(attack_name).hitboxes:
                            self.attacks.get(attack_name).hitboxes[hitbox_number] = {}
                        self.attacks.get(attack_name).hitboxes[hitbox_number][index] = value

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
        #f.write("//This load.gml file was created by mugen2rivals.\n")
        for animation in self.animations.values():
            if animation.offset[0] or animation.offset[1]:
                line = 'sprite_change_offset("' + animation.name + '"' + ", " + str(animation.offset[0]) + ", " + str(animation.offset[1]) + ");\n"
                f.write(line)
        f.write("\n")
        for attack in self.attacks.values():
            line = 'sprite_change_offset("' + attack.name + '"' + ", " + str(attack.offset[0]) + ", " + str(attack.offset[1]) + ");\n"
            f.write(line)
        f.close()

    # Writes a new init.gml file in the output folder based on the character data
    def unparse_init_gml(self, output_folder):
        f = open(output_folder + "/character_files/scripts/init.gml", "x")
        #f.write("//This init.gml file was created by mugen2rivals.\n")
        for name, value in self.init_script.items():
            line = name + ' = ' + value + ';\n'
            f.write(line)
        f.close()

    #Writes new attack .gml scripts to the output /scripts/attacks folder based on character data
    def unparse_attack_scripts(self, output_folder):
        # All converted animations
        for anim_nb, animation in self.converted_animations.items():
            f = open(output_folder + "/converted_actions/" + str(anim_nb) + ".gml", "x")
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
        # Only the chosen attacks from the mapping file
        for attack_name in RivalsCharacter.AttackNames:
            f = open(output_folder + "/character_files/scripts/attacks/" + attack_name + ".gml", "x")
            attack = self.attacks.get(attack_name)
            for key, value in attack.attack_values.items():
                line = ("set_attack_value(AT_" + attack_name.upper() +
                    ", " + key + ", " + value + ");\n")
                f.write(line)
            f.write("\n")
            for nb, window in attack.windows.items():
                for key, value in window.items():
                    line = ("set_window_value(AT_" + attack_name.upper() +
                            ", " + nb + ", " + key + ", " + value + ");\n")
                    f.write(line)
                f.write("\n")
            line = "set_num_hitboxes(AT_" + attack_name.upper() + ", " + attack.num_hitboxes + ");\n"
            f.write(line)
            for nb, hitbox in attack.hitboxes.items():
                for key, value in hitbox.items():
                    line = ("set_hitbox_value(AT_" + attack_name.upper() + ", " + nb + ", " +
                        key + ", " + value + ");\n")
                    f.write(line)
                f.write("\n")
            f.close

    # Copy converted spritesheets to the /sprites/ output folder
    def unparse_spritesheets(self, output_folder):
        for animation_name in RivalsCharacter.AnimationNames:
            animation = self.animations.get(animation_name)
            if animation.filename:
                shutil.copy2(animation.filename, output_folder + "/character_files/sprites/" + animation_name + "_" + animation.filename.split("/")[-1].split("_")[-1])
                shutil.copy2(animation.hurt_filename, output_folder + "/character_files/sprites/" + animation_name + "_hurt_" + animation.hurt_filename.split("/")[-1].split("_")[-1])
        for attack_name in RivalsCharacter.AttackNames:
            attack = self.attacks.get(attack_name)
            if attack.filename:
                shutil.copy2(attack.filename, output_folder + "/character_files/sprites/" + attack_name + "_" + attack.filename.split("/")[-1].split("_")[-1])
                shutil.copy2(attack.hurt_filename, output_folder + "/character_files/sprites/" + attack_name + "_hurt_" + attack.hurt_filename.split("/")[-1].split("_")[-1])


class RivalsAnimation:
    def __init__(self, name):
        self.name = name
        self.offset = (0, 0)
        self.filename = ''


class RivalsAttack:
    def __init__(self, name):
        self.name = name
        self.offset = (0, 0)
        self.filename = ''
        self.hurt_filename = ''
        self.attack_values = {}
        self.windows = {}
        self.num_hitboxes = '0'
        self.hitboxes = {}
