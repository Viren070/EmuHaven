import customtkinter
from PIL import Image

from emulators.dolphin import Dolphin


class DolphinFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.dolphin = Dolphin(self, settings)
        self.settings = settings
        self.build_frame()
    def build_frame(self):
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.dolphin_navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.dolphin_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.dolphin_navigation_frame.grid_rowconfigure(4, weight=1)

        self.dolphin_start_button = customtkinter.CTkButton(self.dolphin_navigation_frame, corner_radius=0, width=100, height=25, image=self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_start_button_event)
        self.dolphin_start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))
        
        self.dolphin_start_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.dolphin_start_frame.grid_columnconfigure(0, weight=1)
        self.dolphin_start_frame.grid_columnconfigure(1, weight=1)
        self.dolphin_start_frame.grid_rowconfigure(0, weight=1)
        self.dolphin_start_frame.grid_rowconfigure(1, weight=2)
        
        self.dolphin_actions_frame = customtkinter.CTkFrame(self.dolphin_start_frame)
        self.dolphin_actions_frame.grid(row=0, column=0, sticky="ew", padx=(80,0), pady=(40,0))
        
        self.dolphin_actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.dolphin_actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.dolphin_actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        
        self.dolphin_launch_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, height=40, width=180, text="Launch Dolphin  ", image = self.play_image, font=customtkinter.CTkFont(size=15, weight="bold"), command=self.dolphin.start_dolphin_wrapper)
        self.dolphin_launch_dolphin_button.grid(row=0, column=1, padx=30, pady=15, sticky="nsew")

        self.dolphin_global_data = customtkinter.StringVar(value=self.settings.app.global_saves_default_value)
        self.dolphin_global_user_data_checkbox = customtkinter.CTkCheckBox(self.dolphin_actions_frame, text = "Use Global Saves",
                                     variable=self.dolphin_global_data, onvalue="True", offvalue="False")
        self.dolphin_global_user_data_checkbox.grid(row=1,column=1, pady=(0,5))
        

        self.dolphin_install_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Install Dolphin", command=self.dolphin.install_dolphin_wrapper)
        self.dolphin_install_dolphin_button.grid(row=0, column=0,padx=10, pady=5, sticky="ew")

        self.dolphin_delete_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Delete Dolphin", fg_color="red", hover_color="darkred", command=self.dolphin.delete_dolphin_button_event)
        self.dolphin_delete_dolphin_button.grid(row=0, column=2,padx=10, sticky="ew", pady=5)

        
        self.dolphin_log_frame = customtkinter.CTkFrame(self.dolphin_start_frame, height=100, fg_color='transparent')
        self.dolphin_log_frame.grid(row=1, column=0, sticky="ew", padx=(80,0), pady=(0,40))
        self.dolphin_log_frame.grid_columnconfigure(0, weight=2)

        
        self.dolphin_manage_data_button = customtkinter.CTkButton(self.dolphin_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_manage_data_button_event)
        self.dolphin_manage_data_button.grid(row=2, column=0, sticky="ew", padx=2)
        self.dolphin_manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.dolphin_manage_data_frame.grid_columnconfigure(0, weight=1)
        self.dolphin_manage_data_frame.grid_columnconfigure(1, weight=1)
        self.dolphin_manage_data_frame.grid_rowconfigure(0, weight=1)
        self.dolphin_manage_data_frame.grid_rowconfigure(1, weight=2)
        self.dolphin_data_actions_frame = customtkinter.CTkFrame(self.dolphin_manage_data_frame, height=150)
        self.dolphin_data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.dolphin_data_actions_frame.grid_columnconfigure(1, weight=1)

        self.dolphin_import_optionmenu = customtkinter.CTkOptionMenu(self.dolphin_data_actions_frame, width=300, values=["All Data"])
        self.dolphin_export_optionmenu = customtkinter.CTkOptionMenu(self.dolphin_data_actions_frame, width=300, values=["All Data"])
        self.dolphin_delete_optionmenu = customtkinter.CTkOptionMenu(self.dolphin_data_actions_frame, width=300, values=["All Data"])
        
        self.dolphin_import_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Import", command=self.dolphin.import_dolphin_data)
        self.dolphin_export_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Export", command=self.dolphin.export_dolphin_data)
        self.dolphin_delete_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Delete", command=self.dolphin.delete_dolphin_data, fg_color="red", hover_color="darkred")

        self.dolphin_import_optionmenu.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_import_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.dolphin_export_optionmenu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_export_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.dolphin_delete_optionmenu.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_delete_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.dolphin_data_log = customtkinter.CTkFrame(self.dolphin_manage_data_frame) 
        self.dolphin_data_log.grid(row=1, column=0, padx=20, pady=20, columnspan=3, sticky="new")
        self.dolphin_data_log.grid_columnconfigure(0, weight=1)
        self.dolphin_data_log.grid_rowconfigure(1, weight=1)
        
    def configure_data_buttons(self, **kwargs):
        self.dolphin_delete_button.configure(**kwargs)
        self.dolphin_import_button.configure(**kwargs)
        self.dolphin_export_button.configure(**kwargs)
    def dolphin_start_button_event(self):
        self.select_dolphin_frame_by_name("start")
    def dolphin_manage_data_button_event(self):
        self.select_dolphin_frame_by_name("data")
        
    def select_dolphin_frame_by_name(self, name):
        self.dolphin_start_button.configure(fg_color=("gray75", "gray25") if name == "start" else "transparent")
        self.dolphin_manage_data_button.configure(fg_color=("gray75", "gray25") if name == "data" else "transparent")
        if name == "start":
            self.dolphin_start_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dolphin_start_frame.grid_forget()
        if name == "data":
            self.dolphin_manage_data_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dolphin_manage_data_frame.grid_forget()
            
    
