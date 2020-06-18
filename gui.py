import mugenrivals
import tkinter as tk
import tkinter.filedialog
import glob
from PIL import ImageTk, Image
import os, shutil

move_names = ['idle', 'walk', 'walkturn', 'jump', 'jumpstart', 'walljump', 'doublejump', 'airdodge', 'airdodge_forward', 'airdodge_back', 'airdodge_up', 'airdodge_upforward', 'airdodge_upback', 'airdodge_down', 'airdodge_downforward', 'airdodge_downback', 'dash', 'dashstart', 'dashstop', 'dashturn', 'land', 'landinglag', 'waveland', 'pratfall', 'crouch', 'tech', 'roll_forward', 'roll_backward', 'parry', 'hurt', 'bighurt', 'hurtground', 'bouncehurt', 'spinhurt', 'uphurt', 'downhurt', 'bair', 'dair', 'dattack', 'dspecial', 'dstrong', 'dtilt', 'fair', 'fspecial', 'fstrong', 'ftilt', 'jab', 'nair', 'nspecial', 'taunt', 'uair', 'uspecial', 'ustrong', 'utilt']
attack_names = ['bair', 'dair', 'dattack', 'dspecial', 'dstrong', 'dtilt', 'fair', 'fspecial', 'fstrong', 'ftilt', 'jab', 'nair', 'nspecial', 'taunt', 'uair', 'uspecial', 'ustrong', 'utilt']
#This class I dont think is actually useful at all? I didn't know what i was doing.
class MoveScreen(tk.Frame):
    #This function is the init of the window, it should create all the buttons and menus that are shared by all move screens
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        #todo: there should be a finish button, that finish button should run a function, and that function should do all the writting to file.
    
    #This function runs every time the page is shown to the user (using navigation arrows).
    def show(self):
        self.lift()
    
    #This function inits a variable for the move screen that represents which rivals move its for. This is necessary for writting and saving to files at the end.   
    def set_page_nb(self, nb):
        self.nb = tk.IntVar()
        self.nb.set(nb)

#The main application class for the window  
class Application(tk.Frame):
    #Init function
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.folder_choose()
    
    #Display the first screen where the user selects a folder to use
    def folder_choose(self):
        self.folder_name = tk.StringVar()
        self.dir_box = tk.Entry(self, textvariable=self.folder_name, width=32)
        self.dir_box.grid(column=0,row=0)
        self.char_folder_button = tk.Button(self)
        self.char_folder_button["text"] = "Character Folder"
        self.char_folder_button["command"] = self.get_folder
        self.char_folder_button.grid(column=1,row=0)
        self.folder_name.trace('w', self.check_folder_valid)

        self.convert_btn = tk.Button(self, text="Convert",
                              command=self.setup_move_screen, state="disabled")
        self.convert_btn.grid(column=1,row=1)
        self.grid()

    #Open a folder
    def get_folder(self):
        folder = tk.filedialog.askdirectory()
        self.folder_name.set(folder)
        
    #Runs the mugen conversion on the given folder, and goes to the move assignment screen.
    def setup_move_screen(self):
        self.dir_box.destroy()
        self.char_folder_button.destroy()
        self.convert_btn.destroy()
        root.update()
        self.filename_dict, self.max_width, self.max_height = mugenrivals.main(self.folder_name.get())
        self.character_creation_screen()
        
    #Test the chosen folder to see if it's usable    
    def check_folder_valid(self, n, m, x):
        sff_path = next((path for path in glob.glob(self.folder_name.get() + "/*.sff") 
            if not path.endswith("ending.sff") 
            and not path.endswith("intro.sff")), None)
        air_path = next((path for path in glob.glob(self.folder_name.get() + "/*.air")), None)
        if sff_path and air_path:
            self.convert_btn['state'] = 'normal'
        else:
            self.convert_btn['state'] = 'disabled'
            
    #Draw the move selection screen, where the user can assign animations to each move
    #This is the old version, which shows one frame at a time, some of the code here should be reuse for the hitbox editor eventually.
    def character_creation_screen_old_frame_view(self):
        self.current_page = tk.IntVar()
        self.current_page.set(0)
        self.pages = []
            
        #Move nagivation buttons
        move_button_frame = tk.Frame(self)
        move_button_frame.pack(side="top", fill="x", expand=False)
        self.move_name_label_text = tk.StringVar()
        self.move_name_label_text.set(move_names[self.current_page.get()])
        self.move_name_label = tk.Label(move_button_frame, textvariable = self.move_name_label_text) #todo: make this into a dropdown menu like the image selection
        self.move_name_label.pack(side="top", fill="both", expand=True)
        self.left_page_btn = tk.Button(move_button_frame, text="Previous",
                              command=self.left_page)
        self.right_page_btn = tk.Button(move_button_frame, text="Next",
                              command=self.right_page)
        self.left_page_btn.pack(side='left')
        self.right_page_btn.pack(side='right')
        #Sprite sheet selection buttons
        sprite_button_frame = tk.Frame(self)
        sprite_button_frame.pack(side="top", fill="x", expand=False)
        self.previous_sprite_btn = tk.Button(sprite_button_frame, text="Previous",
                              command=self.previous_sprite)
        self.next_sprite_btn = tk.Button(sprite_button_frame, text="Previous",
                              command=self.next_sprite)
        self.previous_sprite_btn.pack(side='left')
        self.next_sprite_btn.pack(side='right')
        self.previous_sprite_btn['state'] = 'disabled'
        self.selected_sheet = tk.StringVar()
        self.selected_sheet.set("0")
        sheet_list_menu = tk.OptionMenu(sprite_button_frame, self.selected_sheet, *self.filename_dict.keys(), command=self.change_image)
        sheet_list_menu.pack(side="top")
        #Frame preview 
        self.current_frame = tk.IntVar()
        self.current_page.set(0)
        image_frame = tk.Frame(self)
        image_frame.pack(side="right")
        self.canvas = tk.Canvas(image_frame, width = 100, height = 100)
        self.update_sprite()
        #Frame selection
        self.previous_frame_btn = tk.Button(image_frame, text="Previous",
                              command=self.previous_frame)
        self.previous_frame_btn.pack(side='left')
        self.next_frame_btn = tk.Button(image_frame, text="Next",
                              command=self.next_frame)
        self.next_frame_btn.pack(side='right')
        self.previous_frame_btn['state'] = 'disabled'
        self.frame_nb_label = tk.Label(image_frame, textvariable = self.current_frame)
        self.frame_nb_label.pack(side='bottom')
        #Hitbox buttons
        
        self.pages[0].show()
        
    #In frame view: Display a new image whenever a new sheet is selected and return to frame 0
    def change_image(self, sheet_value):
        filename = self.filename_dict[int(self.selected_sheet.get())]
        self.frame_nb = int(filename.split(".")[0].split("strip")[1])
        self.current_frame.set(0)
        self.next_frame_btn['state'] = 'normal'
        if self.frame_nb <= 1:
            self.next_frame_btn['state'] = 'disabled'
        self.update_sprite()
    
    #In frame view: Display a new frame, whenever a new sheet or frame has to be shown
    def update_sprite(self):
        filename = self.filename_dict[int(self.selected_sheet.get())]
        self.frame_nb = int(filename.split(".")[0].split("strip")[1])
        self.img = Image.open(self.folder_name.get() + "_output/" + filename)
        img_width = self.img.size[0] // self.frame_nb
        self.img2 = self.img.crop([img_width*self.current_frame.get(),0,img_width*self.current_frame.get()+img_width,self.img.size[1]]) #here edit based on frame count
        self.photoimg = ImageTk.PhotoImage(self.img2)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photoimg)
        self.canvas.pack(side='top')
        
    #In frame view: Display the previous sheet
    def previous_sprite(self):
        current_index = list(self.filename_dict.keys()).index(int(self.selected_sheet.get()))
        self.selected_sheet.set(list(self.filename_dict.keys())[current_index - 1])
        if current_index - 1 == 0:
            self.previous_sprite_btn['state'] = 'disabled'
        self.next_sprite_btn['state'] = 'normal'
        self.update_sprite()
     
    #In frame view: Display the next sheet
    def next_sprite(self):
        current_index = list(self.filename_dict.keys()).index(int(self.selected_sheet.get()))
        self.selected_sheet.set(list(self.filename_dict.keys())[current_index + 1])
        if current_index + 1 == len(self.filename_dict.keys()) - 1:
            self.next_sprite_btn['state'] = 'disabled'
        self.previous_sprite_btn['state'] = 'normal'
        self.update_sprite()
    
    #In frame view: Display the previous frame of the current sheet
    def previous_frame(self):
        self.current_frame.set(self.current_frame.get()-1)
        if self.current_frame.get() == 0:
            self.previous_frame_btn['state'] = 'disabled'
        self.next_frame_btn['state'] = 'normal'
        self.update_sprite()
    
    #In frame view: Display the next frame of the current sheet
    def next_frame(self):
        self.current_frame.set(self.current_frame.get()+1)
        if self.current_frame.get() == self.frame_nb -1:
            self.next_frame_btn['state'] = 'disabled'
        self.previous_frame_btn['state'] = 'normal'
        self.update_sprite()
          
    #Draw the move selection screen, where the user can assign animations to each move
    def character_creation_screen(self):
        self.used_sheets = {'idle': 0, 'walk': 0, 'walkturn': 0, 'jump': 0, 'jumpstart': 0, 'walljump': 0, 'doublejump': 0, 
                                         'airdodge': 0, 'airdodge_forward': 0, 'airdodge_back': 0, 'airdodge_up': 0, 
                                         'airdodge_upforward': 0, 'airdodge_upback': 0, 'airdodge_down': 0, 'airdodge_downforward': 0, 'airdodge_downback': 0, 
                                         'dash': 0, 'dashstart': 0, 'dashstop': 0, 'dashturn': 0, 'land': 0, 'landinglag': 0, 'waveland': 0, 'pratfall': 0, 'crouch': 0, 
                                         'tech': 0, 'roll_forward': 0, 'roll_backward': 0, 'parry': 0, 
                                         'hurt': 0, 'bighurt': 0, 'hurtground': 0, 'bouncehurt': 0, 'spinhurt': 0, 'uphurt': 0, 'downhurt': 0, 
                                         'bair': 0, 'dair': 0, 'dattack': 0, 'dspecial': 0, 'dstrong': 0, 'dtilt': 0, 'fair': 0, 'fspecial': 0, 'fstrong': 0, 'ftilt': 0, 
                                         'jab': 0, 'nair': 0, 'nspecial': 0, 'taunt': 0, 'uair': 0, 'uspecial': 0, 'ustrong': 0, 'utilt': 0}

        self.current_page = tk.IntVar()
        self.current_page.set(0)
        #Move nagivation buttons
        move_button_frame = tk.Frame(self)
        move_button_frame.pack(side="top", fill="both", expand=False)
        self.move_name_label_text = tk.StringVar()
        self.move_name_label_text.set(move_names[self.current_page.get()])
        self.move_name_label = tk.Label(move_button_frame, textvariable = self.move_name_label_text) #todo: make this into a dropdown menu like the image selection
        self.move_name_label.pack()
        self.left_page_btn = tk.Button(move_button_frame, text="Previous Animation",
                              command=self.left_page)
        self.left_page_btn['state'] = 'disabled'
        self.right_page_btn = tk.Button(move_button_frame, text="Next Animation",
                              command=self.right_page)
        self.left_page_btn.pack(side='left')
        self.right_page_btn.pack(side='right')
        #Sheet preview
        image_frame = tk.Frame(self)
        image_frame.pack(side="top", fill="x", expand=False)
        self.canvas = tk.Canvas(image_frame, width=self.max_width, height=self.max_height)
        self.selected_sheet = tk.StringVar()
        self.selected_sheet.set("0")
        self.update_sheet()
        #Sprite sheet selection buttons
        sprite_button_frame = tk.Frame(image_frame)
        sprite_button_frame.pack(side="top", fill="x", expand=True)
        self.previous_sprite_btn = tk.Button(sprite_button_frame, text="Previous",
                              command=self.previous_sheet)
        self.next_sprite_btn = tk.Button(sprite_button_frame, text="Next",
                              command=self.next_sheet)
        self.previous_sprite_btn.pack(side='left', fill='x', expand=True)
        self.next_sprite_btn.pack(side='right', fill='x', expand=True)
        self.previous_sprite_btn['state'] = 'disabled'
        sheet_list_menu = tk.OptionMenu(sprite_button_frame, self.selected_sheet, *self.filename_dict.keys(), command=self.update_sheet)
        sheet_list_menu.pack(side="bottom", fill='x', expand=True)
        #Finish Button
        finish_frame = tk.Frame(self)
        finish_frame.pack(side="bottom")
        self.finish_btn = tk.Button(finish_frame, text="Finish",
                              command=self.finish)
        self.finish_btn.pack()
        

    #Move to the previous RoA move screen
    def left_page(self):
        self.current_page.set(self.current_page.get()-1)
        if self.current_page.get() == 0:
            self.left_page_btn['state'] = 'disabled'
        self.right_page_btn['state'] = 'normal'
        self.update_page()
         
    #Move to the next RoA move screen
    def right_page(self):
        self.current_page.set(self.current_page.get()+1)
        if self.current_page.get() == len(move_names)-1:
            self.right_page_btn['state'] = 'disabled'
        self.left_page_btn['state'] = 'normal'
        self.update_page()
        
    def update_page(self):
        self.move_name_label_text.set(move_names[self.current_page.get()])
        self.selected_sheet.set(str(self.used_sheets[move_names[self.current_page.get()]]))
        self.update_sheet()
        
        
    #In sheet view: Display a new sprites sheet
    def update_sheet(self, _=None):
        self.used_sheets[move_names[self.current_page.get()]] = int(self.selected_sheet.get())
        filename = self.filename_dict[int(self.selected_sheet.get())]
        self.img = Image.open(self.folder_name.get() + "_output/" + filename)
        self.photoimg = ImageTk.PhotoImage(self.img)
        #self.canvas.config(width=self.img.size[0], height=self.img.size[1])
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photoimg)
        self.canvas.pack(side='top', fill="x", expand=True)
        
    #In sheet view: Display the previous sheet
    def previous_sheet(self):
        current_index = list(self.filename_dict.keys()).index(int(self.selected_sheet.get()))
        self.selected_sheet.set(list(self.filename_dict.keys())[current_index - 1])
        if current_index - 1 == 0:
            self.previous_sprite_btn['state'] = 'disabled'
        self.next_sprite_btn['state'] = 'normal'
        self.update_sheet()

    #In sheet view: Display the next sheet  
    def next_sheet(self):
        current_index = list(self.filename_dict.keys()).index(int(self.selected_sheet.get()))
        self.selected_sheet.set(list(self.filename_dict.keys())[current_index + 1])
        if current_index + 1 == len(self.filename_dict.keys()) - 1:
            self.next_sprite_btn['state'] = 'disabled'
        self.previous_sprite_btn['state'] = 'normal'
        self.update_sheet()
        
    def finish(self):
        #Create the finalised folder scructure
        character_name = self.folder_name.get().split("/")[-1].split("_output")[0]
        if not os.path.exists(self.folder_name.get() + "_output/" + character_name):
            os.makedirs(self.folder_name.get() + "_output/" + character_name)
        if not os.path.exists(self.folder_name.get() + "_output/" + character_name + "/sprites"):
            os.makedirs(self.folder_name.get() + "_output/" + character_name + "/sprites")
        if not os.path.exists(self.folder_name.get() + "_output/" + character_name + "/scripts"):
            os.makedirs(self.folder_name.get() + "_output/" + character_name + "/scripts")
        if not os.path.exists(self.folder_name.get() + "_output/" + character_name + "/scripts/attacks"):
            os.makedirs(self.folder_name.get() + "_output/" + character_name + "/scripts/attacks")
        #Move the necessary files to the new folders
        for key, value in self.used_sheets.items():
            if key in attack_names:
                shutil.copy(self.folder_name.get() + "_output/" + str(value) + ".gml", 
                            self.folder_name.get() + "_output/" + character_name + "/scripts/attacks/" + key + ".gml")
            frame_nb = str(int(self.filename_dict[value].split(".")[0].split("strip")[1]))
            shutil.copy(self.folder_name.get() + "_output/" + str(value) + "_strip" + frame_nb + ".png", 
                        self.folder_name.get() + "_output/" + character_name + "/sprites/" + key + "_strip" + frame_nb  + ".png")
            shutil.copy(self.folder_name.get() + "_output/" + str(value) + "_hurt_strip" + frame_nb + ".png", 
                        self.folder_name.get() + "_output/" + character_name + "/sprites/" + key + "_hurt_strip" + frame_nb  + ".png")
        exit()
        
        
        

root = tk.Tk()
app = Application(master=root)
app.pack(side="top", fill="both", expand=True)
root.wm_geometry("500x400")
app.mainloop()

#TODO:
#add success popup before the program closes
#add hitbox display/editing