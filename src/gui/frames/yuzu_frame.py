import customtkinter
from PIL import Image

from emulators.yuzu import Yuzu
from gui.firmware_downloader import FirmwareDownloader


class YuzuFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame,  corner_radius=0, fg_color="transparent")
        self.settings = settings
        self.yuzu = Yuzu(self, settings)
        self.build_frame()
    def build_frame(self):
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # create yuzu navigation frame
        self.yuzu_navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.yuzu_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.yuzu_navigation_frame.grid_rowconfigure(4, weight=1)
        # create yuzu menu buttons
        self.yuzu_start_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, image = self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_start_button_event)
        self.yuzu_start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))

        self.yuzu_manage_data_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_manage_data_button_event)
        self.yuzu_manage_data_button.grid(row=2, column=0, padx=2, sticky="ew")
        
        # create yuzu 'Play' frame and widgets
        self.yuzu_start_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.yuzu_actions_frame = customtkinter.CTkFrame(self.yuzu_start_frame)
        self.yuzu_actions_frame.grid(row=0, column=0, padx=40, pady=40)
        self.yuzu_actions_frame.grid_columnconfigure(3, weight=1)
        
        self.yuzu_launch_yuzu_button = customtkinter.CTkButton(self.yuzu_actions_frame, height=40, width=170, image=self.play_image, text="Launch Yuzu  ", command=self.yuzu.start_yuzu_wrapper, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.yuzu_launch_yuzu_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.yuzu_launch_yuzu_button.bind("<Button-1>", command=lambda event: self.yuzu.start_yuzu_wrapper(event))
        self.yuzu_launch_yuzu_button.bind("<Shift-Control-Button-1>", command=lambda event: self.yuzu.start_yuzu_wrapper(event, True))
        
        self.yuzu_global_data = customtkinter.StringVar(value=self.settings.app.global_saves_default_value)
        self.yuzu_global_user_data_checkbox = customtkinter.CTkCheckBox(self.yuzu_actions_frame, text = "Use Global Saves", variable=self.yuzu_global_data, onvalue="True", offvalue="False")
        self.yuzu_global_user_data_checkbox.grid(row=0,column=3, padx=(0,35))

        self.yuzu_install_yuzu_button = customtkinter.CTkButton(self.yuzu_actions_frame, text="Run Yuzu Installer", command=self.yuzu.run_yuzu_install_wrapper)
        self.yuzu_install_yuzu_button.grid(row=0, column=1,padx=10, pady=5)
        self.yuzu_install_yuzu_button.bind("<Button-1>", command=lambda event: self.yuzu.run_yuzu_install_wrapper(event))
        self.yuzu_install_yuzu_button.bind("<Shift-Control-Button-1>", command=lambda event: self.yuzu.install_ea_yuzu_wrapper(event))
        
        self.yuzu_log_frame = customtkinter.CTkFrame(self.yuzu_start_frame)
        self.yuzu_log_frame.grid(row=1, column=0, sticky="nsew", padx=40)
        self.yuzu_log_frame.grid_columnconfigure(0, weight=3)
        # create yuzu 'Manage Data' frame and widgets
        self.yuzu_manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.yuzu_manage_data_frame.grid_columnconfigure(0, weight=1)
        self.yuzu_manage_data_frame.grid_columnconfigure(1, weight=1)
        self.yuzu_manage_data_frame.grid_rowconfigure(0, weight=1)
        self.yuzu_manage_data_frame.grid_rowconfigure(1, weight=2)
        self.yuzu_data_actions_frame = customtkinter.CTkFrame(self.yuzu_manage_data_frame, height=150)
        self.yuzu_data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.yuzu_data_actions_frame.grid_columnconfigure(1, weight=1)

        self.yuzu_import_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data", "Exclude 'nand' & 'keys'"])
        self.yuzu_export_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data", "Exclude 'nand' & 'keys'"])
        self.yuzu_delete_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data", "Exclude 'nand' & 'keys'"])
        
        self.yuzu_import_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Import", command=self.yuzu.import_yuzu_data)
        self.yuzu_export_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Export", command=self.yuzu.export_yuzu_data)
        self.yuzu_delete_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Delete", command=self.yuzu.delete_yuzu_data, fg_color="red", hover_color="darkred")

        self.yuzu_import_optionmenu.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_import_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.yuzu_export_optionmenu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_export_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.yuzu_delete_optionmenu.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_delete_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.yuzu_data_log = customtkinter.CTkFrame(self.yuzu_manage_data_frame) 
        self.yuzu_data_log.grid(row=1, column=0, padx=20, pady=20, columnspan=3, sticky="new")
        self.yuzu_data_log.grid_columnconfigure(0, weight=1)
        self.yuzu_data_log.grid_rowconfigure(1, weight=1)
        # create yuzu downloader button, frame and widgets
        self.yuzu_firmware_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Downloader",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_firmware_button_event)
        self.yuzu_firmware_button.grid(row=3, column=0, padx=2, sticky="ew")
        
        self.yuzu_firmware_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.yuzu_firmware_frame.grid_rowconfigure(2, weight=1)
        self.yuzu_firmware_frame.grid_columnconfigure(2, weight=1)
        self.yuzu_firmware = FirmwareDownloader(self.yuzu_firmware_frame)
        self.yuzu_firmware.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.yuzu_firmware_options_button = customtkinter.CTkButton(self.yuzu_firmware_frame, text="Options", command=self.yuzu_firmware.options_menu)
        self.yuzu_firmware_options_button.grid(row=1, column=1, pady=(0,30))
        
    def configure_data_buttons(self, **kwargs):
        self.yuzu_delete_button.configure(**kwargs)
        self.yuzu_import_button.configure(**kwargs)
        self.yuzu_export_button.configure(**kwargs)
        
    def yuzu_start_button_event(self):
        self.select_yuzu_frame_by_name("start")
    def yuzu_manage_data_button_event(self):
        self.select_yuzu_frame_by_name("data")
    def yuzu_firmware_button_event(self):
        self.select_yuzu_frame_by_name("firmware")

    def select_yuzu_frame_by_name(self, name):
        self.yuzu_start_button.configure(fg_color=("gray75", "gray25") if name == "start" else "transparent")
        self.yuzu_manage_data_button.configure(fg_color=("gray75", "gray25") if name == "data" else "transparent")
        self.yuzu_firmware_button.configure(fg_color=("gray75", "gray25") if name == "firmware" else "transparent")
        if name == "start":
            self.yuzu_start_frame.grid(row=0, column=1, sticky="nsew" )
        else:
            self.yuzu_start_frame.grid_forget()
        if name == "data":
            self.yuzu_manage_data_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_manage_data_frame.grid_forget()

        if name == "firmware":
            self.yuzu_firmware_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_firmware_frame.grid_forget()