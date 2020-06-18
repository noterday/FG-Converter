import os, re, subprocess, glob
from PIL import Image


"""
    Parse the outfile.def of a Mugen character
    
    Return a 2D dictionary where the first key 
    is the group id and the second key is the sprite id of a sprite
    The data is a 3 item list of the sprite filename and it's x and y offsets
"""
def parse_outfile(filename):
    f = open(filename, encoding="latin-1")
    lines = f.readlines()
    outfile_sprite_data = {}
    sprite_section = False

    for line in lines:
        line = line.replace(" ", "").rstrip("\n").partition(";")[0]
        if line.startswith("[Sprite]"):
            sprite_section = True
        if re.match("[0-9]+,[0-9]+,working/outfile[0-9]+.png,-*[0-9]+,-*[0-9]+", line) and sprite_section:
            add_line_outfile(line, outfile_sprite_data)
    return outfile_sprite_data


"""
    Add a single line of the outfile to the outfile dict
"""
def add_line_outfile(line, outfile_sprite_data):
    line = line.split(",")
    group_id = int(line[0])
    sprite_id = int(line[1])
    sprite_name = line[2]
    offset_x = int(line[3])
    offset_y = int(line[4])
    if group_id not in outfile_sprite_data.keys():
        outfile_sprite_data[group_id] = {}
    outfile_sprite_data[group_id][sprite_id] = [sprite_name, offset_x, offset_y]


"""
    Parse the char.air file of a Mugen character
    
    Return a dictionary where each key is a mugen action number,
    and the values are a 2d dictionary containing each frame's information
    in a sequence
"""    
def parse_airfile(filename):
    f = open(filename, encoding="latin-1")
    lines = f.readlines()
    
    air_file_data = {}
    hitboxes = {}
    hurtboxes = {}
    
    action_nb = -1
    for line in lines:
        line = line.strip().rstrip("\n").partition(";")[0]
        line = line.replace(" ", "")
        if re.match("[Begin Action [0-9]+]", line):
            action_nb = int(line.lstrip("[Begin Action").rstrip("]"))
            if action_nb not in air_file_data.keys():
                air_file_data[action_nb] = []
        
        if re.match("[0-9]+,[0-9]+,-*[0-9]+,-*[0-9]+,-*[0-9]+,*.*", line):
            add_frame(action_nb, line, air_file_data)
            
        if re.match("Clsn2\[.+\]=" , line):
            add_box(hurtboxes, action_nb, len(air_file_data[action_nb]), line.partition("=")[2])
        elif re.match("Clsn1\[.+\]=" , line):
            add_box(hitboxes, action_nb, len(air_file_data[action_nb]), line.partition("=")[2])

    return air_file_data, hitboxes, hurtboxes

"""
    Parse a line of hitbox information and add it to the given dictionary.
"""
def add_box(box_dict, action_nb, frame_nb, data):
    if action_nb not in box_dict:
        box_dict[action_nb] = []
    if frame_nb == 0:
        frame_nb = -1
    else:
        frame_nb += 1
    data = data.split(",")
    box_dict[action_nb].append((frame_nb, data[0], data[1], data[2], data[3])) #parse data


"""
    Add a line of animation data to the air file data
"""
def add_frame(action_nb, line, air_file_data):
    line = line.split(",")
    group_id = int(line[0])
    sprite_id = int(line[1])
    offset_x = int(line[2])
    offset_y = int(line[3])
    duration = int(line[4])
    flags = ""
    if len(line) == 6:
        flags = line[5]
    air_file_data[action_nb].append([group_id, sprite_id, offset_x, offset_y, duration, flags])


"""
    Create spritesheet for every action of the character using the parsed mugen .sff and .air file
"""    
def build_spritesheet(outfile, action_nb, frames, outfolder, filename_dict):
    if not frames:
        return
    action_sprites = [get_frame(outfile,frame) for frame in frames]
    images = [(Image.open(sprite[0]), sprite[1], sprite[2]) for sprite in action_sprites]
    widths, heights = zip(*(i[0].size for i in images))

    max_width = max(widths)
    max_height = max(heights)

    spritesheet = Image.new('RGBA', (max_width*len(images), max_height), (0,0,0,0))

    x_offset = 0
    for im in images:
        spritesheet.paste(add_alpha(im[0]), (x_offset,max_height-im[0].size[1]), mask=0)
        x_offset += max_width
        
    #make the hurtbox sheet
    alpha = spritesheet.getchannel("A")
    hurtboxsheet = Image.new('RGBA', (max_width*len(images), max_height), (0,255,0,255))
    hurtboxsheet.putalpha(alpha)
    filename = str(action_nb) + "_strip" + str(len(images)) +'.png'
    filename_dict[action_nb] = filename
    spritesheet.save(outfolder + "/" + filename)
    hurtboxsheet.save(outfolder + "/" + str(action_nb) + "_hurt_strip" + str(len(images)) +'.png')
    return max_width, max_height


"""
    Get an item from the outfile dictionary
    
    Return outfile000 as the default if either the group or image id don't exist
"""
def get_frame(outfile, frame):
    if frame[0] not in outfile.keys():
        return ("working/outfile000.png", 0, 0)
    if frame[1] not in outfile[frame[0]].keys():
        return ("working/outfile000.png", 0, 0)
    return outfile[frame[0]][frame[1]]


"""
    Modify a given image to make the color of the first pixel transparent
"""
def add_alpha(image):
    image = image.convert("RGBA")
    datas = image.getdata()
    newData = []
    r,g,b,a = image.getpixel((0,0))
    for item in datas:
        if item[0] == r and item[1] == g and item[2] == b:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    image.putdata(newData)
    return image


"""
    Add a new portion to an animation's gml file containing window timing, 
    based on the mugen airfile animation timing
    
    Returns a list of int representing the starting frame of each window
"""
def create_gml_windows_section(gml, frames):
    gml.write("//Windows Timing\n")
    gml.write('set_attack_value(AT_ATTACK, AG_SPRITE, sprite_get("attack"));\n')
    gml.write('set_attack_value(AT_ATTACK, AG_HURTBOX_SPRITE, sprite_get("attack_hurt"));\n')
    windows = []
    timings = [frame[4] for frame in frames]
    timings.append(-2)
    gml.write("set_attack_value(AT_ATTACK, AG_NUM_WINDOWS, " + str(len(frames))+ ");\n\n")
    for i in range(0, len(frames)):
        gml.write("set_window_value(AT_ATTACK, " + str(i+1) + ", AG_WINDOW_LENGTH," + str(frames[i][4]) + ");\n")
        gml.write("set_window_value(AT_ATTACK, " + str(i+1) + ", AG_WINDOW_ANIM_FRAMES,1" + ");\n")
        gml.write("set_window_value(AT_ATTACK, " + str(i+1) + ", AG_WINDOW_ANIM_FRAME_START," + str(i) + ");\n")
        gml.write("\n")
        
    
"""
"""    
def create_gml_box_section(gml, boxes):
    gml.write("//Hitboxes\n")
    gml.write("set_num_hitboxes(AT_ATTACK, " + str(len(boxes)) + ");\n")
    for i in range(0, len(boxes)):
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_HITBOX_TYPE, 1);\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_LIFETIME, 1);\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_SHAPE, 1);\n")
        box = boxes[i]
        starting_frame = box[0]
        sx = int(box[1])
        sy = int(box[2])
        ex = int(box[3])
        ey = int(box[4])
        width = abs(sx - ex)
        height = abs(sy - ey)
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_HITBOX_X, " + str(sx) + ");\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_HITBOX_Y, " + str(sy) + ");\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_WIDTH, " + str(width) + ");\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_HEIGHT, " + str(height) + ");\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_WINDOW, " + str(starting_frame) + ");\n")
        gml.write("set_hitbox_value(AT_ATTACK, " + str(i+1) + ", HG_WINDOW_CREATION_FRAME, 0);\n")
        gml.write("\n")
            


def main():
    #ask user for a file
    folder = input("Path to mugen folder: ")
    outfolder = folder + "_output"
    if not os.path.exists(folder):
        input("The folder does not exist.")
        return
        
    #process the mugen files to get the sprites and outfile-sff    
    sff_path = next(path for path in glob.glob(folder + "/*.sff") 
                    if not path.endswith("ending.sff") 
                    and not path.endswith("intro.sff"))
    air_path = glob.glob(folder + "/*.air")[0]
    if not os.path.exists("working"):
        os.makedirs("working")
    subprocess.run(["mugen/sff2png.exe", sff_path, "working/outfile", "-f 0"])
    outfile_path = "working/outfile-sff.def" 
    if not os.path.exists(folder + "_output"):
        os.makedirs(folder + "_output")
        
    #parse the mugen files to get all the data
    outfile = parse_outfile(outfile_path)
    airfile, hitboxes, hurtboxes = parse_airfile(air_path)
    
    #create the rival files from the mugen data
    #todo: rework this entire section
    for action_nb, frames in airfile.items():
        build_spritesheet(outfile, action_nb, frames, outfolder)
        gml = open(outfolder + "/" + str(action_nb) + ".gml", "w+")
        gml.write("//Section created by mugenrivals script.\n")
        window_start_frames = create_gml_windows_section(gml, frames)
        if action_nb in hitboxes:
            create_gml_box_section(gml, hitboxes[action_nb], window_start_frames)
        gml.close()
    
    
    input("Done!")

def main(folder):
    max_width = 0
    max_height = 0
    #ask user for a file
    outfolder = folder + "_output"
    if not os.path.exists(folder):
        input("The folder does not exist.")
        return
        
    #process the mugen files to get the sprites and outfile-sff    
    sff_path = next(path for path in glob.glob(folder + "/*.sff") 
                    if not path.endswith("ending.sff") 
                    and not path.endswith("intro.sff"))
    air_path = glob.glob(folder + "/*.air")[0]
    if not os.path.exists("working"):
        os.makedirs("working")
    subprocess.run(["mugen/sff2png.exe", sff_path, "working/outfile", "-f 0"])
    outfile_path = "working/outfile-sff.def" 
    if not os.path.exists(folder + "_output"):
        os.makedirs(folder + "_output")
        
    #parse the mugen files to get all the data
    outfile = parse_outfile(outfile_path)
    airfile, hitboxes, hurtboxes = parse_airfile(air_path)
    
    #create the rival files from the mugen data
    filename_dict = {}
    for action_nb, frames in airfile.items():
        width, height = build_spritesheet(outfile, action_nb, frames, outfolder, filename_dict)
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height
        gml = open(outfolder + "/" + str(action_nb) + ".gml", "w+")
        gml.write("//Section created by mugenrivals script.\n")
        create_gml_windows_section(gml, frames)
        if action_nb in hitboxes:
            create_gml_box_section(gml, hitboxes[action_nb])
        gml.close()
    return filename_dict, max_width, max_height