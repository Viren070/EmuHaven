import customtkinter
from gui.frames.my_switch_games_frame import MySwitchGamesFrame


class YuzuGamesFrame(customtkinter.CTkTabview):
    def __init__(self, master, settings, cache, event_manager):
        super().__init__(master, corner_radius=7, anchor="nw")
        self.emulator = master.yuzu
        self.master = master
        self.assets = master.assets
        self.roms = None
        self.settings = settings
        self.cache = cache
        self.event_manager = event_manager

        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()



    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = MySwitchGamesFrame(self.tab("My ROMs"), cache=self.cache, assets=self.assets, event_manager=self.event_manager, emulator_name="yuzu", emulator_object=self.emulator)
        self.current_roms_frame.grid(row=0, column=0, sticky="nsew")
