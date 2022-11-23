import struct, array
from io import BytesIO
from PIL import Image

import modules.options as options
import modules.sff.SFFv2 as SFFv2


"""
The logic to read from sff1 file is based off sffconverter on github.

https://github.com/chikuchikugonzalez/sffconverter/
"""


class SFFPalette():
    def __init__(self):
        self.group = 0
        self.palette = 0
        self.data = None
        self.colors = 256
        self.reversed = False


class SFFSprite():
    def __init__(self):
        self.group = 0
        self.image = 0
        self.axis = None
        self.width = 0
        self.height = 0
        self.linkedIndex = 0
        self.paletteNumber = 0
        self.data = None
        self.compressedData = None
        self.final_image = None


class PCXImage():
    def __init__(self):
        self.data = None
        self.compresseddData = None
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        self.palette = None
        self.bytesPerLine = 0

    @property
    def width(self):
        """Get Image Width"""
        return self.maxX - self.minX + 1
 
    @property
    def height(self):
        """Get Image Height"""
        return self.maxY - self.minY + 1

    def load(self, data):
        # Read PCX Properties
        dims = struct.unpack('<HHHH', data[4:12])
        self.minX = dims[0]
        self.minY = dims[1]
        self.maxX = dims[2]
        self.maxY = dims[3]
        self.bytesPerLine = struct.unpack('<H', data[66:68])[0]
        dataLength = self.bytesPerLine * self.height
        # Uncompressing
        self.compressedData = data[128:-769]
        self.data = decompress_rle_pcx(self.compressedData, self.width * self.height)


def get_sprites_from_sff1(fp, used_pal):
    # Getting the header information
    palettes = []
    sprites = []
    sprites_dict = {}
    numGroups, numSprites = struct.unpack('<II', fp.read(8))
    subfileOffset, headerSize = struct.unpack('<II', fp.read(8))
    pal_type = fp.read(1)
    # Reading sprites
    offset = subfileOffset
    paletteIndex = 0 # Need a way to get the palette (not understood yet)
    paletteData = b'\x00' * 768
    _index = 0
    for i in range(0, numSprites):
        _index += 1
        fp.seek(offset, 0) # Seek to the Sprite
        sprite = SFFSprite()

        # Read the sprite data
        nextOffset = struct.unpack('<I', fp.read(4))[0]
        dataSize = struct.unpack('<I', fp.read(4))[0]
        axisX, axisY = struct.unpack('<HH', fp.read(4))
        groupNo, imageNo = struct.unpack('<HH', fp.read(4))
        linkedIndex = struct.unpack('<H', fp.read(2))[0]
        sharedMode = struct.unpack('<B', fp.read(1))[0]
        sprite.group = groupNo
        sprite.image = imageNo
        sprite.axis = (axisX, axisY)
        sprite.linkedIndex = linkedIndex
        if linkedIndex == 0:
            fp.seek(offset + 32, 0)
            data = fp.read(dataSize)
            if sharedMode == 0:
                # Reading palette
                palette = SFFPalette()
                palette.group = groupNo
                palette.number = imageNo
                palette.data = data[-768:]
                palettes.append(palette)
                if (groupNo == 9000 and imageNo == 0) or (groupNo == 0 and imageNo == 0):
                    paletteIndex = 0
                else:
                    paletteIndex = len(palettes) - 1
            else:
                data += paletteData
                if (groupNo == 9000 and imageNo == 0) or (groupNo == 0 and imageNo == 0):
                    paletteIndex = 0
            pcxImage = PCXImage()
            pcxImage.load(data)
            sprite.width = pcxImage.width
            sprite.height = pcxImage.height
            sprite.data = pcxImage.data
            sprite.paletteNumber = paletteIndex
        else:
            # Clone
            sprite.width = sprites[linkedIndex].width
            sprite.height = sprites[linkedIndex].height
            sprite.paletteNumber = sprites[linkedIndex].paletteNumber
        sprite.final_image = create_image(used_pal, sprite, i)
        sprites_dict[(str(sprite.group), str(sprite.image))] = sprite
        sprites.append(sprite)
        offset = nextOffset
    return sprites_dict


def get_palettes_from_sff2(file):
    palettes = []
    sffv2_file = SFFv2.SFF2File(file)
    numOfpaletes = SFFv2.get_num_pal(sffv2_file)
    for i in range(numOfpaletes):
        pal = SFFv2.get_pal(sffv2_file, i)
        del pal[3::4]
        palettes.append(pal)
    return palettes


def get_sprites_from_sff2(file, palettes):
    sprites_dict = {}

    sffv2_file = SFFv2.SFF2File(file)
    numOfSprites = SFFv2.get_num_sprites(sffv2_file)

    for i in range(numOfSprites):
        sprite = SFFSprite()
        sprite_node = sffv2_file.GetSpriteNode(i)
        sprite.group = sprite_node.GetGroupNo()
        sprite.image = sprite_node.GetSprNo()
        sprite.width = sprite_node.GetWidth()
        sprite.height = sprite_node.GetHeight()
        sprite.axis = (sprite_node.GetXaxis(), sprite_node.GetYaxis())
        sprite.paletteNumber = sprite_node.GetPalInd()
        sprite_data = SFFv2.get_sprite(sffv2_file, i)
        try:
            if sprite_node.GetFmt() == 1: # Invalid encoding
                raise Exception
            elif sprite_node.GetFmt() in (2, 3, 4): # SFFv2
                sprite.final_image = Image.frombytes(
                    'L', (sprite.width, sprite.height),
                    bytes(sprite_data))
            elif sprite_node.GetFmt() in (10, 11, 12): # Sffv2.1 png files
                sprite_data = sprite_data[4:] # For some reason there is always 4 unecessary bytes before the png
                sprite.final_image = Image.open(BytesIO(bytes(sprite_data[4:])))
            sprite.final_image.putpalette(palettes[sprite.paletteNumber], "RGB")
        except Exception as e:
            if options.verbose:
                print("Unable to extract image " + str(i) + " from .sff file. (" + str(e) + ")")
            sprite.final_image = create_empty_image(sprite)
        sprites_dict[(str(sprite.group), str(sprite.image))] = sprite
    return sprites_dict


def decompress_rle_pcx(data, maxLength):
        """Uncompressing PCX Image data as RLE"""
        bytes = array.array('B')
        length = len(data)
        i = 0
        total = 0
        while i < length:
            byte = data[i]
            val = byte
            if (val & 0xC0) == 0xC0:
                # Run Length
                count = (val & 0x3F)
                byte = data[i + 1]
                i += 1
            else:
                count = 1
            i += 1
            # Append
            for j in range(0, count):
                bytes.append(byte)
                total += 1
                if total >= maxLength:
                    # Over
                    return bytes.tobytes()
        return bytes.tobytes()


def create_image(palette, sprite, i):
    try:
        image = Image.frombytes('L', (sprite.width, sprite.height), sprite.data)
        image.putpalette(palette, "RGB")
        return image
    except Exception as e:
        if options.verbose:
            print("Unable to extract image " + str(i) + " from .sff file. (" + str(e) + ")")
        return create_empty_image(sprite)


def create_empty_image(sprite):
    return Image.new('RGB', (sprite.width, sprite.height))


def read_sff(sprite_file, pal_files):
    binary_sff = open(sprite_file, "rb")
    signature = binary_sff.read(12)
    version = binary_sff.read(4)
    if not signature == b"ElecbyteSpr\x00":
        raise Exception("Input source is not Elecbyte Sprite File")
    if version == b'\x00\x01\x00\x01':
        palettes = get_palettes_from_pal_files(pal_files)
        sprites = get_sprites_from_sff1(binary_sff, palettes[options.default_palette-1])
    elif version == b'\x00\x00\x00\x02':
        palettes = get_palettes_from_sff2(sprite_file)
        sprites = get_sprites_from_sff2(sprite_file, palettes)
    elif version == b'\x00\x01\x00\x02':
        palettes = get_palettes_from_sff2(sprite_file)
        sprites = get_sprites_from_sff2(sprite_file, palettes)
    else:
        raise Exception("SFF version is not recognized")
    return sprites, palettes


def get_palettes_from_pal_files(pal_files):
    palettes = []
    for file in pal_files:
        act_file = open(file, "rb")
        act_palette = []
        for i in range(256):
            r = struct.unpack('<B', act_file.read(1))[0]
            g = struct.unpack('<B', act_file.read(1))[0]
            b = struct.unpack('<B', act_file.read(1))[0]
            act_palette = [r, g, b] + act_palette
        palettes.append(act_palette)
    return palettes