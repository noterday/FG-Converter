import os, sys, getopt

from modules.mugen_character import MugenCharacter
from modules.rivals_character import RivalsCharacter


# Determines the object to create and the conversions to apply based on command line arguments
def main(input_type, output_type, mapping_file, input_folder):
    output_folder = create_folders(input_folder, input_type, output_type) # Create folders
    input_character_object = create_character_object(input_folder, input_type)
    input_character_object.parse_folder(output_folder) # Parse the input character data
    converted_character_object = input_character_object.convert_to(output_type, output_folder, mapping_file) # Convert to a different type
    converted_character_object.unparse_character(output_folder) # Output the converted character to files


# Determines the game engine used in the input folder from it's file extensions
def guess_input_type(input_folder):
    for file in os.listdir(input_folder):
        if file.endswith(".def"):
            return "mugen"
        if file.endswith("config.ini"):
            return "rivals"


# Creates the basic folder structure for the requested output type
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


# Returns a new character object of the specified type
def create_character_object(input_folder, input_type):
    if input_type == "mugen":
        return MugenCharacter(input_folder)
    elif input_type == "rivals":
        return RivalsCharacter(input_folder)


# Outputs an help message
def print_help():
    print('USAGE: fg-converter [-h][-m] (--to-rivals | --to-mugen) <input-folder>')
    print('Converts user made characters between various fighting game engines.')
    print('')
    print('-h, --help')
    print('     Print this help')
    print('')
    print('-m, --mapping-file=FILE')
    print('     Use this file to automatically map animations to specific inputs')
    print('')
    print('(--to-rivals | --to-mugen)')
    print('     Convert the character to the specified game engine')
    print('')
    print('input-folder')
    print('     The character folder to convert from')
    exit()


# First function called
# Parses the arguments given from command line using getopt
if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'hm:', ['help', 'mapping-file=', 'to-rivals', 'to-mugen'])
    output_type = None
    mapping_file = None
    for option, value in optlist:
        if option in ['-h', '--help']:
            print_help()
        elif option in ['-m', '--mapping-file']:
            mapping_file = value
        elif option == '--to-rivals':
            output_type = 'rivals'
        elif option == '--to-mugen':
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
