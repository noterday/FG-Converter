import struct
import array
from PIL import Image

"""
The logic to read from sff1 file is mostly based off sffconverter on github.

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
        self.data = PCXImage.decompressData(self.compressedData, self.width * self.height)

    def decompressData(data, maxLength):
        """Uncompressing PCX Image data as RLE"""
        bytes = array.array('B')
        length = len(data)
        i = 0
        total = 0
        while i < length:
            byte = data[i]
            val = byte
            #val = struct.unpack('<B', byte)[0]
            if (val & 0xC0) == 0xC0:
                # Run Length
                count = val & 0x3F
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


def read_sff(file):
    palettes = [] # unused
    sprites = []
    binary_sff = open(file, "rb")
    signature = binary_sff.read(12)
    version = binary_sff.read(4)
    if not signature == b"ElecbyteSpr\x00":
        raise Exception("Input source is not Elecbyte Sprite File")
    if version == b'\x00\x01\x00\x01':
        palettes, sprites = get_sprites_from_sff1(binary_sff)
    elif version == b'\x00\x00\x00\x02':
        raise  Exception("SFFv2 not yet supported.")
    elif version == b'\x00\x01\x00\x02':
        raise  Exception("SFFv2.1 not yet supported.")
    else:
        raise  Exception("SFF version is not recognized")
    return sprites


def get_sprites_from_sff1(fp):
    # Getting the header information
    palettes = []
    sprites = []
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
        sprites.append(sprite)
        offset = nextOffset
    return palettes, sprites


def create_image(palette_file, sprite):
    act_file = open(palette_file, "rb")
    act_palette = []
    for i in range(256): #  There is no version number written in the file. The file is 768 or 772 bytes long and contains 256 RGB colors. The first color in the table is index zero. There are three bytes per color in the order red, green, blue. If the file is 772 bytes long there are 4 additional bytes remaining. Two bytes for the number of colors to use. Two bytes for the color index with the transparency color to use. If loaded into the Colors palette, the colors will be installed in the color swatch list as RGB colors.
        r = struct.unpack('<B', act_file.read(1))[0]
        g = struct.unpack('<B', act_file.read(1))[0]
        b = struct.unpack('<B', act_file.read(1))[0]
        act_palette = [r, g, b] + act_palette
    try:
        image = Image.frombytes('L', (sprite.width, sprite.height), sprite.data)
        image.putpalette(act_palette, "RGB")
        return image
    except:
        return Image.new('RGB', (sprite.width, sprite.height))


# DEBUG TESTS
if __name__ == "__main__":
    PALETTE_NB_INPUT = "/storage/Dev Works/FG-Conversions/useful files/Mugen Characters/kfm2/kfm.act"
    PAL_2 = "/storage/Dev Works/FG-Conversions/useful files/Mugen Characters/sf3_ryu/act/ryu01.act"
    TEST_INPUT2 = "/storage/Dev Works/FG-Conversions/useful files/Mugen Characters/kfm2/kfm.sff" # IS WinMUGEN
    TEST_INPUT3 = "/storage/Dev Works/FG-Conversions/useful files/Mugen Characters/Akaakiha_AA/Akaakiha_AA/Akaakiha_AA.sff"
    TEST_INPUT4 = "/storage/Dev Works/FG-Conversions/useful files/Mugen Characters/sf3_ryu/sf3_ryu.sff"
    act_file = open(PALETTE_NB_INPUT, "rb")
    act_palette = []
    for i in range(256): #  There is no version number written in the file. The file is 768 or 772 bytes long and contains 256 RGB colors. The first color in the table is index zero. There are three bytes per color in the order red, green, blue. If the file is 772 bytes long there are 4 additional bytes remaining. Two bytes for the number of colors to use. Two bytes for the color index with the transparency color to use. If loaded into the Colors palette, the colors will be installed in the color swatch list as RGB colors.
        r = struct.unpack('<B', act_file.read(1))[0]
        g = struct.unpack('<B', act_file.read(1))[0]
        b = struct.unpack('<B', act_file.read(1))[0]
        act_palette = [r, g, b] + act_palette

    sprites = read_sff(TEST_INPUT2)
    checked_sprite = sprites[3]
    image = Image.frombytes('L', (checked_sprite.width, checked_sprite.height), checked_sprite.data)
    image.putpalette(act_palette, "RGB")
    image.save('image_test_sff.png')


    act_file = open(PAL_2, "rb")
    act_palette = []
    for i in range(256): #  There is no version number written in the file. The file is 768 or 772 bytes long and contains 256 RGB colors. The first color in the table is index zero. There are three bytes per color in the order red, green, blue. If the file is 772 bytes long there are 4 additional bytes remaining. Two bytes for the number of colors to use. Two bytes for the color index with the transparency color to use. If loaded into the Colors palette, the colors will be installed in the color swatch list as RGB colors.
        r = struct.unpack('<B', act_file.read(1))[0]
        g = struct.unpack('<B', act_file.read(1))[0]
        b = struct.unpack('<B', act_file.read(1))[0]
        act_palette = [r, g, b] + act_palette


    sprites = read_sff(TEST_INPUT4)
    checked_sprite = sprites[3]
    image = Image.frombytes('L', (checked_sprite.width, checked_sprite.height), checked_sprite.data)
    image.putpalette(act_palette, "RGB")
    image.save('image_test_sff2.png')

#pal1    = kfm6.act  ;Palettes (can have up to 12)
#pal2    = kfm4.act
#pal3    = kfm2.act
#pal4    = kfm5.act
#pal5    = kfm3.act
#pal6    = kfm.act