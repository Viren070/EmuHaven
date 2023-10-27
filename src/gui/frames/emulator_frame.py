import customtkinter 
from PIL import Image 


class EmulatorFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings, metadata):
        super().__init__(parent_frame,  corner_radius=0, bg_color="transparent")
        self.settings = settings 
        self.metadata = metadata
        self.parent_frame = parent_frame
        self.build_frame()
    def build_frame(self):
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # create yuzu navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)
        # create yuzu menu buttons
        self.start_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, width=100, height=25, image = self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.start_button_event)
        self.start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))

        self.manage_data_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.manage_data_button_event)
        self.manage_data_button.grid(row=2, column=0, padx=2, sticky="ew")
        
        self.manage_roms_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage ROMs",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.manage_roms_button_event)
        self.manage_roms_button.grid(row=3, column=0, padx=2, sticky="ew")
        
        self.start_frame = None 
        self.manage_data_frame = None 
        self.manage_roms_frame = None
        
    def start_button_event(self):
        self.select_frame_by_name("start")
        
    def manage_data_button_event(self):
        self.select_frame_by_name("data")
    def manage_roms_button_event(self):
        self.select_frame_by_name("roms")

    def select_frame_by_name(self, name):
        self.start_button.configure(fg_color=self.start_button.cget("hover_color") if name == "start" else "transparent")
        self.manage_data_button.configure(fg_color=self.manage_data_button.cget("hover_color") if name == "data" else "transparent")
        self.manage_roms_button.configure(fg_color=self.manage_roms_button.cget("hover_color") if name == "roms" else "transparent")    
        if name == "start":
            self.start_frame.grid(row=0, column=1, sticky="nsew" )
        else:
            self.start_frame.grid_forget()
        if name == "data":
            self.manage_data_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.manage_data_frame.grid_forget()
        if name == "roms":
            self.manage_roms_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.manage_roms_frame.grid_forget()