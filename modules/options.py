import os

opt = 'hvm:o:p:'
args = ['help', 'mapping', 'output', 'verbose', 'palette']

# Parses the command line arguments given by the user
def parse_arguments(optlist, args):
    global input_folder, output_folder, button_mapping_file, input_engine, chosen_output, verbose, default_palette
    
    default_palette = 1
    button_mapping_file = None
    chosen_output = None
    verbose = None

    # Parsing the options
    for option, value in optlist:
        if option in ['-h', '--help']:
            print_help()
            exit()
        elif option in ['-m', '--mapping']:
            button_mapping_file = value.lstrip()
        elif option in ['-o', '--output']:
            chosen_output = value
        elif option in ['-v', '--verbose']:
            verbose = True
        elif option in ['-p', '--palette']:
            default_palette = int(value.lstrip())

    # Parse the argument (should be the input folder)
    if len(args) > 1:
        print_help()
        exit()
    elif len(args) == 0:
        input_folder = prompt_for_folder()
    else:
        input_folder = args[0]

    # Check if given palette is valid
    if not default_palette > 0:
        raise Exception("The given default palette index is invalid. Must be an integer above 0.")
    
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
    print('USAGE: fg-converter [-h][-v][-p][-m <file>][-o <index>] <input>')
    print("")
    print("-h, --help")
    print("     Print this help")
    print("")
    print("-v, --verbose")
    print("     Display additional progress and error information.")
    print("")
    print("-p <index> --palette=<index>")
    print("     The default palette index to use for sprites in the input.")
    print("")
    print("-m <file>, --mapping=<file>")
    print("     A text file mapping animation names from the input to the output engine.")
    print("     If given, a structured character folder for the output engine will be generated.")
    print("")
    print("-o <index>, --output=<index>")
    print("     The output game engine :")
    print("         1. Rivals of Aether")
    print("         2. Mugen (work-in-progress)")
    print("")
    print("<input>")
    print("     The root directory of the character to be converted.")
    print("     For Mugen characters, the directory must contain a .def file")
    print("     For Rivals characters, the directory must contain a config.ini file")


# Asks to chose an output engine
def prompt_for_output_type():
    print("Choose an game output type:")
    print("1. Rivals of Aether")
    print("2. Mugen (work-in-progress)")
    print("")
    return input("Enter: ")

def prompt_for_folder():
    return input("Enter the input character data path :")

# Determines the game engine used in the input folder from it's file extensions
def guess_input_type(input_folder):
    if not os.path.isdir(input_folder):
        raise Exception("Error: Input is not a directory.")
    for file in os.listdir(input_folder):
        if file.endswith("config.ini"):
            return "rivals"
        if file.endswith(".def"):
            return "mugen"
    raise Exception("Error: Input folder is not a recognizable character data folder.")

def parse_button_mapping():
    global button_mapping_file
    input_mapping = {}
    
    f = open(button_mapping_file)
    lines = f.readlines()
    for line in lines:
        line = line.split(';')[0].strip().replace(" ", "")
        if '=' in line:
            in_name, out_name = line.split('=')
            out_name = out_name.split(',')
            out_name[0] = int(out_name[0])
            input_mapping[in_name] = out_name
    return input_mapping