import os

import customtkinter

from gui.frames.switch_roms_frame import SwitchROMSFrame
from pathlib import Path

class RyujinxROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, settings, cache):
        super().__init__(master, height=500, width=700)
        self.master = master
        self.roms = None
        self.cache = cache
        self.settings = settings
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()

    def get_title_ids(self):
        blacklist_list = ["0100000000001009", ""]
        if self.settings.ryujinx.portable_mode:
            user_directory = self.settings.ryujinx.install_directory / "portable"
        else:
            user_directory = Path(os.getenv("APPDATA")) / "ryujinx"
        title_id_dir = os.path.join(user_directory, "games")
        if not os.path.exists(title_id_dir) or not os.listdir(title_id_dir):
            return []
        title_ids = []
        for title_id in os.listdir(title_id_dir):
            if os.path.isdir(os.path.join(title_id_dir, title_id)) and title_id not in blacklist_list:
                title_ids.append(title_id.upper())
        return title_ids

    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = SwitchROMSFrame(self.tab("My ROMs"), self.settings, self.cache, self.get_title_ids, "ryujinx")
        self.current_roms_frame.grid(row=0, column=0, sticky="nsew")
