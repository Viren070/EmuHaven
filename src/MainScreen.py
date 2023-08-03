import errno
import json
import os
import shutil
from datetime import datetime
from re import compile as comp
from hashlib import pbkdf2_hmac
from subprocess import run
from sys import platform
from threading import Thread
from time import perf_counter, sleep
from tkinter import filedialog, messagebox, ttk
from zipfile import ZipFile

import customtkinter
from colorama import Fore, Style, just_fix_windows_console
from PIL import Image

from PasswordDialog import PasswordDialog
from SwitchEmuTool import Application as FirmwareManager
from SwitchEmuTool import DownloadStatusFrame as InstallStatus

ERROR_INVALID_NAME = 123
just_fix_windows_console()
class MainScreen(customtkinter.CTk):    # create class 
    def __init__(self, opening_frames=['home', None]):
        start = perf_counter()
        print_and_write_to_log(f"------------------------[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][START] MainScreen.__init__: Initialising Object....-------------------------")
        self.settings_unlocked = True if opening_frames[1] == 'appearance' else False   # unlock settings if opening frames is appearance as user has only changed colour theme
        super().__init__()
        self.just_opened = True
        self.dolphin_is_running = False
        self.yuzu_automatic_firmwarekeys_install = True 
        self.yuzu_installer_available = True
        self.dolphin_installer_available = True
        try:
            self.define_images()
        except FileNotFoundError:   # image file was not found 
            messagebox.showerror("Image Error", "You are missing the image files. Please download the latest release from GitHub again and do not delete any folders.\n\nIf the GitHub repository is unavailable or you believe this was a mistake, contact the creator.")
            self.destroy()  # destroy app
            return
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.__init__: Creating widgets...")
        self.create_widgets()   # create widgets
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.__init__: Created widgets")
        self.select_frame_by_name(opening_frames[0])  # use opening frame in argument and set opening frames to them. 
        self.select_settings_frame_by_name(opening_frames[1])
        self.just_opened = False
        self.protocol("WM_DELETE_WINDOW", self.close_button_event)  # set function to be called when window is closed
        Thread(target=self.delete_temp_folders).start()  # start new thread to delete temp folders. 
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.__init__: Initialised in {(perf_counter() - start):.2}s")
        self.mainloop()  # start mainloop that allows tkinter window to function and respond.

    def define_images(self):   # set images as attributes for later use
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.dolphin_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "dolphin_logo.png")), size=(26, 26))
        self.yuzu_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "yuzu_logo.png")), size=(26, 26))
        self.play_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "play_light.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "play_dark.png")), size=(20, 20))
        self.settings_image =  customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "settings_light.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "settings_dark.png")), size=(20, 20))
        self.lock_image =  customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "padlock_light.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "padlock_dark.png")), size=(20, 20))
    def create_widgets(self):
        
        self.resizable(False, False)  # disable resizing of window
        self.title("Emulator Manager")  # set title of window
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.minsize(800,500) # set the minimum size of the window 
        
        
        # create navigation frame 
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # create navigation frame title. 
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text= "Emulator Manager v0.6.4",
                                                             compound="left", padx=5, font=customtkinter.CTkFont(size=12, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # create navigation menu buttons
        self.dolphin_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.dolphin_image, border_spacing=10, text="Dolphin",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_button_event)
        self.dolphin_button.grid(row=1, column=0, sticky="ew")

        self.yuzu_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.yuzu_image, border_spacing=10, text="Yuzu",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.yuzu_button_event)
        self.yuzu_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.settings_image, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=6, column=0, sticky="ew")

# create dolphin frame
        self.dolphin_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.dolphin_frame.grid_columnconfigure(1, weight=1)
        self.dolphin_frame.grid_rowconfigure(0, weight=1)
        
        self.dolphin_navigation_frame = customtkinter.CTkFrame(self.dolphin_frame, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.dolphin_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.dolphin_navigation_frame.grid_rowconfigure(4, weight=1)

        self.dolphin_start_button = customtkinter.CTkButton(self.dolphin_navigation_frame, corner_radius=0, width=50, height=25, image=self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_start_button_event)
        self.dolphin_start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))
        
        self.dolphin_start_frame = customtkinter.CTkFrame(self.dolphin_frame, corner_radius=0, fg_color="transparent")
        
        
        self.dolphin_actions_frame = customtkinter.CTkFrame(self.dolphin_start_frame)
        self.dolphin_actions_frame.grid(row=0, column=0, padx=40, pady=40)
        self.dolphin_actions_frame.grid_columnconfigure(3, weight=1)
        
        self.dolphin_launch_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, height=40, width=180, text="Launch Dolphin  ", image = self.play_image, font=customtkinter.CTkFont(size=15, weight="bold"), command=self.start_dolphin_wrapper)
        self.dolphin_launch_dolphin_button.grid(row=0, column=1, padx=30, pady=15, sticky="n")

        self.dolphin_global_data = customtkinter.StringVar(value="0")
        self.dolphin_global_user_data_checkbox = customtkinter.CTkCheckBox(self.dolphin_actions_frame, text = "Use Global Saves",
                                     variable=self.dolphin_global_data, onvalue="1", offvalue="0")
        self.dolphin_global_user_data_checkbox.grid(row=1,column=1, pady=(0,5))
        

        self.dolphin_install_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Install Dolphin", command=self.install_dolphin_wrapper)
        self.dolphin_install_dolphin_button.grid(row=0, column=0,padx=10, pady=5)

        self.dolphin_delete_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Delete Dolphin", fg_color="red", hover_color="darkred", command=self.delete_dolphin_button_event)
        self.dolphin_delete_dolphin_button.grid(row=0, column=2,padx=10, pady=5)

        
        self.dolphin_log_frame = customtkinter.CTkFrame(self.dolphin_start_frame)
        self.dolphin_log_frame.grid(row=1, column=0, sticky="nsew", padx=40)
        self.dolphin_log_frame.grid_columnconfigure(0, weight=2)

        
        self.dolphin_manage_data_button = customtkinter.CTkButton(self.dolphin_navigation_frame, corner_radius=0, width=20, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_manage_data_button_event)
        self.dolphin_manage_data_button.grid(row=2, column=0, sticky="ew", padx=2)
        self.dolphin_manage_data_frame = customtkinter.CTkFrame(self.dolphin_frame, corner_radius=0, fg_color="transparent")
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
        
        self.dolphin_import_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Import", command=self.import_dolphin_data)
        self.dolphin_export_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Export", command=self.export_dolphin_data)
        self.dolphin_delete_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Delete", command=self.delete_dolphin_data, fg_color="red", hover_color="darkred")

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
        
# create yuzu frame
        self.yuzu_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.yuzu_frame.grid_columnconfigure(1, weight=1)
        self.yuzu_frame.grid_rowconfigure(0, weight=1)
        # create yuzu navigation frame
        self.yuzu_navigation_frame = customtkinter.CTkFrame(self.yuzu_frame, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.yuzu_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.yuzu_navigation_frame.grid_rowconfigure(4, weight=1)
        # create yuzu menu buttons
        self.yuzu_start_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=20, height=25, image = self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_start_button_event)
        self.yuzu_start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))

        self.yuzu_manage_data_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=20, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_manage_data_button_event)
        self.yuzu_manage_data_button.grid(row=2, column=0, padx=2, sticky="ew")
        
        # create yuzu 'Play' frame and widgets
        self.yuzu_start_frame = customtkinter.CTkFrame(self.yuzu_frame, corner_radius=0, fg_color="transparent")

        self.yuzu_actions_frame = customtkinter.CTkFrame(self.yuzu_start_frame)
        self.yuzu_actions_frame.grid(row=0, column=0, padx=40, pady=40)
        self.yuzu_actions_frame.grid_columnconfigure(3, weight=1)
        
        self.yuzu_launch_yuzu_button = customtkinter.CTkButton(self.yuzu_actions_frame, height=40, width=170, image=self.play_image, text="Launch Yuzu  ", font=customtkinter.CTkFont(size=15, weight="bold"), command=self.start_yuzu_wrapper)
        self.yuzu_launch_yuzu_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")

        self.yuzu_global_data = customtkinter.StringVar(value="0")
        self.yuzu_global_user_data_checkbox = customtkinter.CTkCheckBox(self.yuzu_actions_frame, text = "Use Global Saves", variable=self.yuzu_global_data, onvalue="1", offvalue="0")
        self.yuzu_global_user_data_checkbox.grid(row=0,column=3, padx=(0,35))

        self.yuzu_install_yuzu_button = customtkinter.CTkButton(self.yuzu_actions_frame, text="Run Yuzu Installer", command=self.run_yuzu_install_wrapper)
        self.yuzu_install_yuzu_button.grid(row=0, column=1,padx=10, pady=5)
          
        self.yuzu_log_frame = customtkinter.CTkFrame(self.yuzu_start_frame)
        self.yuzu_log_frame.grid(row=1, column=0, sticky="nsew", padx=40)
        self.yuzu_log_frame.grid_columnconfigure(0, weight=3)
        # create yuzu 'Manage Data' frame and widgets
        self.yuzu_manage_data_frame = customtkinter.CTkFrame(self.yuzu_frame, corner_radius=0, fg_color="transparent")
        self.yuzu_manage_data_frame.grid_columnconfigure(0, weight=1)
        self.yuzu_manage_data_frame.grid_columnconfigure(1, weight=1)
        self.yuzu_manage_data_frame.grid_rowconfigure(0, weight=1)
        self.yuzu_manage_data_frame.grid_rowconfigure(1, weight=2)
        self.yuzu_data_actions_frame = customtkinter.CTkFrame(self.yuzu_manage_data_frame, height=150)
        self.yuzu_data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.yuzu_data_actions_frame.grid_columnconfigure(1, weight=1)

        self.yuzu_import_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data"])
        self.yuzu_export_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data"])
        self.yuzu_delete_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data"])
        
        self.yuzu_import_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Import", command=self.import_yuzu_data)
        self.yuzu_export_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Export", command=self.export_yuzu_data)
        self.yuzu_delete_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Delete", command=self.delete_yuzu_data, fg_color="red", hover_color="red")

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
        self.yuzu_firmware_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=20, height=25, border_spacing=10, text="Downloader",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.yuzu_firmware_button_event)
        self.yuzu_firmware_button.grid(row=3, column=0, padx=2, sticky="ew")
        
        self.yuzu_firmware_frame = customtkinter.CTkFrame(self.yuzu_frame, corner_radius=0, fg_color="transparent")
        self.yuzu_firmware_frame.grid_rowconfigure(2, weight=1)
        self.yuzu_firmware_frame.grid_columnconfigure(2, weight=1)
        self.yuzu_firmware = FirmwareManager(self.yuzu_firmware_frame)
        self.yuzu_firmware.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.yuzu_firmware_options_button = customtkinter.CTkButton(self.yuzu_firmware_frame, text="Options", command=self.yuzu_firmware.options_menu)
        self.yuzu_firmware_options_button.grid(row=1, column=1, pady=(0,30))
        # create settings frame 
        
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent", width=20)
        self.settings_frame.grid_columnconfigure(1, weight=1)
        self.settings_frame.grid_rowconfigure(0, weight=1)
        # create settings navigation frame      
        self.settings_navigation_frame = customtkinter.CTkFrame(self.settings_frame, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
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
        installer_paths = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        user_saves_directory = os.path.join(os.getcwd(), "User Data")
        switch_firmware_keys_folder_path = os.path.join(installer_paths, "Yuzu Files")
        self.user_profile = os.path.expanduser('~')
        self.temp_extract_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Temp")
         
        self.default_dolphin_settings_install_directory = os.path.join(self.user_profile, "AppData\\Local\\Dolphin Emulator\\")
        self.default_dolphin_settings_user_directory = os.path.join(self.user_profile, "AppData\\Roaming\\Dolphin Emulator")
        self.default_dolphin_settings_global_save_directory = os.path.join(user_saves_directory, "Dolphin")
        self.default_dolphin_settings_export_directory = os.path.join(user_saves_directory, "Dolphin")
        self.default_dolphin_settings_dolphin_zip_directory = os.path.join(installer_paths, 'Dolphin 5.0-19368.zip')
            
        self.default_yuzu_settings_install_directory = os.path.join(self.user_profile, "AppData\\Local\\yuzu\\yuzu-windows-msvc\\")
        self.default_yuzu_settings_user_directory = os.path.join(self.user_profile, "AppData\\Roaming\\yuzu\\")
        self.default_yuzu_settings_global_save_directory = os.path.join(user_saves_directory, "Yuzu")
        self.default_yuzu_settings_export_directory = os.path.join(user_saves_directory, "Yuzu")
        self.default_yuzu_settings_installer_path = os.path.join(installer_paths, 'yuzu_install.exe')
        self.default_yuzu_settings_firmware_path = os.path.join(switch_firmware_keys_folder_path, "Firmware 16.0.3 (Rebootless Update 2).zip")
        self.default_yuzu_settings_key_path = os.path.join(switch_firmware_keys_folder_path, "Keys 16.0.3.zip")

# create dolphin settings widgets          
        self.dolphin_settings_frame = customtkinter.CTkFrame(self.settings_frame, corner_radius=0, fg_color="transparent")
        self.dolphin_settings_frame.grid_columnconfigure(0, weight=1)
        
        self.dolphin_settings_user_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_install_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_global_save_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_export_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_dolphin_zip_directory_variable = customtkinter.StringVar()
       
        
        
        
        customtkinter.CTkLabel(self.dolphin_settings_frame, text="User Directory: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_user_directory_entry = customtkinter.CTkEntry(self.dolphin_settings_frame,  width=300)
        self.dolphin_settings_user_directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_user_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=0, column=3, padx=5, pady=10, sticky="e")
        ttk.Separator(self.dolphin_settings_frame, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
    
        customtkinter.CTkLabel(self.dolphin_settings_frame, text="Dolphin Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_install_directory_entry = customtkinter.CTkEntry(self.dolphin_settings_frame, width=300)
        self.dolphin_settings_install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_install_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=2,column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self.dolphin_settings_frame, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self.dolphin_settings_frame, text="Global Save Directory: ").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_global_save_directory_entry = customtkinter.CTkEntry(self.dolphin_settings_frame, width=300)
        self.dolphin_settings_global_save_directory_entry.grid(row=4, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_global_save_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=4, column=3, padx=5, sticky="E")
        ttk.Separator(self.dolphin_settings_frame, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self.dolphin_settings_frame, text="Export Directory: ").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_export_directory_entry = customtkinter.CTkEntry(self.dolphin_settings_frame, width=300)
        self.dolphin_settings_export_directory_entry.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_export_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=6, column=3, padx=5, sticky="E")
        ttk.Separator(self.dolphin_settings_frame, orient='horizontal').grid(row=7, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self.dolphin_settings_frame, text="Dolphin ZIP: ").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_dolphin_zip_directory_entry = customtkinter.CTkEntry(self.dolphin_settings_frame, width=300)
        self.dolphin_settings_dolphin_zip_directory_entry.grid(row=8, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_dolphin_zip_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self.dolphin_settings_frame, orient='horizontal').grid(row=9, columnspan=4, sticky="ew")
     
        self.dolphin_settings_actions_frame = customtkinter.CTkFrame(self.dolphin_settings_frame, fg_color="transparent")
        self.dolphin_settings_actions_frame.grid_columnconfigure(0, weight=1)
        self.dolphin_settings_actions_frame.grid(row=10,sticky="ew", columnspan=5, padx=10, pady=10)
        customtkinter.CTkButton(self.dolphin_settings_actions_frame, text="Apply", command=self.apply_dolphin_settings).grid(row=10,column=3,padx=10,pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_actions_frame, text="Restore Defaults", command=self.restore_default_dolphin_settings).grid(row=10, column=0, padx=10,pady=10, sticky="w")
 
        # create yuzu settings widgets        
        self.yuzu_settings_frame = customtkinter.CTkFrame(self.settings_frame, corner_radius=0, fg_color="transparent")
        self.yuzu_settings_frame.grid_columnconfigure(0, weight=1)
            
        self.yuzu_settings_install_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_user_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_global_save_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_export_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_installer_path_variable = customtkinter.StringVar()
        self.yuzu_settings_firmware_path_variable = customtkinter.StringVar()
        self.yuzu_settings_key_path_variable = customtkinter.StringVar()
        
        #1
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="User Directory: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_user_directory_entry = customtkinter.CTkEntry(self.yuzu_settings_frame,  width=300)
        self.yuzu_settings_user_directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_user_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=0, column=3, padx=5, pady=10, sticky="e")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
        #2
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="yuzu Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_install_directory_entry = customtkinter.CTkEntry(self.yuzu_settings_frame, width=300)
        self.yuzu_settings_install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_install_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=2,column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")
        #3
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="Global Save Directory: ").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_global_save_directory_entry = customtkinter.CTkEntry(self.yuzu_settings_frame, width=300)
        self.yuzu_settings_global_save_directory_entry.grid(row=4, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_global_save_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=4, column=3, padx=5, sticky="E")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")
        #4
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="Export Directory: ").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_export_directory_entry = customtkinter.CTkEntry(self.yuzu_settings_frame, width=300)
        self.yuzu_settings_export_directory_entry.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_export_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=6, column=3, padx=5, sticky="E")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=7, columnspan=4, sticky="ew")      
        #5
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="Yuzu Installer: ").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_yuzu_installer_path_entry = customtkinter.CTkEntry(self.yuzu_settings_frame, width=300)
        self.yuzu_settings_yuzu_installer_path_entry.grid(row=8, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_yuzu_installer_path_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=9, columnspan=4, sticky="ew")
        #6
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="Switch Firmware: ").grid(row=10, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_firmware_path_entry = customtkinter.CTkEntry(self.yuzu_settings_frame, width=300)
        self.yuzu_settings_firmware_path_entry.grid(row=10, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_firmware_path_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=10, column=3, padx=5, sticky="E")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=11, columnspan=4, sticky="ew")
        #7
        customtkinter.CTkLabel(self.yuzu_settings_frame, text="Switch Keys: ").grid(row=12, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_key_path_entry = customtkinter.CTkEntry(self.yuzu_settings_frame, width=300)
        self.yuzu_settings_key_path_entry.grid(row=12, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_frame, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_key_path_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=12, column=3, padx=5, sticky="E")
        ttk.Separator(self.yuzu_settings_frame, orient='horizontal').grid(row=13, columnspan=4, sticky="ew")
        
        self.yuzu_settings_actions_frame = customtkinter.CTkFrame(self.yuzu_settings_frame, fg_color="transparent")
        self.yuzu_settings_actions_frame.grid_columnconfigure(0, weight=1)
        self.yuzu_settings_actions_frame.grid(row=14,sticky="ew", columnspan=4, padx=10, pady=10)
        customtkinter.CTkButton(self.yuzu_settings_actions_frame, text="Apply", command=self.apply_yuzu_settings).grid(row=10,column=3,padx=10,pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_actions_frame, text="Restore Defaults", command=self.restore_default_yuzu_settings).grid(row=10, column=0, padx=10,pady=10, sticky="w")

        # define settings dictionaries 
        self.dolphin_settings_dict = {
            "1" : {
                "var" : self.dolphin_settings_user_directory_variable,
                "entry" : self.dolphin_settings_user_directory_entry,
                "default": self.default_dolphin_settings_user_directory,
                "name": "Dolphin User Directory"
            },
            "2" : {
                "var" : self.dolphin_settings_install_directory_variable,
                "entry" : self.dolphin_settings_install_directory_entry,
                "default": self.default_dolphin_settings_install_directory,
                "name" : "Dolphin Installation Directory"
            },
            "3" : {
                "var" : self.dolphin_settings_global_save_directory_variable,
                "entry" : self.dolphin_settings_global_save_directory_entry,
                "default": self.default_dolphin_settings_global_save_directory,
                "name": "Dolphin Global Save Directory"
            },
            "4" : {
                "var" : self.dolphin_settings_export_directory_variable,
                "entry" : self.dolphin_settings_export_directory_entry,
                "default": self.default_dolphin_settings_export_directory,
                "name" : "Dolphin Export Directory"
            },
            "5" : {
                "var" : self.dolphin_settings_dolphin_zip_directory_variable,
                "entry" : self.dolphin_settings_dolphin_zip_directory_entry,
                "default": self.default_dolphin_settings_dolphin_zip_directory,
                "name": "Dolphin ZIP Path"
            }
        }
        self.yuzu_settings_dict = {
            "1" : {
                "var" : self.yuzu_settings_user_directory_variable,
                "entry" : self.yuzu_settings_user_directory_entry,
                "default": self.default_yuzu_settings_user_directory,
                "name" : "Yuzu User Directory"
            },
            "2" : {
                "var" : self.yuzu_settings_install_directory_variable,
                "entry" : self.yuzu_settings_install_directory_entry,
                "default": self.default_yuzu_settings_install_directory,
                "name" : "Yuzu Installation Directory"
            },
            "3" : {
                "var" : self.yuzu_settings_global_save_directory_variable,
                "entry" : self.yuzu_settings_global_save_directory_entry,
                "default": self.default_yuzu_settings_global_save_directory,
                "name" : "Yuzu Global Save Directory"
            },
            "4" : {
                "var" : self.yuzu_settings_export_directory_variable,
                "entry" : self.yuzu_settings_export_directory_entry,
                "default": self.default_yuzu_settings_export_directory,
                "name" : "Yuzu Export Directory"
            },
            "5" : {
                "var" : self.yuzu_settings_installer_path_variable,
                "entry" : self.yuzu_settings_yuzu_installer_path_entry,
                "default": self.default_yuzu_settings_installer_path,
                "name" : "Yuzu Installer Path"
            },
            "6" : {
                "var" : self.yuzu_settings_firmware_path_variable,
                "entry" : self.yuzu_settings_firmware_path_entry,
                "default": self.default_yuzu_settings_firmware_path,
                "name" : "Yuzu Firmware ZIP Path"
            },
            "7" : {
                "var" : self.yuzu_settings_key_path_variable,
                "entry" : self.yuzu_settings_key_path_entry,
                "default": self.default_yuzu_settings_key_path,
                "name" : "Yuzu Key ZIP Path"
            }
        }
        # load settings from settings.json if found
        self.settings_path = os.path.join(os.getenv("APPDATA"),"Emulator Manager", "config")
        self.settings_file = os.path.join(self.settings_path, 'settings.json')
        
        # create appearance and themes widgets for settings menu 'Appearance'
        self.appearance_settings_frame = customtkinter.CTkFrame(self.settings_frame, corner_radius=0, fg_color="transparent")
        self.appearance_settings_frame.grid_columnconfigure(0, weight=1)
        
        self.appearance_mode_variable = customtkinter.StringVar()
        self.colour_theme_variable = customtkinter.StringVar()
        
        self.appearance_mode_variable.set(self._get_appearance_mode().title())
        self.colour_theme_variable.set(customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title())
        customtkinter.CTkLabel(self.appearance_settings_frame, text="Appearance Mode: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self.appearance_settings_frame, variable=self.appearance_mode_variable, values=["Dark", "Light"], command=self.change_appearance_mode).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self.appearance_settings_frame, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self.appearance_settings_frame, text="Colour Theme: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self.appearance_settings_frame, variable=self.colour_theme_variable, values=["Blue", "Dark Blue", "Green"], command=self.change_colour_theme).grid(row=2, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self.appearance_settings_frame, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")
        
        if not os.path.exists(self.settings_file): 
            self.previous_settings_available = False
        else:
            self.previous_settings_available = True
            
        if self.previous_settings_available:
            self.load_settings()
        else:
            self.restore_default_dolphin_settings()
            self.restore_default_yuzu_settings()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.create_widgets [END]")
    def change_colour_theme(self, theme, startup=False):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.change_colour_theme: Changing colour theme to {theme} with startup as {startup}")
        if customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title() == theme: # if current theme is the same as the proposed theme, return
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.change_colour_theme: Theme is already {theme}")
            return
        customtkinter.set_default_color_theme(theme.replace(" ","-").lower())  #set the theme to the proposed theme after converting to proper theme name
        if not startup: # if the colour theme is being changed in the settings page and not when loading from settings.json
            self.update_settings()   # update settings to reflect latest change in appearance settings
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.change_colour_theme: Theme changed to {theme}\n[CONSOLE] MainScreen.change_colour_theme: Destroying Current object") 
        self.destroy()   # destroy current window (because changing colour theme directly does not work)
        MainScreen(['settings','appearance'])  # create new window and open on the Appearance page 
        
    def change_appearance_mode(self, mode, startup=False):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.change_appearance_mode: changing appearance mode to {mode} with startup as {startup}")
        customtkinter.set_appearance_mode(mode.lower()) # change appearance mode using customtkinters function 
        if not startup:
            self.update_settings()   # update settings.json if change was through settings menu
            
    def update_settings(self):
        # define settings by using variables
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_settings: Defining new settings")
        settings = { 
            "dolphin_settings": {
                "Dolphin User Directory": self.dolphin_settings_dict["1"]['var'].get(),
                "Dolphin Installation Directory": self.dolphin_settings_dict["2"]['var'].get(),
                "Dolphin Global Save Directory": self.dolphin_settings_dict["3"]['var'].get(),
                "Dolphin Export Directory": self.dolphin_settings_dict["4"]['var'].get(),
                "Dolphin ZIP Path" : self.dolphin_settings_dict["5"]['var'].get()
                
            },
            "yuzu_settings": {
                "Yuzu User Directory": self.yuzu_settings_dict["1"]['var'].get(),
                "Yuzu Installation Directory": self.yuzu_settings_dict["2"]['var'].get(),
                "Yuzu Global Save Directory" : self.yuzu_settings_dict["3"]['var'].get(),
                "Yuzu Export Directory" : self.yuzu_settings_dict["4"]['var'].get(),
                "Yuzu Installer Path" : self.yuzu_settings_dict["5"]['var'].get(),
                "Yuzu Firmware ZIP Path" : self.yuzu_settings_dict["6"]['var'].get(),
                "Yuzu Key ZIP Path" : self.yuzu_settings_dict["7"]['var'].get()
                
            },
            "appearance_settings": {
                "Appearance Mode" : self.appearance_mode_variable.get(),
                "Colour Theme" : self.colour_theme_variable.get()
            }
        }
        # create settings.json at the correct path if it doesn't already exist
        if not(os.path.exists(self.settings_path)):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_settings: Making folders for settings path")
            os.makedirs(self.settings_path) # makes the necessary folders 
        try:
            with open(self.settings_file, "w") as file:
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_settings: Writing settings to settings.json")
                json.dump(settings, file)   # writes settings to settings.json
        except Exception as error:
            print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.update_settings: {error}" + Style.RESET_ALL)
            messagebox.showerror("Error", error)  # show error if raised
      
    def load_settings(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.load_settings [START]")
        if not os.path.exists(self.settings_file): 
            self.previous_settings_available = False
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.load_settings: No settings file found")
            return 
        self.previous_settings_available = True
        with open(self.settings_file, 'r') as file: # open settings.json as file
            try:
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.load_settings: Reading settings.json")
                loaded_settings = json.load(file) # store dictionary in 'loaded_settings'
            except json.decoder.JSONDecodeError as error:
                self.restore_default_dolphin_settings()   # if any error raised then restore the default settings. 
                self.restore_default_yuzu_settings()
                print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.load_settings: {error}" + Style.RESET_ALL)
                messagebox.showerror("Error", "Unable to load settings")
                return
        # define indiviudal dictonaries for each emulator.
        dolphin_settings = loaded_settings["dolphin_settings"]
        yuzu_settings = loaded_settings["yuzu_settings"]
        for entry_id, setting in self.dolphin_settings_dict.items(): # iterate through each setting in the current settings dictonary
            setting_name = setting['name']      # get the name of the setting 
            previous_setting_value = dolphin_settings[setting_name]  # get the previous value of the setting from the dictonary using the name as a key
            if entry_id == "5": 
                if "Temp\\_MEI" in previous_setting_value: # if Temp\\_MEI is in the previous setting value, then it means that it was from the -onefile exe and the path needs to be updated as it changes each time the app is opened
                    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.load_settings: Restoring {setting_name} to default as it uses old exe path")
                    self.restore_default_dolphin_settings(entry_id) # the default value will hold the new path 
                if not os.path.exists(previous_setting_value) and not os.path.exists(setting["default"]):
                    setting["var"].set("")
                    setting["entry"].delete(0, 'end')
                    setting["default"] = ""
                elif not os.path.exists(previous_setting_value) and os.path.exists(setting["default"]):
                    self.restore_default_dolphin_settings(entry_id)
                else:
                    setting["default"] = previous_setting_value
                    setting['var'].set(previous_setting_value)  # set the variable value to previous_value
                    setting['entry'].delete(0, 'end')
                    setting['entry'].insert(0, previous_setting_value)
                continue # go to next setting
            setting['var'].set(previous_setting_value)  # set the variable value to previous_value 
            setting['entry'].delete(0, 'end')   # set the value of the entry widget to the previous value 
            setting['entry'].insert(0, previous_setting_value)
        for entry_id, setting in self.yuzu_settings_dict.items():
            setting_name = setting['name']
            previous_setting_value = yuzu_settings[setting_name]
            if int(entry_id) >= 5: 
                if "Temp\\_MEI" in previous_setting_value: # if Temp\\_MEI is in the previous setting value, then it means that it was from the -onefile exe and the path needs to be updated as it changes each time the app is opened
                    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.load_settings: Restoring {setting_name} to default as it uses old exe path")
                    self.restore_default_yuzu_settings(entry_id)
                if not os.path.exists(previous_setting_value) and not os.path.exists(setting["default"]):
                    setting["var"].set("")
                    setting["entry"].delete(0, 'end')
                    setting["default"] = ""
                elif not os.path.exists(previous_setting_value) and os.path.exists(setting["default"]):
                    self.restore_default_yuzu_settings(entry_id)
                else:
                    setting["default"] = previous_setting_value
                    setting['var'].set(previous_setting_value)  # set the variable value to previous_value
                    setting['entry'].delete(0, 'end')
                    setting['entry'].insert(0, previous_setting_value)
                continue
            setting['var'].set(previous_setting_value)  # set the variable value to previous_value 
            setting['entry'].delete(0, 'end')   # set the value of the entry widget to the previous value 
            setting['entry'].insert(0, previous_setting_value)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.load_settings [END]")    
    def dolphin_button_event(self):
        self.select_frame_by_name("dolphin")

    def yuzu_button_event(self):
        self.select_frame_by_name("yuzu")

    def settings_button_event(self):
        self.select_frame_by_name("settings")
    
    def select_frame_by_name(self, name):
        if not self.just_opened and ( self.dolphin_settings_changed() or self.yuzu_settings_changed() ) and name != "settings":
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.select_frame_by_name: Settings changed")
            if messagebox.askyesno("Confirmation", "You have unsaved changes in the settings, leave anyways?"):
                self.revert_settings()
            else:
                return 
        self.settings_button.configure(fg_color=("transparent"))
        # show selected frame
        if name == "settings" and not self.settings_unlocked: 
            self.validate_password()
            return
        if name == "settings" and self.settings_unlocked:
            self.minsize(1100,500)
            self.settings_button.configure(fg_color=("gray75", "gray25"))
            self.settings_frame.grid(row=0, column=1, sticky="nsew")       
        else:
            self.settings_frame.grid_forget()
            self.select_settings_frame_by_name(None)
            self.minsize(800,500)
        self.dolphin_button.configure(fg_color=("gray75", "gray25") if name == "dolphin" else "transparent")
        self.yuzu_button.configure(fg_color=("gray75", "gray25") if name == "yuzu" else "transparent")
        
        if name == "dolphin":
            self.dolphin_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dolphin_frame.grid_forget()
            self.select_dolphin_frame_by_name(None)
        if name == "yuzu":
            self.yuzu_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_frame.grid_forget()
            self.select_yuzu_frame_by_name(None)
        
    def validate_password(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_password: creating password dialog")
        dialog = PasswordDialog(text="Enter password:", title="Settings Password")
        guess = dialog.get_input()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_password: received input of {guess}")
        if guess == "" or guess is None:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_password [END]")
            return
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_password: Comparing hashes")
        if pbkdf2_hmac('sha256', guess.encode('utf-8'), bytes(b'GI\xaaK"\xcd`\x1b\x06\xc9\x18\x82\xc8c\xc5\xc9(\xa3\xc3\x93\x9e\xd2\xde\x93\\\x85\xd4\xb5\x1f\xcc\xac\x92'), 100000, dklen=128 ) == bytes(b'\xda\xea,d\x865\xaeS\xb1\\!~\x1c\xf7X\xef\xdfS\x94\x07i\xb8\x83<\x17h\x11Fc\xfd\xbdE\xf8\x044\xd6\xf6\x93m\xc9\xd6`{\xd9.R\xa3\xfe\x86\x00\x90&_\x12=\xdf\x99\xae\xe5\x92w\xdd\xbcwf]\xf41\x94\xa4q\x81P\xfd\x9dv\x9a\xb5\xfb\x13N\xe3"\x00\xe20\xc3\xf0\x01:\x0c\x18\x1d\xb1\x9b\xbdi\xf8\x02\t\xc5\t\xc50n(T\xff\x8b\xb1!\xf1\xba2\xe2y\x94\x89\xae]\x1f\xede\x9c=\xday`'):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_password: Correct password given")
            self.settings_unlocked = True
            self.select_frame_by_name("settings")
            self.minsize(1100,500)
            return
        else:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_password: Incorrect password given")
            messagebox.showerror("Incorrect", "That is the incorrect password, to make changes to the settings you require a password")
            return 
        
    def dolphin_settings_button_event(self):
        self.select_settings_frame_by_name("dolphin")
    def yuzu_settings_button_event(self):
        self.select_settings_frame_by_name("yuzu")
    def appearance_settings_button_event(self):
        self.select_settings_frame_by_name("appearance")
        
    def select_settings_frame_by_name(self, name):
        # set button color for selected button
        if not self.just_opened:
            if self.dolphin_settings_changed() and name != "dolphin":
                if messagebox.askyesno("Confirmation", "You have unsaved changes in the settings for dolphin, leave anyways?"):
                    self.revert_settings("dolphin")
                else:
                    return 
            if self.yuzu_settings_changed() and name != "yuzu":
                if messagebox.askyesno("Confirmation", "You have unsaved changes in the settings for dolphin, leave anyways?"):
                    self.revert_settings("yuzu")
                else:
                    return 
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
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.lock_settings: Locking settings")
        self.settings_unlocked = False
        self.select_frame_by_name("None")
    
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


    def install_dolphin_wrapper(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.install_dolphin_wrapper")
        self.validate_optional_paths()
        if self.check_dolphin_installation() and not messagebox.askyesno("Confirmation", "Dolphin seems to already be installed, install anyways?"):
            return 
        if not self.dolphin_installer_available:
            print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.install_dolphin_wrapper: path to zip archive of dolphin has not been set" + Style.RESET_ALL)
            messagebox.showerror("Error", "The path to the Dolphin ZIP has not been set or is invalid, please check the settings")
            return
        
        Thread(target=self.extract_dolphin_install).start()
        
   
    def extract_dolphin_install(self): 
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.extract_dolphin_install: Extracting Dolphin")
        self.dolphin_install_dolphin_button.configure(state="disabled")
        self.dolphin_delete_dolphin_button.configure(state="disabled")
        self.dolphin_launch_dolphin_button.configure(state="disabled")
        dolphin_install_frame = InstallStatus(self.dolphin_log_frame, "Extracting Dolphin", self)
        dolphin_install_frame.skip_to_installation()
        dolphin_install_frame.grid(row=0, column=0, sticky="nsew")
        with ZipFile(self.dolphin_settings_dolphin_zip_directory_variable.get(), 'r') as archive:
            total_files = len(archive.namelist())
            extracted_files = 0
            
            for file in archive.namelist():
                archive.extract(file, self.dolphin_settings_install_directory_variable.get())
                extracted_files += 1
                # Calculate and display progress
                dolphin_install_frame.update_extraction_progress(extracted_files / total_files) 
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.extract_dolphin_install: Finished extracting dolphin")        
        messagebox.showinfo("Done", f"Installed Dolphin to {self.dolphin_settings_install_directory_variable.get()}")
        dolphin_install_frame.destroy()
        self.dolphin_install_dolphin_button.configure(state="normal")
        self.dolphin_delete_dolphin_button.configure(state="normal")
        self.dolphin_launch_dolphin_button.configure(state="normal")
        self.check_dolphin_installation()
    
    def delete_dolphin_button_event(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin_button_event")
        if self.dolphin_is_running:
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.delete_dolphin_button_event: Dolphin is running, cannot delete"+Style.RESET_ALL)
            messagebox.showerror("Error", "Please close Dolphin before trying to delete it. If dolphin is not open, try restarting the application")
            return
        if messagebox.askyesno("Confirmation", "Are you sure you wish to delete the Dolphin Installation. This will not delete your user data."):
            self.dolphin_delete_dolphin_button.configure(state="disabled", text="Deleting...")
            Thread(target=self.delete_dolphin).start()
        
    def delete_dolphin(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin: Started")
        try:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin: Deleting from {self.dolphin_settings_install_directory_variable.get()}")
            shutil.rmtree(self.dolphin_settings_install_directory_variable.get())
            self.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
        except FileNotFoundError as error:
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.delete_dolphin: {error}"+Style.RESET_ALL)
            messagebox.showinfo("Dolphin", "Installation of dolphin not found")
            self.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            return
        except Exception as e:
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.delete_dolphin: {e}"+Style.RESET_ALL)
            messagebox.showerror("Error", e)
            self.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            return
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin [END]")
        messagebox.showinfo("Success", "The Dolphin installation was successfully was removed")
        
    def start_dolphin_wrapper(self):
        self.validate_optional_paths()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin_wrapper [START]")
        if self.check_dolphin_installation():
            self.dolphin_is_running = True
            self.dolphin_launch_dolphin_button.configure(state="disabled", text="Launching...  ")
            self.dolphin_install_dolphin_button.configure(state="disabled")
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin_wrapper: Start Dolphin Thread")
            Thread(target=self.start_dolphin).start()
        else:
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.start_dolphin_wrapper: No dolphin installation found"+Style.RESET_ALL)
            messagebox.showerror("Error","A dolphin installation was not found. Please press Install Dolphin below to begin.")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin_wrapper [END]")
    def start_dolphin(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin [START]")
        if self.dolphin_global_data.get() == "1":
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin: Loading Data")
            self.copy_directory_with_progress((os.path.join(self.dolphin_settings_global_save_directory_variable.get(), os.getlogin())), self.dolphin_settings_user_directory_variable.get(), "Loading Dolphin Data", self.dolphin_log_frame)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin: Starting Dolphin...")
        self.dolphin_launch_dolphin_button.configure(state="disabled", text="Launched!  ")
        run([os.path.join(self.dolphin_settings_install_directory_variable.get(),'Dolphin.exe')], capture_output = True)
        self.dolphin_is_running = False
        if self.dolphin_global_data.get() == "1":
            self.dolphin_launch_dolphin_button.configure(state="disabled", text="Launch Dolphin  ")
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin: Saving Data")
            self.copy_directory_with_progress(self.dolphin_settings_user_directory_variable.get(), (os.path.join(self.dolphin_settings_global_save_directory_variable.get(), os.getlogin())), "Saving Dolphin Data", self.dolphin_log_frame)
        self.dolphin_launch_dolphin_button.configure(state="normal", text="Launch Dolphin  ")
        self.dolphin_install_dolphin_button.configure(state="normal")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_dolphin [END]")
    def check_dolphin_installation(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_dolphin_installation [START]")
        default_dolphin_location = os.path.join(self.dolphin_settings_install_directory_variable.get(),'Dolphin.exe')
        if os.path.exists(default_dolphin_location):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_dolphin_installation: Returning True")
            self.dolphin_installed = True
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_dolphin_installation [END]")
            return True
        else:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_dolphin_installation: Returning False")
            self.dolphin_installed = False
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_dolphin_installation [END]")
            return False
    
    def check_yuzu_installation(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_installation [START]")
        self.check_yuzu_firmware_and_keys()
        if os.path.exists(os.path.join(self.yuzu_settings_install_directory_variable.get(),'yuzu.exe')):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_installation: Returning True")
            self.yuzu_installed = True
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_installation [END]")
            return True
        else:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_installation: Returning False")
            self.yuzu_installed = False
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_installation [END]")
            return False
    
    def run_yuzu_install_wrapper(self):
        self.validate_optional_paths()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install_wrapper [START]")
        if not self.yuzu_installer_available:
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.start_yuzu_install_wrapper: Yuzu installer not found at {self.yuzu_settings_installer_path_variable.get()}"+Style.RESET_ALL)
            messagebox.showerror("Error", "The path to the yuzu installer has not been set in the settings or is invalid, please check the settings page.")
            return 
        self.yuzu_install_yuzu_button.configure(state="disabled")
        self.yuzu_launch_yuzu_button.configure(state="disabled")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install_wrapper: Start yuzu installer thread.")
        Thread(target=self.run_yuzu_install).start()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install_wrapper [END]")
    def run_yuzu_install(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install: Creating copy of yuzu_install.exe [START]")
        temp_dir = os.path.join(os.getenv("TEMP"),"yuzu-installer")
        os.makedirs(temp_dir, exist_ok=True)
        path_to_installer = self.yuzu_settings_installer_path_variable.get()
        target_installer = os.path.join(temp_dir, 'yuzu_install.exe')
        try:
            shutil.copy(path_to_installer, target_installer)
        except Exception as error:
            print_and_write_to_log(Fore.RED+ f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install: Error while copying - {error}"+Style.RESET_ALL)
            messagebox.showerror("Copy Error", f"Unable to make a copy of yuzu_install.exe\n\n{error}")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install: Running yuzu_install.exe")
        run([target_installer], capture_output = True)
        sleep(0.3) # trying to delete instantly causes PermissionError
        try:
            shutil.rmtree(temp_dir)
        except PermissionError as error:
            print_and_write_to_log(Fore.RED+ f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install: Error while deleting temp dir - {error}"+Style.RESET_ALL)
            messagebox.showerror("Delete Error", "Unable to delete temporary yuzu installer directory.")
        except Exception as error:
            print_and_write_to_log(Fore.RED+ f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install: Error while deleting temp dir - {error}"+Style.RESET_ALL)
        self.yuzu_install_yuzu_button.configure(state="normal")
        self.yuzu_launch_yuzu_button.configure(state="normal")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.run_yuzu_install [END]")
    def check_yuzu_firmware_and_keys(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_firmware_and_keys [START]")
        to_return = True
        if os.path.exists( os.path.join(self.yuzu_settings_user_directory_variable.get(), "keys\\prod.keys")):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_firmware_and_keys: Found keys")
            self.yuzu_keys_installed = True
        else:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_firmware_and_keys: No prod.keys found at {self.yuzu_settings_user_directory_variable.get()}")
            self.yuzu_keys_installed = False
            to_return = False
        if os.path.exists ( os.path.join(self.yuzu_settings_user_directory_variable.get(), "nand\\system\\Contents\\registered")) and os.listdir(os.path.join(self.yuzu_settings_user_directory_variable.get(), "nand\\system\\Contents\\registered")):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_firmware_and_keys: Found firmware files")
            self.firmware_installed = True
        else:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_firmware_and_keys: No Firmware files found at {self.yuzu_settings_user_directory_variable.get()}")
            self.firmware_installed = False
            to_return = False
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.check_yuzu_firmware_and_keys: returning={to_return} [END]")
        return to_return
    
    def install_missing_firmware_or_keys(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.install_missing_firmware_or_keys [START]")
        self.check_yuzu_firmware_and_keys()
        if not self.yuzu_keys_installed:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.install_missing_firmware_or_keys: Installing Keys")
            status_frame = InstallStatus(
            self.yuzu_log_frame, (os.path.basename(self.yuzu_settings_key_path_variable.get())), self)
            status_frame.grid(row=0, pady=10, sticky="EW")
            status_frame.skip_to_installation()
            try:
                self.yuzu_firmware.start_key_installation_custom(self.yuzu_settings_key_path_variable.get(), status_frame)
            except Exception as error:
                print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.install_missing_firmware_or_keys: During keys - {error}" + Style.RESET_ALL)
                messagebox.showerror("Unknown Error", f"An unknown error occured during key installation \n\n {error}")
                status_frame.destroy()
                return False
            status_frame.destroy()
        if not self.firmware_installed:
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.install_missing_firmware_or_keys: Installing Firmware")
            status_frame = InstallStatus(self.yuzu_log_frame, (os.path.basename(self.yuzu_settings_firmware_path_variable.get())), self)
            status_frame.grid(row=0, pady=10, sticky="EW")
            status_frame.skip_to_installation()
            try:
                self.yuzu_firmware.start_firmware_installation_from_custom_zip(self.yuzu_settings_firmware_path_variable.get(), status_frame)
            except Exception as error:
                print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.install_missing_firmware_or_keys: During firmware - {error}" + Style.RESET_ALL)
                messagebox.showerror("Unknown Error", f"An unknown error occured during firmware installation \n\n {error}")
                status_frame.destroy()
                return False
            status_frame.destroy()
        if self.check_yuzu_firmware_and_keys():
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.install_missing_firmware_or_keys: Returning True [END]")
            return True
        else:
            print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.install_missing_firmware_or_keys: Still missing firmware/keys after installing" + Style.RESET_ALL)
            messagebox.showerror("Install Error", "Unable to install keys or firmware. Try using the SwitchEmuTool to manually install through the options Menu")
            
    def start_yuzu_wrapper(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu_wrapper [START]")
        if not self.check_yuzu_installation():
            print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.start_yuzu_wrapper: no yuzu_installation found" + Style.RESET_ALL)
            messagebox.showerror("Error","A yuzu installation was not found. Please run the yuzu installer.")
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu_wrapper [END]")
            return
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu_wrapper: Starting yuzu thread [END]")
        self.yuzu_install_yuzu_button.configure(state="disabled")
        self.yuzu_launch_yuzu_button.configure(state="disabled", text="Launching...  ")
        Thread(target=self.start_yuzu).start()
    
    def start_yuzu(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu [START]")
        if self.yuzu_global_data.get() == "1":
            try:
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu: Loading Data")
                self.copy_directory_with_progress((os.path.join(self.yuzu_settings_global_save_directory_variable.get(), os.getlogin())), self.yuzu_settings_user_directory_variable.get(), "Loading Yuzu Data", self.yuzu_log_frame)
            except Exception as error:
                print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.start_yuzu: {error}" + Style.RESET_ALL)
                if not messagebox.askyesno("Error", f"Unable to load your data, would you like to continue\n\n Full Error: {error}"):
                    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu [END]")
                    return 
                    
        if not self.check_yuzu_firmware_and_keys():
            if messagebox.askyesno("Error","You are missing your keys or firmware. Without these files, the games will not run. Would you like to install the missing files?"):
                if not self.yuzu_automatic_firmwarekeys_install:
                    messagebox.showerror("Error", "The paths to the firmware and key archives have not been set or are invalid, please check the settings page.")
                    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu [END]")
                    return
                self.install_missing_firmware_or_keys()
            
        self.yuzu_is_running = True
        self.yuzu_launch_yuzu_button.configure(text="Launched!  ")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu: Running yuzu.exe")
        run([os.path.join(self.yuzu_settings_install_directory_variable.get(),'yuzu.exe')], capture_output = True)
        
        self.yuzu_is_running = False
        if self.yuzu_global_data.get() == "1":
            try:
                self.yuzu_launch_yuzu_button.configure(state="disabled", text="Launch Yuzu  ")
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu: Saving Yuzu Data")
                self.copy_directory_with_progress(self.yuzu_settings_user_directory_variable.get(), (os.path.join(self.yuzu_settings_global_save_directory_variable.get(), os.getlogin())), "Saving Yuzu Data", self.yuzu_log_frame)
            except Exception as error:
                print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.start_yuzu: {error}" + Style.RESET_ALL)
                messagebox.showerror("Save Error", f"Unable to save your data\n\nFull Error: {error}")
        self.yuzu_launch_yuzu_button.configure(state="normal", text="Launch Yuzu  ")
        self.yuzu_install_yuzu_button.configure(state="normal")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.start_yuzu [END]")
    
    def copy_directory_with_progress(self, source_dir, target_dir, title, log_frame):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.copy_directory_with_progress [START]")
        if not os.path.exists(source_dir):
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.copy_directory_with_progress: {source_dir} does not exist"+Style.RESET_ALL)
            messagebox.showerror("Path Error", f"Path does not exist: {source_dir}")
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.copy_directory_with_progress [END]")
            return
        progress_bar = InstallStatus(log_frame, title, self)
        progress_bar.skip_to_installation()
        progress_bar.grid(row=0, column=0, sticky="nsew")
        progress_bar.grid_propagate(False)
        # Get a list of all files and folders in the source directory
        all_files = []
        for root, dirs, files in os.walk(source_dir):
            all_files.extend([os.path.join(root, file) for file in files])

        # Get the total number of files to copy
        total_files = len(all_files)

        # Create the target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        def find_common_suffix(file_path, target_file_path):
            file_parts = file_path.split(os.sep)
            target_parts = target_file_path.split(os.sep)

            common_suffix = []
            while file_parts and target_parts and file_parts[-1] == target_parts[-1]:
                common_suffix.insert(0, file_parts.pop())
                target_parts.pop()

            return os.path.join(*common_suffix)

        # Copy files from source to target directory and display progress
        copied_files = 0
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.copy_directory_with_progress: Copying {source_dir} to {target_dir}")
        for file in all_files:
            
            
            target_file = os.path.join(target_dir, os.path.relpath(file, source_dir))
            target_dirname = os.path.dirname(target_file)
            
            progress_bar.install_status_label.configure(text=find_common_suffix(file, target_file))
            # Create the necessary directories in the target if they don't exist
            if not os.path.exists(target_dirname):
                os.makedirs(target_dirname)

            # Copy the file to the target directory
            shutil.copy2(file, target_file)

            copied_files += 1
            progress = (copied_files / total_files) 
            progress_bar.update_extraction_progress(progress)
        progress_bar.destroy()
        messagebox.showinfo(title, "Copy Complete!")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.copy_directory_with_progress [END]")
    
        
        
    def export_yuzu_data(self):
        
        mode = self.yuzu_export_optionmenu.get()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.export_yuzu_data, mode={mode} [START]")
        user_directory = self.yuzu_settings_user_directory_variable.get()
        export_directory = self.yuzu_settings_export_directory_variable.get()
        users_global_save_directory = os.path.join(export_directory, os.getlogin())
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No yuzu data on local drive found")
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.export_yuzu_data:mode={mode}: {user_directory} does not exist [END]"+Style.RESET_ALL)
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            self.start_copy_thread(user_directory, users_export_directory, "Exporting All Yuzu Data", self.yuzu_data_log)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            self.start_copy_thread(save_dir, os.path.join(users_export_directory, 'nand', 'user', 'save'), "Exporting Yuzu Save Data", self.yuzu_data_log)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.export_yuzu_data: mode={mode} [END]")
    def import_yuzu_data(self):
        mode = self.yuzu_import_optionmenu.get()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.import_yuzu_data: mode={mode} [START]")
        export_directory = self.yuzu_settings_export_directory_variable.get()
        user_directory = self.yuzu_settings_user_directory_variable.get()
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.import_yuzu_data:mode={mode}: {users_export_directory} does not exist [END]"+Style.RESET_ALL)
            return
        if mode == "All Data":
            self.start_copy_thread(users_export_directory, user_directory, "Import All Yuzu Data", self.yuzu_data_log)
        elif mode == "Save Data":
            save_dir = os.path.join(users_export_directory, 'nand', 'user', 'save')
            self.start_copy_thread(save_dir, os.path.join(user_directory, 'nand', 'user', 'save'), "Importing Yuzu Save Data", self.yuzu_data_log)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.import_yuzu_data: mode={mode} [END]")
    def delete_yuzu_data(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_yuzu_data [START]")
        if not messagebox.askyesno("Confirmation", "This will delete the data from Yuzu's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_yuzu_data [END]")
            return

        mode = self.yuzu_delete_optionmenu.get()
        result = ""

        user_directory = self.yuzu_settings_user_directory_variable.get()
        global_save_directory = self.yuzu_settings_global_save_directory_variable.get()
        export_directory = self.yuzu_settings_export_directory_variable.get()
        users_global_save_directory = os.path.join(global_save_directory, os.getlogin())
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        def delete_directory(directory):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_yuzu_data.delete_directory: directory={directory} [START]")
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_yuzu_data.delete_directory: Deleted Directory. [END]")
                return True
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_yuzu_data.delete_directory: Nothing Deleted [END]")
            return False

        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
            result += f"Data deleted from {users_global_save_directory}\n" if delete_directory(users_global_save_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            save_dir = os.path.join(global_save_directory, os.getlogin(), 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            if export_directory != global_save_directory:
                save_dir = os.path.join(export_directory, os.getlogin(), 'nand', 'user', 'save')
                result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""

        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_yuzu_data [END]")
    
    def export_dolphin_data(self):
        mode = self.dolphin_export_optionmenu.get()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.export_dolphin_data: mode={mode} [START]")
        user_directory = self.dolphin_settings_user_directory_variable.get()
        export_directory = self.dolphin_settings_export_directory_variable.get()
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No dolphin data on local drive found")
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.export_dolphin_data:mode={mode}: {user_directory} does not exist [END]"+Style.RESET_ALL)
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            self.start_copy_thread(user_directory, users_export_directory, "Exporting All Dolphin Data", self.dolphin_data_log)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.export_dolphin_data: mode={mode} [END]")    
    def import_dolphin_data(self):
        mode = self.dolphin_export_optionmenu.get()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.import_dolphin_data: mode={mode} [START]")
        user_directory = self.dolphin_settings_user_directory_variable.get()
        export_directory = self.dolphin_settings_export_directory_variable.get()
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No dolphin data associated with your username was found")
            print_and_write_to_log(Fore.RED+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.import_dolphin_data:mode={mode}: {users_export_directory} does not exist [END]"+Style.RESET_ALL)
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            self.start_copy_thread(users_export_directory, user_directory, "Importing All Dolphin Data", self.dolphin_data_log)
    def delete_dolphin_data(self):
        if not messagebox.askyesno("Confirmation", "This will delete the data from Dolphin's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        mode = self.dolphin_delete_optionmenu.get()
        result = ""
        user_directory = self.dolphin_settings_user_directory_variable.get()
        global_save_directory = self.dolphin_settings_global_save_directory_variable.get()
        export_directory = self.dolphin_settings_export_directory_variable.get()
        users_global_save_directory = os.path.join(global_save_directory, os.getlogin())
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        def delete_directory(directory):
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin_data.delete_directory: directory={directory} [START]")
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin_data.delete_directory: Deleted directory. [END]")
                return True
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin_data.delete_directory: Nothing Deleted [END]")
            return False
        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
            result += f"Data deleted from {users_global_save_directory}\n" if delete_directory(users_global_save_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
            
        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_dolphin_data [END]")
    def start_copy_thread(self, *args):
        Thread(target=self.copy_directory_with_progress, args=args).start()
    def update_dolphin_setting_with_explorer(self, entry_widget):
        def find_dolphin_entry_id_by_entry_widget(entry_widget):
            for entry_id, settings in self.dolphin_settings_dict.items():
                if settings["entry"] == entry_widget:
                    return entry_id

            # If the entry widget is not found in the dictionary, return None or any other value to indicate not found.
            return None
        entry_id = find_dolphin_entry_id_by_entry_widget(entry_widget)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_dolphin_setting_with_explorer: Setting id {entry_id} [START]")
        if entry_id == '5':
            dolphin_zip = filedialog.askopenfilename(initialdir=os.path.dirname(self.dolphin_settings_dict[entry_id]['var'].get()) if os.path.exists(self.dolphin_settings_dict[entry_id]['var'].get()) else os.getcwd(), filetypes=[("Dolphin 5.0-xxxxx.zip", "*zip")])
            if dolphin_zip is None or dolphin_zip == "":
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_dolphin_setting_with_explorer: Setting id {entry_id} Not updated as no input was given [END]")
                return 
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, dolphin_zip)
            if self.dolphin_settings_dict[entry_id]['default'] == "":
                self.dolphin_settings_dict[entry_id]['default'] = dolphin_zip
        else:
            directory = filedialog.askdirectory(initialdir=os.path.dirname(self.dolphin_settings_dict[entry_id]['var'].get()) if os.path.exists(self.dolphin_settings_dict[entry_id]['var'].get()) else os.getcwd())
            if directory is None or directory == "":
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_dolphin_setting_with_explorer: Setting id {entry_id} Not updated as no input was given [END]")
                return 
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, directory)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_dolphin_setting_with_explorer [END]")
        
            
    def apply_dolphin_settings(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.apply_dolphin_settings [START]")
        errors = ""
        for entry_id, settings in self.dolphin_settings_dict.items():
            entry_widget = settings["entry"]
            var = settings["var"]
            current_value = entry_widget.get()
            name = settings['name']
            if entry_id == "5": 
                if (current_value == "" or current_value is None):
                    messagebox.showwarning("Warning", "Leaving the dolphin zip path empty will result in the dolphin install button to not work. You will have to set your install directory to your own installation of Dolphin.")
                    self.dolphin_installer_available = False
                    var.set(current_value)
                    continue
                elif not os.path.exists(current_value):
                    errors+=f"'{name}' is Invalid. File does not exist\n"
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
                    continue
            if self.is_path_exists_or_creatable(current_value):
                var.set(current_value)
                if settings['default'] == "": settings['default'] = current_value
            else:
                errors+=f"'{name}' is Invalid\n"
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, var.get())
        if errors != "": messagebox.showerror("Incorrect Paths", errors)
        self.update_settings()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.apply_dolphin_settings [END]")
    def restore_default_dolphin_settings(self, entry_id=None):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.restore_default_dolphin_settings: entry_id={entry_id} [START]")
        if entry_id:
            # Restore the specific setting with the provided entry_id
            if entry_id in self.dolphin_settings_dict:
                settings = self.dolphin_settings_dict[entry_id]
                entry_widget = settings["entry"]
                default_value = settings["default"]
                var = settings["var"]

                entry_widget.delete(0, 'end')  # Clear the entry widget
                entry_widget.insert(0, default_value)  # Set the default value to the entry widget
                var.set(default_value)  # Update the associated StringVar variable with the default value
        else:
            # Restore all settings to their default values
            for entry_id, settings in self.dolphin_settings_dict.items():
                entry_widget = settings["entry"]
                default_value = settings["default"]
                var = settings["var"]

                entry_widget.delete(0, 'end')  # Clear the entry widget
                entry_widget.insert(0, default_value)  # Set the default value to the entry widget
                var.set(default_value)  # Update the associated StringVar variable with the default value
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.restore_default_dolphin_settings [END]")
        
        
    def update_yuzu_setting_with_explorer(self, entry_widget):
        
        
        def find_yuzu_entry_id_by_entry_widget(entry_widget):
            for entry_id, settings in self.yuzu_settings_dict.items():
                if settings["entry"] == entry_widget:
                    return entry_id

            # If the entry widget is not found in the dictionary, return None or any other value to indicate not found.
            return None
        entry_id = find_yuzu_entry_id_by_entry_widget(entry_widget)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_yuzu_settings_with_explorer: entry_id={entry_id} [START]")
        if entry_id == '5':
            yuzu_installer = filedialog.askopenfilename(initialdir=os.path.dirname(self.yuzu_settings_dict[entry_id]['var'].get()) if os.path.exists(self.yuzu_settings_dict[entry_id]['var'].get()) else os.getcwd(), filetypes=[("yuzu_install.exe", "*exe")])
            if yuzu_installer is None or yuzu_installer == "":
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_yuzu_settings_with_explorer: entry_id={entry_id} Not updated as input empty [END]")
                return 
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, yuzu_installer)
            if self.yuzu_settings_dict[entry_id]['default'] == "":
                self.yuzu_settings_dict[entry_id]['default'] = yuzu_installer
        elif int(entry_id) > 5:
            zip_archive = filedialog.askopenfilename(initialdir=os.path.dirname(self.yuzu_settings_dict[entry_id]['var'].get()) if os.path.exists(self.yuzu_settings_dict[entry_id]['var'].get()) else os.getcwd(), filetypes=[("Firmware" if entry_id=="6" else "Keys", "*zip")])
            if zip_archive is None or zip_archive == "":
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_yuzu_settings_with_explorer: entry_id={entry_id} Not updated as input empty [END]")
                return 
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, zip_archive)
            if self.yuzu_settings_dict[entry_id]['default'] == "":
                self.yuzu_settings_dict[entry_id]['default'] = zip_archive
        else:
            directory = filedialog.askdirectory(initialdir=os.path.dirname(self.yuzu_settings_dict[entry_id]['var'].get()) if os.path.exists(self.yuzu_settings_dict[entry_id]['var'].get()) else os.getcwd())
            if directory is None or directory == "":
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_yuzu_settings_with_explorer: entry_id={entry_id} Not updated as input empty [END]")
                return 
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, directory)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.update_yuzu_settings_with_explorer: entry_id={entry_id} [END]")
    
            
    def apply_yuzu_settings(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.apply_yuzu_settings [START]")
        errors = ""
        warnings = ""
        for entry_id, settings in self.yuzu_settings_dict.items():
            entry_widget = settings["entry"]
            var = settings["var"]
            current_value = entry_widget.get()
            name  = settings['name']
            if entry_id == "5":
                if (current_value == "" or current_value is None):
                    warnings+="Leaving the yuzu installer path empty will result in the button for the yuzu installer not working.\n\n"
                    self.yuzu_installer_available = False
                    var.set(current_value)
                    continue
                elif current_value.split(".")[-1] != "exe":
                    errors+=f"'{name}' is Invalid. Must be an exe file\n"
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
                    continue
                elif not os.path.exists(current_value):
                    errors+=f"'{name}' is Invalid. File does not exist\n"
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
                    continue 
            elif int(entry_id) > 5:
                if (current_value == "" or current_value is None):
                    warnings+="Leaving the paths for the firmware or key archives will result in the automatic installation not working.\n\n"
                    self.yuzu_automatic_firmwarekeys_install = False
                    var.set(current_value)
                    continue
                elif current_value.split(".")[-1] != "zip":
                    errors+=f"'{name}' is Invalid. Must be a ZIP File\n"
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
                    continue
                elif not os.path.exists(current_value):
                    errors+=f"'{name}' is Invalid. File does not exist\n"
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
                    continue
            if self.is_path_exists_or_creatable(current_value):
                var.set(current_value)
                if settings['default'] == "": settings['default'] = current_value
            else:
                errors+=f"'{name}' is Invalid\n"
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, var.get())
                
        if errors != "" and not self.just_opened: messagebox.showerror("Incorrect Paths", errors)
        if warnings != "" and not self.just_opened: messagebox.showwarning("Warning(s)", warnings)
        # have variables for entries, when apply clicked check values (use previous value in StringVar) and then if correct, set values to variables otherwise take value from StringVar and place in entry. 
        self.update_settings()
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.apply_yuzu_settings [END]")
    def restore_default_yuzu_settings(self, entry_id=None):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.restore_default_yuzu_settings: entry_id={entry_id} [START]")
        if entry_id:
            # Restore the specific setting with the provided entry_id
            if entry_id in self.yuzu_settings_dict:
                settings = self.yuzu_settings_dict[entry_id]
                entry_widget = settings["entry"]
                default_value = settings["default"]
                var = settings["var"]

                entry_widget.delete(0, 'end')  # Clear the entry widget
                entry_widget.insert(0, default_value)  # Set the default value to the entry widget
                var.set(default_value)  # Update the associated StringVar variable with the default value
        else:
            # Restore all settings to their default values
            for entry_id, settings in self.yuzu_settings_dict.items():
                entry_widget = settings["entry"]
                default_value = settings["default"]
                var = settings["var"]

                entry_widget.delete(0, 'end')  # Clear the entry widget
                entry_widget.insert(0, default_value)  # Set the default value to the entry widget
                var.set(default_value)  # Update the associated StringVar variable with the default value
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.restore_default_yuzu_settings [END]")
    def dolphin_settings_changed(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.dolphin_settings_changed [START]")
        for entry_id, settings in self.dolphin_settings_dict.items():
            entry_widget = settings["entry"]
            var = settings["var"]
            current_value = entry_widget.get()
            if current_value != var.get():
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.dolphin_settings_changed Returning True [END]")
                return True
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.dolphin_settings_changed Returning False [END]")
        return False
    def yuzu_settings_changed(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.yuzu_settings_changed [START]")
        for entry_id, settings in self.yuzu_settings_dict.items():
            entry_widget = settings["entry"]
            var = settings["var"]
            current_value = entry_widget.get()
            
            if current_value != var.get():
                print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.yuzu_settings_changed Returning True [END]")
                return True
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.yuzu_settings_changed: Returning False [END]")
        return False
    def revert_settings(self, mode="both"):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.revert_settings: mode={mode} [START]")
        if mode != "dolphin":
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.revert_settings: Reverting yuzu settings")
            for entry_id, settings in self.yuzu_settings_dict.items():
                entry_widget = settings["entry"]
                var = settings["var"]
                current_value = entry_widget.get()
                
                if current_value != var.get():
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
        if mode != "yuzu":
            print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.revert_settings: Reverting dolphin settings")
            for entry_id, settings in self.dolphin_settings_dict.items():
                entry_widget = settings["entry"]
                var = settings["var"]
                current_value = entry_widget.get()
                
                if current_value != var.get():
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, var.get())
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.revert_settings: mode={mode} [END]")
                    
    def validate_optional_paths(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_optional_paths [START]")
        if ( not os.path.exists(self.yuzu_settings_firmware_path_variable.get()) ) or ( not os.path.exists(self.yuzu_settings_key_path_variable.get())):
            print_and_write_to_log(Fore.LIGHTYELLOW_EX+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][WARNING] MainScreen.validate_optional_paths: Key path or firmware path doesn't exist "+Style.RESET_ALL)
            self.yuzu_automatic_firmwarekeys_install = False
        else:
            self.yuzu_automatic_firmwarekeys_install = True
        if os.path.exists(self.yuzu_settings_installer_path_variable.get()):
            self.yuzu_installer_available = True 
        else:
            print_and_write_to_log(Fore.LIGHTYELLOW_EX+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][WARNING] MainScreen.validate_optional_paths: yuzu_install.exe at given path doesn't exist"+Style.RESET_ALL)
            self.yuzu_installer_available = False
        if os.path.exists(self.dolphin_settings_dolphin_zip_directory_variable.get()):
            self.dolphin_installer_available = True 
        else:
            print_and_write_to_log(Fore.LIGHTYELLOW_EX+f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][WARNING] MainScreen.validate_optional_paths: Dolphin-x64.zip at given path doesn't exist"+Style.RESET_ALL)
            self.dolphin_installer_available = False
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.validate_optional_paths [END]")
    def close_button_event(self):
        if messagebox.askyesno("Confirmation","Are you sure you want to exit?"):
            self.destroy()
        
    def is_pathname_valid(self, pathname: str) -> bool:
          
        # If this pathname is either not a string or is but is empty, this pathname
        # is invalid.
        try:
            if not isinstance(pathname, str) or not pathname:
                return False

            # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
            # if any. Since Windows prohibits path components from containing `:`
            # characters, failing to strip this `:`-suffixed prefix would
            # erroneously invalidate all valid absolute Windows pathnames.
            _, pathname = os.path.splitdrive(pathname)

            # Directory guaranteed to exist. If the current OS is Windows, this is
            # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
            # environment variable); else, the typical root directory.
            root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
                if platform == 'win32' else os.path.sep
            assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

            # Append a path separator to this directory if needed.
            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

            # Test whether each path component split from this pathname is valid or
            # not, ignoring non-existent and non-readable path components.
            for pathname_part in pathname.split(os.path.sep):
                try:
                    os.lstat(root_dirname + pathname_part)
                # If an OS-specific exception is raised, its error code
                # indicates whether this pathname is valid or not. Unless this
                # is the case, this exception implies an ignorable kernel or
                # filesystem complaint (e.g., path not found or inaccessible).
                #
                # Only the following exceptions indicate invalid pathnames:
                #
                # * Instances of the Windows-specific "WindowsError" class
                #   defining the "winerror" attribute whose value is
                #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
                #   fine-grained and hence useful than the generic "errno"
                #   attribute. When a too-long pathname is passed, for example,
                #   "errno" is "ENOENT" (i.e., no such file or directory) rather
                #   than "ENAMETOOLONG" (i.e., file name too long).
                # * Instances of the cross-platform "OSError" class defining the
                #   generic "errno" attribute whose value is either:
                #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
                #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == ERROR_INVALID_NAME:
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        return False
        # If a "TypeError" exception was raised, it almost certainly has the
        # error message "embedded NUL character" indicating an invalid pathname.
        except TypeError as exc:
            return False
        # If no exception was raised, all path components and hence this
        # pathname itself are valid. (Praise be to the curmudgeonly python.)
        else:
            return True
        # If any other exception was raised, this is an unrelated fatal issue
        # (e.g., a bug). Permit this exception to unwind the call stack.
        #
        # Did we mention this should be shipped with Python already?
    def is_path_creatable(self, pathname: str) -> bool:
        '''
        `True` if the current user has sufficient permissions to create the passed
        pathname; `False` otherwise.
        '''
        # Parent directory of the passed path. If empty, we substitute the current
        # working directory (CWD) instead.
        dirname = os.path.dirname(pathname) or os.getcwd()
        if os.path.exists(pathname): return True
        
        try:
            path_to_file = os.path.join(pathname, "temp.txt")
            os.makedirs(pathname, exist_ok=True)
            with open(path_to_file, 'w') as f:
                f.write("Test")
            os.remove(path_to_file)
            return True
        except Exception as error:
            messagebox.showerror("Error", error)
            return False
        return os.access(dirname, os.W_OK)
        
    def is_path_exists_or_creatable(self, pathname: str) -> bool:
        
        '''
        `True` if the passed pathname is a valid pathname for the current OS _and_
        either currently exists or is hypothetically creatable; `False` otherwise.

        This function is guaranteed to _never_ raise exceptions.
        '''
        
        try:
            # To prevent "os" module calls from raising undesirable exceptions on
            # invalid pathnames, is_pathname_valid() is explicitly called first.
            #return self.is_pathname_valid(pathname)
            return self.is_pathname_valid(pathname) and (os.path.exists(pathname) or self.is_path_creatable(pathname))
        # Report failure on non-fatal filesystem complaints (e.g., connection
        # timeouts, permissions issues) implying this path to be inaccessible. All
        # other exceptions are unrelated fatal issues and should not be caught here.
        except OSError:
            return False
              
            
    def delete_temp_folders(self):
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_temp_folders: Deleting temp folders")
        current_path = os.path.dirname(os.path.realpath(__file__))   
        temp_directory = (os.getenv("TEMP"))
        for item in os.listdir(temp_directory):
            item_path = os.path.join(temp_directory, item)
            # Check if the item is a directory
            if os.path.isdir(item_path) and "_MEI" in item_path and item_path != current_path:
                try:
                    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_temp_folders: Deleting {item_path}")
                    shutil.rmtree(item_path)
                except:
                    print_and_write_to_log(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] MainScreen.delete_temp_folders: {item_path}" + Style.RESET_ALL)
        print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] MainScreen.delete_temp_folders [END]")
                
def load_appearance_settings():
    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] Loading appearance settings")
    try:
        path_to_settings = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "config", "settings.json")
        if os.path.exists(path_to_settings):
            with open(path_to_settings) as file:
        
                loaded_settings = json.load(file)
                appearance_settings = loaded_settings["appearance_settings"]
                theme = appearance_settings["Colour Theme"].replace(" ", "-").lower()
                appearance_mode = appearance_settings["Appearance Mode"].lower()
        else:
            appearance_mode = "system"
            theme = "blue"   
    except Exception as error_msg:
        appearance_mode = "system"
        theme = "blue"
        messagebox.showerror("Settings Error", f"Unable to load appearance settings\n\n{error_msg}")

    
    customtkinter.set_default_color_theme(theme)
    customtkinter.set_appearance_mode(appearance_mode)
    print_and_write_to_log(f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE] Loaded appearance settings")
def print_and_write_to_log(str):
    print(str)
    try:
        with open("emulator_manager.log", "a") as f:
            f.write(comp(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', str)+"\n")
    except:
        print(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}][CONSOLE][ERROR] COULD NOT WRITE TO LOG FILE" + Style.RESET_ALL)
        