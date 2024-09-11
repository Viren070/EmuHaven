import customtkinter
from customtkinter import ThemeManager


class EmulatorFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, paths, settings, versions, assets):
        super().__init__(parent_frame,  corner_radius=0, bg_color="transparent")
        self.settings = settings
        self.metadata = self.versions = versions
        self.paths = paths
        self.assets = assets
        self.parent_frame = parent_frame
        self.build_frame()

    def build_frame(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # create yuzu navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=20, border_width=2)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        # create yuzu menu buttons
        text_color = ThemeManager.theme["CTkLabel"]["text_color"]
        self.start_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, width=120, height=25, image=self.assets.play_image, border_spacing=10, text="Play",
                                                    fg_color="transparent", text_color=text_color,
                                                    anchor="w", command=self.start_button_event)
        self.start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2, 0))

        
        self.manage_data_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, width=120, height=25, border_spacing=10, text="Manage Data",
                                                            fg_color="transparent", text_color=text_color,
                                                            anchor="w", command=self.manage_data_button_event)

        self.manage_data_button.grid(row=2, column=0, padx=2, sticky="ew")

        self.manage_games_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, width=120, height=25, border_spacing=10, text="Manage Games",
                                                          fg_color="transparent", text_color=text_color,
                                                          anchor="w", command=self.manage_games_button_event)
        self.manage_games_button.grid(row=3, column=0, padx=2, sticky="ew")

        self.start_frame = None
        self.manage_data_frame = None
        self.manage_games_frame = None

    def start_button_event(self):
        self.select_frame_by_name("start")

    def manage_data_button_event(self):
        self.select_frame_by_name("data")

    def manage_games_button_event(self):
        self.select_frame_by_name("games")

    def select_frame_by_name(self, name):
        self.start_button.configure(fg_color=self.start_button.cget("hover_color") if name == "start" else "transparent")
        self.manage_data_button.configure(fg_color=self.manage_data_button.cget("hover_color") if name == "data" else "transparent")
        self.manage_games_button.configure(fg_color=self.manage_games_button.cget("hover_color") if name == "games" else "transparent")
        if name == "start":
            self.start_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.start_frame.grid_forget()
        if name == "data":
            self.manage_data_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.manage_data_frame.grid_forget()
        if name == "games":
            self.manage_games_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.manage_games_frame.grid_forget()
