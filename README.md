# FG-Converter
A conversion script between various fighting game engine character formats, to help speed up character creation work. Currently only supports conversions from Mugen to Rivals of Aether. Converts all spritesheets and animation/hitbox data between games.

###### Conversion into Rivals of Aether
![alt text](https://i.imgur.com/O2XegT7.png)

A spritesheet, hurt spritesheet and .gml script will be saved for each animation in the `converted_actions` folder. If a button mapping file was given as argument, these files will be placed in the `character_files` folder with the appropriate names. Copy the `character_files` folder to your workshop folder and continue work on it from there.

![alt text](https://i.imgur.com/uqQEjjS.png)
  
## How to use
Install Python 3 and [Pillow](https://github.com/python-pillow/Pillow) through Pip.

```
python3 fg-converter.py [-h][-m <file>] (--to-rivals | --to-mugen) <input-folder>

-h, --help
     Print this help

-m <file>, --mapping-file=<file>
     Use this file to automatically map animations to specific inputs

(--to-rivals | --to-mugen)
     Convert the character to the specified game engine

<input-folder>
    The folder containing the character files to convert.
    For Mugen characters, this is the folder that contains the .def file.
```

Reference the 'button_mapping.ini' file for an example of button mapping for a Rivals > Mugen conversion.

Input references: 
[Mugen Action Numbers](http://www.elecbyte.com/mugendocs-11b1/air.html#character-reserved-action-numbers), [Rivals of Aether Animation Names](https://rivalsofaether.com/animation-names/).

## TODO
- [ ] Better handling of Mugen .sff file + handling of Mugen color palettes
- [ ] Conversion of sound effects
- [ ] Add reverse conversion (from Rivals to Mugen)
- [ ] Support for other games (Fraymaker on release or anything else that is requested)
