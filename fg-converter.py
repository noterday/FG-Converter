import os, sys, getopt

import modules.options as options
from modules.mugen_character import MugenCharacter
from modules.rivals_character import RivalsCharacter


if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'hvm:o:', ['help', 'mapping', 'output', 'verbose'])
    options.parse_arguments(optlist, args)

    # Create the basic folder structure
    if not os.path.exists("output"):
        os.mkdir("output")
    if os.path.exists(options.output_folder):
        counter = 1
        while os.path.exists(options.output_folder + str(counter)):
            counter += 1
        options.output_folder += str(counter)
    os.mkdir(options.output_folder)


    # Create the input character object
    if options.input_engine == "rivals":
        character = RivalsCharacter()
    elif options.input_engine == "mugen":
        character =  MugenCharacter()

    # Parse and convert the character
    character.parse()
    if options.chosen_output == "1":
        output_character = character.convert_to_rivals()
    elif options.chosen_output == "2":
        output_character = character.convert_to_mugen()