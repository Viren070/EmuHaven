import os
from threading import Thread
from tkinter import messagebox

import customtkinter
from PIL import Image

from emulators.yuzu import Yuzu
from gui.frames.firmware_downloader import FirmwareDownloader


class YuzuFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame,  corner_radius=0, bg_color="transparent")
        self.settings = settings
        self.yuzu = Yuzu(self, settings)
        self.build_frame()
    def build_frame(self):
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.yuzu_mainline = customtkinter.CTkImage(Image.open(self.settings.get_image_path("yuzu_mainline")), size=(276, 129))
        self.yuzu_early_access = customtkinter.CTkImage(Image.open(self.settings.get_image_path("yuzu_early_access")), size=(276, 129))
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # create yuzu navigation frame
        self.yuzu_navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=20, border_width=2, border_color=("white","black"))
        self.yuzu_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.yuzu_navigation_frame.grid_rowconfigure(4, weight=1)
        # create yuzu menu buttons
        self.yuzu_start_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, image = self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.yuzu_start_button_event)
        self.yuzu_start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))

        self.yuzu_manage_data_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.yuzu_manage_data_button_event)
        self.yuzu_manage_data_button.grid(row=2, column=0, padx=2, sticky="ew")
        
        # create yuzu 'Play' frame and widgets
        self.yuzu_start_frame = customtkinter.CTkFrame(self, corner_radius=0, border_width=0)
        self.yuzu_start_frame.grid_columnconfigure(0, weight=1)
        self.yuzu_start_frame.grid_rowconfigure(0, weight=1)
        
        self.center_frame = customtkinter.CTkFrame(self.yuzu_start_frame, border_width=0)
        self.center_frame.grid(row=0, column=0, sticky="nsew")
        #self.center_frame.grid_propagate(False)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=2)
        
        ################################################# CONSIDER ADDING SEPARATE FRAMES FOR EARLY ACCESS VERSION WITH EITHER DIFFERENT MENU OR OPTIONMENU IN CORNER
        self.mainline_image = self.yuzu_mainline
        self.early_access_image = self.yuzu_early_access
        self.selected_channel = customtkinter.StringVar()
        self.version_optionmenu = customtkinter.CTkOptionMenu(self.center_frame, variable=self.selected_channel, command=self.switch_channel, values=["Mainline", "Early Access"])
        self.version_optionmenu.grid(row=0, column=0, padx=10, pady=20, sticky="ne")

        # Image button
        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.mainline_image)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.mainline_actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.mainline_actions_frame.grid(row=2, column=0, columnspan=3)
        
        self.mainline_actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.mainline_actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.mainline_actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally
        
        self.launch_mainline_button = customtkinter.CTkButton(self.mainline_actions_frame, height=40, width=170, image=self.play_image, text="Launch Yuzu  ", command=self.yuzu.start_yuzu_wrapper, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_mainline_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_mainline_button.bind("<Button-1>", command=lambda event: self.yuzu.start_yuzu_wrapper(event))
        #self.yuzu_launch_yuzu_button.bind("<Shift-Control-Button-1>", command=lambda event: self.yuzu.start_yuzu_wrapper(event, True))
        
        self.yuzu_global_data = customtkinter.StringVar(value=self.settings.app.auto_import__export_default_value)
        self.yuzu_global_user_data_checkbox = customtkinter.CTkCheckBox(self.mainline_actions_frame, text = "Auto Import/Export", variable=self.yuzu_global_data, onvalue="True", offvalue="False")
        self.yuzu_global_user_data_checkbox.grid(row=1,column=2, sticky="n", padx=10, pady=5)

        self.install_mainline_button = customtkinter.CTkButton(self.mainline_actions_frame, text="Install Yuzu", command=self.install_mainline_button_event)
        self.install_mainline_button.grid(row=0, column=1,padx=10, pady=5, sticky="ew")
        
        self.delete_mainline_button = customtkinter.CTkButton(self.mainline_actions_frame, text="Delete Yuzu", fg_color="red", hover_color="darkred", command=self.delete_mainline_button_event)
        self.delete_mainline_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        ### Early Access Actions Frame 
        
        self.early_access_actions_frame = customtkinter.CTkFrame(self.center_frame)
       
        self.early_access_actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.early_access_actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.early_access_actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally
        
        self.launch_early_access_button = customtkinter.CTkButton(self.early_access_actions_frame, height=40, width=170, image=self.play_image, text="Launch Yuzu EA  ", command=self.yuzu.start_yuzu_wrapper, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_early_access_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_early_access_button.bind("<Button-1>", command=lambda event: self.yuzu.start_yuzu_wrapper(event, True))
        #self.yuzu_launch_yuzu_button.bind("<Shift-Control-Button-1>", command=lambda event: self.yuzu.start_yuzu_wrapper(event, True))
        self.delete_early_access_button = customtkinter.CTkButton(self.early_access_actions_frame, text="Delete Yuzu EA", fg_color="red", hover_color="darkred", command=self.delete_early_access_button_event)
        self.delete_early_access_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        self.yuzu_global_user_data_checkbox = customtkinter.CTkCheckBox(self.early_access_actions_frame, text = "Auto Import/Export", variable=self.yuzu_global_data, onvalue="True", offvalue="False")
        self.yuzu_global_user_data_checkbox.grid(row=1,column=2, sticky="n", padx=10, pady=5)

        self.install_early_access_button = customtkinter.CTkButton(self.early_access_actions_frame, text="Install Yuzu EA  ", command=self.yuzu.install_ea_yuzu_wrapper)
        self.install_early_access_button.grid(row=0, column=1,padx=10, pady=5, sticky="ew")
        
        firmware_keys_frame = customtkinter.CTkFrame(self.center_frame)
        firmware_keys_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=3)
        firmware_keys_frame.grid_columnconfigure(0, weight=1)
        firmware_keys_frame.grid_columnconfigure(1, weight=1)
        firmware_keys_frame.grid_columnconfigure(2, weight=1)
        firmware_keys_frame.grid_rowconfigure(0, weight=1)
        self.install_firmware_button = customtkinter.CTkButton(firmware_keys_frame, text="Install Firmware", command=self.install_firmware_button_event)
        self.install_firmware_button.grid(row=0, column=0, pady=5, padx=20, sticky="w")
        self.install_keys_button = customtkinter.CTkButton(firmware_keys_frame, text="Install Keys", command=self.install_keys_button_event)
        self.install_keys_button.grid(row=0, column=3, pady=5, padx=20, sticky="e")
        
        
   
        self.yuzu_log_frame = customtkinter.CTkFrame(self.center_frame, fg_color='transparent', border_width=0)
        self.yuzu_log_frame.grid(row=4, column=0, padx=80, sticky="ew")
        self.yuzu_log_frame.grid_propagate(False)
        self.yuzu_log_frame.grid_columnconfigure(0, weight=3)
        # create yuzu 'Manage Data' frame and widgets
        self.yuzu_manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
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
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.yuzu_firmware_button_event)
        self.yuzu_firmware_button.grid(row=3, column=0, padx=2, sticky="ew")
        
        self.yuzu_firmware_frame = customtkinter.CTkFrame(self, corner_radius=0, border_width=0, fg_color="transparent")
        self.yuzu_firmware_frame.grid_rowconfigure(2, weight=1)
        self.yuzu_firmware_frame.grid_columnconfigure(2, weight=1)
        self.yuzu_firmware = FirmwareDownloader(self.yuzu_firmware_frame)
        self.yuzu_firmware.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.yuzu_firmware_options_button = customtkinter.CTkButton(self.yuzu_firmware_frame, text="Options", command=self.yuzu_firmware.options_menu)
        self.yuzu_firmware_options_button.grid(row=1, column=1, pady=(0,30))
        
        self.early_access_actions_frame.grid_propagate(False)
        self.mainline_actions_frame.grid_propagate(False)
        self.selected_channel.set(self.settings.app.default_yuzu_channel)
        self.switch_channel()
    def configure_data_buttons(self, **kwargs):
        self.yuzu_delete_button.configure(**kwargs)
        self.yuzu_import_button.configure(**kwargs)
        self.yuzu_export_button.configure(**kwargs)
    def configure_mainline_buttons(self, state, **kwargs):
        self.launch_mainline_button.configure(state=state, **kwargs)
        self.install_mainline_button.configure(state=state)
        self.delete_mainline_button.configure(state=state)
    def configure_early_access_buttons(self, state, **kwargs):
        self.install_early_access_button.configure(state=state)
        self.launch_early_access_button.configure(state=state, **kwargs)
        self.delete_early_access_button.configure(state=state)
    def configure_firmware_key_buttons(self, state):
        self.install_firmware_button.configure(state=state)
        self.install_keys_button.configure(state=state)
    def revert_early_access_buttons(self):
        self.install_early_access_button.configure(text="Install Yuzu EA", state="normal")
        self.launch_early_access_button.configure(text="Launch Yuzu EA  ", width=170, state="normal")
        self.delete_early_access_button.configure(text="Delete Yuzu EA", state="normal")
    def revert_mainline_buttons(self):
        self.launch_mainline_button.configure(text="Launch Yuzu  ", width=170, state="normal")
        self.install_mainline_button.configure(text="Install Yuzu", state="normal")
        self.delete_mainline_button.configure(text="Delete Yuzu", state="normal")
    def yuzu_start_button_event(self):
        self.select_yuzu_frame_by_name("start")
    def yuzu_manage_data_button_event(self):
        self.select_yuzu_frame_by_name("data")
    def yuzu_firmware_button_event(self):
        self.select_yuzu_frame_by_name("firmware")

    def select_yuzu_frame_by_name(self, name):
        self.yuzu_start_button.configure(fg_color=self.yuzu_start_button.cget("hover_color") if name == "start" else "transparent")
        self.yuzu_manage_data_button.configure(fg_color=self.yuzu_manage_data_button.cget("hover_color") if name == "data" else "transparent")
        self.yuzu_firmware_button.configure(fg_color=self.yuzu_firmware_button.cget("hover_color") if name == "firmware" else "transparent")
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
    def switch_channel(self, value=None):
        value=self.selected_channel.get()
        if value == "Mainline":
            self.image_button.configure(image=self.mainline_image)
            self.mainline_actions_frame.grid(row=2, column=0, columnspan=3)
        else:
            self.mainline_actions_frame.grid_forget()
        if value=="Early Access":
            self.image_button.configure(image=self.early_access_image)
            self.early_access_actions_frame.grid(row=2, column=0, columnspan=3)
        else:
            self.early_access_actions_frame.grid_forget()
            
            
    def install_mainline_button_event(self):
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc")) and not messagebox.askyesno("Yuzu Exists", "There is already an installation of yuzu at the specified install directory, overwrite this installation?"):
            return 
        self.configure_mainline_buttons("disabled")
        thread=Thread(target=self.yuzu.install_mainline_handler)
        thread.start()
        #self.enable_buttons_after_thread(thread, "mainline")
   
    def delete_early_access_button_event(self):
        if not messagebox.askyesno("Delete Yuzu EA", "Are you sure you want to delete yuzu EA?"):
            return
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")):
            self.configure_early_access_action_buttons("disabled")
            Thread(target=self.yuzu.delete_early_access).start()
        else:
            messagebox.showinfo("Delete Yuzu EA", f"Could not find a yuzu EA installation at {os.path.join(self.settings.yuzu.install_directory, 'yuzu-windows-msvc-early-access')}")
    
    def delete_mainline_button_event(self):
        if not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")):
            messagebox.showinfo("Yuzu EA", f"No installation of Yuzu Early Access was found at {os.path.join(self.settings.yuzu.install_directory,'yuzu-windows-msvc-early-access')}")
            return 
        self.configure_mainline_buttons("disabled")
        thread=Thread(target=self.yuzu.delete_mainline)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["mainline"],)).start()
    
    def install_firmware_button_event(self):
        if self.yuzu.check_current_firmware() and not messagebox.askyesno("Firmware Exists", "You already seem to have firmware installed, install anyways?"):
            return 
        if not self.yuzu.verify_firmware_archive() and not messagebox.askyesno("Firmware Not Found", "You have not specified a path to a firmware archive in the settings menu, would you like to try installing the firmware from the internet?"):
            return 
        self.configure_firmware_key_buttons("disabled")
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        thread=Thread(target=self.yuzu.install_firmware_handler)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["firmware_keys","mainline","early_access"], )).start()
   
    def install_keys_button_event(self):
        if self.yuzu.check_current_keys() and not messagebox.askyesno("Keys Exist", "You already seem to have the decryption keys, install anyways?"):
            return 
        if not self.yuzu.verify_key_archive() and not messagebox.askyesno("Keys Not Found", "You have not specified a path to a key archive or prod.keys file in the settings menu, would you like to try downloading the keys through the internet?"):
            return 
        self.configure_firmware_key_buttons("disabled")
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        thread = Thread(target=self.yuzu.install_key_handler)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["firmware_keys","mainline","early_access"],)).start()
    def enable_buttons_after_thread(self, thread, buttons):
        thread.join()
        for button in buttons:
            if button == "mainline":
                self.configure_mainline_buttons("normal", text="Launch Yuzu  ", width=170)
            elif button == "early_access":
                self.configure_early_access_buttons("normal", text="Launch Yuzu EA  ", width=170)
            elif button == "firmware_keys":
                self.configure_firmware_key_buttons("normal")
            elif button == "data":
                self.configure_data_buttons(state="normal")
        