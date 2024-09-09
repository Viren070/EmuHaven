import os

import customtkinter


class YuzuGamesFrame(customtkinter.CTkTabview):
    def __init__(self, master, settings, cache):
        super().__init__(master, corner_radius=7, anchor="nw")
        self.master = master
        self.roms = None
        self.settings = settings
        self.cache = cache
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()

    def get_game_ids(self):
        blacklist_list = ["0100000000001009", ""]
        user_directory = ""
        return []
        game_list_dir = os.path.join(user_directory, "cache", "game_list")
        if not os.path.exists(game_list_dir) or not os.listdir(game_list_dir):
            return []
        title_ids = []
        for file in os.listdir(game_list_dir):
            title_id = file.replace(".pv.txt", "")
            if file.endswith(".pv.txt") and title_id not in blacklist_list:
                title_ids.append(title_id)
        return title_ids

    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)

        #self.current_roms_frame = SwitchROMSFrame(self.tab("My ROMs"), self.settings, self.cache, self.get_game_ids, "yuzu")
        #self.current_roms_frame.grid(row=0, column=0, sticky="nsew")
