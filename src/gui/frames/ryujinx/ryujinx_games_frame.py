import customtkinter
from gui.frames.my_switch_games_frame import MySwitchGamesFrame


class RyujinxROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, settings, cache):
        super().__init__(master, corner_radius=7, anchor="nw")
        self.emulator = master.ryujinx
        self.event_manager = master.event_manager
        self.assets = master.assets
        self.master = master
        self.roms = None
        self.cache = cache
        self.settings = settings
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()


    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = MySwitchGamesFrame(self.tab("My ROMs"), cache=self.cache, assets=self.assets, event_manager=self.event_manager, emulator_name="ryujinx", emulator_object=self.emulator)
        self.current_roms_frame.grid(row=0, column=0, sticky="nsew")
