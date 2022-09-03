import os, sys, getopt

from modules.mugen_character import MugenCharacter
from modules.rivals_character import RivalsCharacter


# Outputs an help message
def print_help():
    print('USAGE: fg-converter [-h][-m <file>][-o <value>] <input>')
    print("")
    print("-h, --help")
    print("     Print this help")
    print("")
    print("-m <file>, --mapping-file=<file>")
    print("     Use this file to map animations from the input character to animations in the output character")
    print("     If this argument is given, a ready-to-use character directory containing the necessary animations will be generated.")
    print("     If this argument is not given, a raw dump of all converted animations will be generated instead.")
    print("")
    print("-o <value>, --output=<value>")
    print("     The game engine the character will be converted into.")
    print("     Value should be one of the following numbers: ")
    print("         1. Rivals of Aether")
    print("         2. Mugen (work-in-progress)")
    print("")
    print("<input>")
    print("     The path to the root directory of the character to convert.")
    print("     For Mugen characters, the directory must contain a .def file")
    print("     For Rivals characters, the directory must contain a config.ini file")


def prompt_for_output_type():
    print("Choose an game output type:")
    print("1. Rivals of Aether")
    print("2. Mugen (work-in-progress)")
    print("")
    return input("Enter: ")


# Determines the game engine used in the input folder from it's file extensions
def guess_input_type(input_folder):
    for file in os.listdir(input_folder):
        if file.endswith("config.ini"):
            return "rivals"
        if file.endswith(".def"):
            return "mugen"


# Returns a new character object of the specified type
def create_character_object(input_folder):
    input_type = guess_input_type(input_folder)
    if input_type == "rivals":
        return RivalsCharacter(input_folder)
    elif input_type == "mugen":
        return MugenCharacter(input_folder)
    else:
        raise Exception("Error: No valid object for this type")


if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'hm:o:', ['help', 'mapping', 'output'])
    button_mapping_file = None
    chosen_output = None

    # Parsing the options
    for option, value in optlist:
        if option in ['-h', '--help']:
            print_help()
            exit()
        elif option in ['-m', '--mapping']:
            button_mapping_file = value
        elif option in ['-o', '--output']:
            chosen_output = value

    # Parse the command line argument
    if len(args) != 1:
        print_help()
        exit()
    else:
        input_folder = args[0]

    # Determine the folder structure
    if button_mapping_file:
        print("Converting according to the given button mapping.")
        print("")
    elif button_mapping_file == None:
        print("No button mapping given. Will output a raw animation folder.")
        print("")

    # Determine the output type
    if not chosen_output:
        chosen_output = prompt_for_output_type()
    chosen_output = chosen_output.replace(" ", "")
    if chosen_output not in ["1", "2"]:
        print("Invalid output type!")


    # Basic folder structure
    NAMES = ["rivals", "mugen"]
    if not os.path.exists("converted_characters"):
        os.mkdir("converted_characters")
    output_folder = "converted_characters/" + os.path.basename(input_folder.rstrip('/')) + "_" + NAMES[int(chosen_output)-1] + "_converted"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    else:
        new_filename_counter = 1
        while os.path.exists(output_folder + str(new_filename_counter)):
            new_filename_counter += 1
        output_folder += str(new_filename_counter)
        os.mkdir(output_folder)

    # Conversion
    base_character = create_character_object(input_folder)
    base_character.parse()
    if button_mapping_file:
        if chosen_output == "1":
            base_character.convert_to_rivals_mapped(output_folder, button_mapping_file)
        elif chosen_output == "2":
            base_character.convert_to_mugen_mapped(output_folder, button_mapping_file)
    else:
        if chosen_output == "1":
            base_character.convert_to_rivals_raw(output_folder)
        elif chosen_output == "2":
            base_character.convert_to_mugen_raw(output_folder)