import customtkinter

from gui.frames.current_roms_frame import CurrentROMSFrame


class RyujinxROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, dolphin, settings):
        super().__init__(master, height=500, width=700)
        self.master = master 
        self.roms = None
        self.settings = settings 
        self.dolphin = dolphin 
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()
        
        
    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)

        
        self.current_roms_frame = CurrentROMSFrame(self.tab("My ROMs"), self, self.settings.ryujinx,  (".nsp"), scan_subdirectories=True)
        self.current_roms_frame.grid(row=0, column=0, sticky="nsew")
       