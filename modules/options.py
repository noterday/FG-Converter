import os





# Parses the command line arguments given by the user
def parse_arguments(optlist, args):
    global input_folder, output_folder, button_mapping_file, input_engine, chosen_output
    
    button_mapping_file = None
    # Parsing the options
    for option, value in optlist:
        if option in ['-h', '--help']:
            print_help()
            exit()
        elif option in ['-m', '--mapping']:
            button_mapping_file = value
        elif option in ['-o', '--output']:
            chosen_output = value

    # Parse the argument (should be the input folder)
    if len(args) != 1:
        print_help()
        exit()
    else:
        input_folder = args[0]

    
    # Determine the input type
    input_engine = guess_input_type(input_folder)

    # Determines the output engine
    if not chosen_output:
        chosen_output = prompt_for_output_type()
    chosen_output = chosen_output.replace(" ", "")
    if chosen_output not in ["1", "2"]:
        raise Exception("Error: Invalid output option.")
    
    # Determines the output folder name
    output_folder = "output/" + os.path.basename(input_folder.rstrip('/')) + "_" + input_engine + "_converted"


# Outputs an help message
def print_help():
    print('USAGE: fg-converter [-h][-m <file>][-o <value>] <input>')
    print("")
    print("-h, --help")
    print("     Print this help")
    print("")
    print("-m <file>, --mapping=<file>")
    print("     A text file mapping animation names from the input to the output engine.")
    print("     If given, a structured character folder for the output engine will be generated.")
    print("")
    print("-o <value>, --output=<value>")
    print("     The game engine to convert toward :")
    print("         1. Rivals of Aether")
    print("         2. Mugen (work-in-progress)")
    print("")
    print("<input>")
    print("     The root directory of the character to be converted.")
    print("     For Mugen inputs, the directory must contain a .def file")
    print("     For Rivals inputs, the directory must contain a config.ini file")


# Asks to chose an output engine
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
    raise Exception("Error: Invalid input folder.")