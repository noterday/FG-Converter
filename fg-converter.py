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
        return RivalsCharacter()
    elif input_type == "mugen":
        return MugenCharacter()
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

    # Determine the output type
    if not chosen_output:
        chosen_output = prompt_for_output_type()
    chosen_output = chosen_output.replace(" ", "")
    if chosen_output not in ["1", "2"]:
        print("Invalid output type!")

    # Basic folder structure
    NAMES = ["rivals", "mugen"]
    if not os.path.exists("output"):
        os.mkdir("output")
    output_folder = "output/" + os.path.basename(input_folder.rstrip('/')) + "_" + NAMES[int(chosen_output)-1] + "_out"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    else:
        new_filename_counter = 1
        while os.path.exists(output_folder + str(new_filename_counter)):
            new_filename_counter += 1
        output_folder += str(new_filename_counter)
        os.mkdir(output_folder)

    # Display the folder structure
    print("Saving the converted files to '" + output_folder + "/raw_output'")
    if button_mapping_file:
        print("Input mapping given, the converted character will be saved to '" + output_folder + "/character'")
    print("")

    # Conversion
    character = create_character_object(input_folder)
    character.parse(input_folder)
    if chosen_output == "1":
        output_character = character.convert_to_rivals(output_folder)
    elif chosen_output == "2":
        output_character = character.convert_to_mugen(output_folder)
    if button_mapping_file:
        output_character.create_character_folder(output_folder, button_mapping_file)