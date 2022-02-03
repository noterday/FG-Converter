import os

# An abstract class for character data.


class GenericCharacter:
    # All character take a folder as an argument, the folder they will be created from or into
    def __init__(self, base_folder):
        self.base_folder = base_folder

    # Abstract. Parses the folder to fetch the engine specific character data
    def parse_folder(self, output_folder):
        pass

    # Abstract. Recreates the files and folder using the saved data
    def unparse_character(self, folder_name):
        pass

    # Abstract. Creates a MugenCharacter object using this object's data
    def convert_to_mugen(self):
        pass

    # Abstract. Creates a RivalsCharacter object using this object's data
    def convert_to_rivals(self):
        pass

    # Determines the conversion function to use and calls it
    def convert_to(self, type, output_folder, input_mapping_file):
        # Calls the appropriate convertor
        if type == "mugen":
            return self.convert_to_mugen(output_folder, input_mapping_file)
        elif type == "rivals":
            return self.convert_to_rivals(output_folder, input_mapping_file)
