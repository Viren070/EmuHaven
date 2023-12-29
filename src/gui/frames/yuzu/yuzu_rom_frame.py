import os 

import customtkinter

from gui.frames.current_roms_frame import CurrentROMSFrame
from gui.frames.switch_roms_frame import SwitchROMSFrame

class YuzuROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, settings, cache):
        super().__init__(master, height=500, width=700)
        self.master = master
        self.roms = None
        self.settings = settings
        self.cache = cache
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()
        
    def get_game_ids(self):
        user_directory = self.settings.yuzu.user_directory
        game_list_dir = os.path.join(user_directory, "cache", "game_list")
        if not os.path.exists(game_list_dir) or not os.listdir(game_list_dir):
            return []
        game_ids = [] 
        for game_id in os.listdir(game_list_dir):
            if game_id.endswith(".pv.txt"):
                game_ids.append(game_id.replace(".pv.txt", ""))
        return game_ids
    
    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = SwitchROMSFrame(self.tab("My ROMs"), self.settings, self.cache, self.get_game_ids, "yuzu")
        self.current_roms_frame.grid(row=0, column=0, sticky="nsew")
