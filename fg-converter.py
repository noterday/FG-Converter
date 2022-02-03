import os, sys, getopt

from modules.mugen_character import MugenCharacter
from modules.rivals_character import RivalsCharacter


# Fake argument sets to use as tests for this script
M_TO_R = ["/storage/GameDev/rivals-redo/useful files/mugen characters/kfm2", "mugen", "rivals", "/storage/GameDev/rivals-redo/script/m2r_button_mapping_example.ini"]
R_TO_M = ["/storage/GameDev/rivals-redo/useful files/roa characters/Sandbert", "rivals", "mugen", ""]
R_TO_R = ["/storage/GameDev/rivals-redo/useful files/roa characters/Sandbert", "rivals", "rivals", ""]

short_options = ['']

# Determines the object to create and the conversions to apply based on command line arguments
# For temporary testing purposes, the arguments are written out as global variables at the top of this file
def main(input_type, output_type, mapping_file, input_folder):
    # Create the output folders
    output_folder = create_folders(input_folder, input_type, output_type)
    # Parse, convert and output the character
    input_character_object = create_character_object(input_folder, input_type)
    input_character_object.parse_folder(output_folder)
    converted_character_object = input_character_object.convert_to(output_type, output_folder, mapping_file)
    converted_character_object.unparse_character(output_folder)


def guess_input_type(input_folder):
    for file in os.listdir(input_folder):
        if file.endswith(".def"):
            return "mugen"
        if file.endswith("config.ini"):
            return "rivals"


def create_folders(input_folder, input_type, output_type):
    # Base Folders
    if not os.path.exists("conversion_output"):
        os.mkdir("conversion_output")
    print(input_folder, os.path.basename(input_folder.rstrip('/')))
    output_folder = "conversion_output/" + os.path.basename(input_folder.rstrip('/')) + "_" + output_type
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    else:
        new_filename_counter = 1
        while os.path.exists(output_folder + str(new_filename_counter)):
            new_filename_counter += 1
        output_folder += str(new_filename_counter)
        os.mkdir(output_folder)
    # Game Specific Input folders
    if input_type == "mugen":
        os.mkdir(output_folder + "/converted_actions")
        os.mkdir(output_folder + "/converted_actions/extracted_sprites")
    # Game Specific Output folders
    if output_type == "rivals":
        os.mkdir(output_folder + "/character_files")
        os.mkdir(output_folder + "/character_files/scripts")
        os.mkdir(output_folder + "/character_files/scripts/attacks")
        os.mkdir(output_folder + "/character_files/sprites")
    return output_folder

def create_character_object(input_folder, input_type):
    if input_type == "mugen":
        return MugenCharacter(input_folder)
    elif input_type == "rivals":
        return RivalsCharacter(input_folder)

def print_help():
    print('USAGE: fg-converter [-h][-m] (--output-rivals | --output-mugen) <input-folder>')
    print('Converts user made characters between various fighting game engines.')
    print('')
    print('-h, --help')
    print('     Print this help')
    print('')
    print('-m, --mapping-file=FILE')
    print('     Use this file to automatically map animations to specific inputs')
    print('')
    print('(--output-rivals | --output-mugen)')
    print('     Convert the character to the specified game engine')
    print('')
    print('input-folder')
    print('     The character folder to convert from')
    exit()


if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'hm:', ['help', 'mapping-file=', 'output-rivals', 'output-mugen'])
    output_type = None
    mapping_file = None
    for option, value in optlist:
        if option in ['-h', '--help']:
            print_help()
        elif option in ['-m', '--mapping-file']:
            mapping_file = value
        elif option == '--output-rivals':
            output_type = 'rivals'
        elif option == '--output-mugen':
            output_type = 'mugen'
    if len(args) != 1 or not output_type:
        print_help()
    else:
        input_folder = args[0]
    input_type = guess_input_type(input_folder)
    if input_type == output_type:
        print("Input and Output types cannot be the same.")
        exit()
    main(input_type, output_type, mapping_file, input_folder)
