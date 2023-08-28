import os
from tkinter import messagebox

import customtkinter
from PIL import Image

from gui.frames.app_settings import AppSettings
from gui.frames.dolphin_settings import DolphinSettings
from gui.frames.yuzu_settings import YuzuSettings


class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent", width=20)
        self.settings = settings 
        self.parent_frame = parent_frame
        self.build_gui()
    def build_gui(self):
        self.lock_image =  customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("padlock_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("padlock_dark")), size=(20, 20))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # create settings navigation frame      
        self.settings_navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.settings_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.settings_navigation_frame.grid_rowconfigure(4, weight=1)

        # create settings navigation menu buttons
        self.dolphin_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=20, height=25, border_spacing=10, text="Dolphin",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_settings_button_event)
        self.dolphin_settings_button.grid(row=1, column=0, padx=2, pady=(2,0), sticky="ew")
        
        self.yuzu_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=20, height=25, border_spacing=10, text="Yuzu",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_settings_button_event)
        self.yuzu_settings_button.grid(row=2, column=0, padx=2, sticky="ew")
        
        self.appearance_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=20, height=25, border_spacing=10, text="Appearance",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.appearance_settings_button_event)
        self.appearance_settings_button.grid(row=3, column=0, padx=2, sticky="ew")
        self.settings_lock_button = customtkinter.CTkButton(self.settings_navigation_frame, text="Lock", image = self.lock_image, anchor="w", command = self.lock_settings)
        self.settings_lock_button.grid(row=6, column=0, padx = 20, pady=20)

        # set default paths and other useful paths 
        installer_paths = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Emulator Files")
        user_saves_directory = os.path.join(os.getcwd(), "User Data")
        switch_firmware_keys_folder_path = os.path.join(installer_paths, "Yuzu Files")
        self.user_profile = os.path.expanduser('~')
        self.temp_extract_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Temp")
         
        self.default_dolphin_settings_install_directory = os.path.join(self.user_profile, "AppData\\Local\\Dolphin Emulator\\")
        self.default_dolphin_settings_user_directory = os.path.join(self.user_profile, "AppData\\Roaming\\Dolphin Emulator")
        self.default_dolphin_settings_global_save_directory = os.path.join(user_saves_directory, "Dolphin")
        self.default_dolphin_settings_export_directory = os.path.join(user_saves_directory, "Dolphin")
        self.default_dolphin_settings_dolphin_zip_directory = os.path.join(installer_paths, 'Dolphin 5.0-19870.zip')
            
        self.default_yuzu_settings_install_directory = os.path.join(self.user_profile, "AppData\\Local\\yuzu\\yuzu-windows-msvc\\")
        self.default_yuzu_settings_user_directory = os.path.join(self.user_profile, "AppData\\Roaming\\yuzu\\")
        self.default_yuzu_settings_global_save_directory = os.path.join(user_saves_directory, "Yuzu")
        self.default_yuzu_settings_export_directory = os.path.join(user_saves_directory, "Yuzu")
        self.default_yuzu_settings_installer_path = os.path.join(installer_paths, 'yuzu_install.exe')
        self.default_yuzu_settings_firmware_path = os.path.join(switch_firmware_keys_folder_path, "Firmware 16.0.3 (Rebootless Update 2).zip")
        self.default_yuzu_settings_key_path = os.path.join(switch_firmware_keys_folder_path, "Keys 16.0.3.zip")
        
        self.dolphin_settings_frame = DolphinSettings(self, self.settings)
        self.yuzu_settings_frame = YuzuSettings(self, self.settings)
        self.appearance_settings_frame = AppSettings(self, self.settings)
        
    def dolphin_settings_button_event(self):
        self.select_settings_frame_by_name("dolphin")
    def yuzu_settings_button_event(self):
        self.select_settings_frame_by_name("yuzu")
    def appearance_settings_button_event(self):
        self.select_settings_frame_by_name("appearance")
        
    def select_settings_frame_by_name(self, name):
        # set button color for selected button
        self.yuzu_settings_button.configure(fg_color=("gray75", "gray25") if name == "yuzu" else "transparent")
        self.dolphin_settings_button.configure(fg_color=("gray75", "gray25") if name == "dolphin" else "transparent")
        self.appearance_settings_button.configure(fg_color=("gray75", "gray25") if name == "appearance" else "transparent")
        # show selected frame
        if name == "dolphin":
            self.dolphin_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dolphin_settings_frame.grid_forget()
        if name == "yuzu":
            self.yuzu_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_settings_frame.grid_forget()
        if name == "appearance":
            self.appearance_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.appearance_settings_frame.grid_forget()
    def lock_settings(self):
        self.parent_frame.settings_unlocked = False
        self.parent_frame.select_frame_by_name("None")
    