import os, re, subprocess, glob
from PIL import Image




"""
	Parse the outfile.def of a Mugen character
	
	Returns a 2D dictionary where the first key 
	is the group id and the second key is the sprite id of a sprite. 
	The data is a 3 item list of the sprite filename and it's x and y offsets.
"""
def parse_outfile(filename):
	f = open(filename)
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
"""	
def parse_airfile(filename):
	f = open(filename)
	lines = f.readlines()
	air_file_data = {}
	action_nb = -1
	
	for line in lines:
		line = line.strip().rstrip("\n").partition(";")[0]
		if re.match("[Begin Action [0-9]+]", line):
			action_nb = int(line.lstrip("[Begin Action").rstrip("]"))
			
		line = line.replace(" ", "")
		if re.match("[0-9]+,[0-9]+,-*[0-9]+,-*[0-9]+,-*[0-9]+,*.*", line):
			add_frame(action_nb, line, air_file_data)
	return air_file_data

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
	if action_nb not in air_file_data.keys():
		air_file_data[action_nb] = []
	air_file_data[action_nb].append([group_id, sprite_id, offset_x, offset_y, duration, flags])
	
	
"""
	Create spritesheet for every action of the character using the parsed mugen .sff and .air file
"""	
def build_spritesheet(outfile, airfile, outfolder):
	for action_nb, frames in airfile.items():
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
		
		
		spritesheet.save(outfolder + "/" + str(action_nb) + "_strip" + str(len(images)) +'.png')
		hurtboxsheet.save(outfolder + "/" + str(action_nb) + "_hurt_strip" + str(len(images)) +'.png')
			
"""
	Get an item from the outfile dictionary
	
	Returns the value for outfile000 if the group and sprite numbers don't exist to prevent crashes
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
	
	
	
def main():
	folder = input("Enter the Mugen character folder path: ")
	if not os.path.exists(folder):
		print("The folder does not exist.")
		return
		
	sff_path = next(path for path in glob.glob(folder + "/*.sff") 
					if not path.endswith("ending.sff") 
					and not path.endswith("intro.sff"))
	air_path = glob.glob(folder + "/*.air")[0]
		
	if not os.path.exists("working"):
		os.makedirs("working")
	subprocess.run(["mugen/sff2png.exe", sff_path, "working/outfile", "-f 0"])
	
	outfile_path = "working/outfile-sff.def" 
	outfolder = folder + "_output"
	if not os.path.exists(folder + "_output"):
		os.makedirs(folder + "_output")
	
	outfile = parse_outfile(outfile_path)
	airfile = parse_airfile(air_path)
	build_spritesheet(outfile, airfile, outfolder)
	
	
	input("Done!")
	

main()