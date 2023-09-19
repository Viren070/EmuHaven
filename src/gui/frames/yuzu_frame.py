import os
from threading import Thread
from tkinter import messagebox

import customtkinter
from PIL import Image

from emulators.yuzu import Yuzu
from gui.frames.firmware_downloader import FirmwareDownloader
from utils.requests_utils import get_headers, get_resources_release
from gui.frames.yuzu_rom_frame import YuzuROMFrame

class YuzuFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings, metadata):
        super().__init__(parent_frame,  corner_radius=0, bg_color="transparent")
        self.settings = settings
        self.metadata = metadata
        self.yuzu = Yuzu(self, settings, metadata)
        self.mainline_version = None 
        self.early_access_version = None 
        self.firmware_keys_version = None
        self.installed_mainline_version = ""
        self.installed_early_access_version = ""
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
        self.yuzu_navigation_frame.grid_rowconfigure(5, weight=1)
        # create yuzu menu buttons
        self.yuzu_start_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, image = self.play_image, border_spacing=10, text="Play",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.yuzu_start_button_event)
        self.yuzu_start_button.grid(row=1, column=0, sticky="ew", padx=2, pady=(2,0))

        self.yuzu_manage_data_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage Data",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.yuzu_manage_data_button_event)
        self.yuzu_manage_data_button.grid(row=2, column=0, padx=2, sticky="ew")
        
        self.manage_roms_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Manage ROMs",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.manage_roms_button_event)
        self.manage_roms_button.grid(row=3, column=0, padx=2, sticky="ew")
        
        self.yuzu_firmware_button = customtkinter.CTkButton(self.yuzu_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Downloader",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.yuzu_firmware_button_event)
        self.yuzu_firmware_button.grid(row=4, column=0, padx=2, sticky="ew")
        
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
        
        self.launch_mainline_button = customtkinter.CTkButton(self.mainline_actions_frame, height=40, width=170, image=self.play_image, text="Launch Yuzu  ", command=self.launch_mainline_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_mainline_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_mainline_button.bind("<Button-1>", command=self.launch_mainline_button_event)

        self.install_mainline_button = customtkinter.CTkButton(self.mainline_actions_frame, text="Install Yuzu", command=self.install_mainline_button_event)
        self.install_mainline_button.grid(row=0, column=1,padx=10, pady=5, sticky="ew")
        
        self.delete_mainline_button = customtkinter.CTkButton(self.mainline_actions_frame, text="Delete Yuzu", fg_color="red", hover_color="darkred", command=self.delete_mainline_button_event)
        self.delete_mainline_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        ### Early Access Actions Frame 
        
        self.early_access_actions_frame = customtkinter.CTkFrame(self.center_frame)
       
        self.early_access_actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.early_access_actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.early_access_actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally
        
        self.launch_early_access_button = customtkinter.CTkButton(self.early_access_actions_frame, height=40, width=170, image=self.play_image, text="Launch Yuzu EA  ", command=self.launch_early_access_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_early_access_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_early_access_button.bind("<Button-1>", command=self.launch_early_access_button_event)
        
        self.delete_early_access_button = customtkinter.CTkButton(self.early_access_actions_frame, text="Delete Yuzu EA", fg_color="red", hover_color="darkred", command=self.delete_early_access_button_event)
        self.delete_early_access_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        

        self.install_early_access_button = customtkinter.CTkButton(self.early_access_actions_frame, text="Install Yuzu EA  ", command=self.install_early_access_button_event)
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
        
        self.yuzu_import_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Import", command=self.import_data_button_event)
        self.yuzu_export_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Export", command=self.export_data_button_event)
        self.yuzu_delete_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Delete", command=self.delete_data_button_event, fg_color="red", hover_color="darkred")

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
        
        
        self.yuzu_firmware_frame = customtkinter.CTkFrame(self, corner_radius=0, border_width=0, fg_color="transparent")
        self.yuzu_firmware_frame.grid_rowconfigure(2, weight=1)
        self.yuzu_firmware_frame.grid_columnconfigure(2, weight=1)
        self.yuzu_firmware = FirmwareDownloader(self.yuzu_firmware_frame)
        self.yuzu_firmware.grid(row=0, column=1, sticky="nsew")
        self.yuzu_firmware_options_button = customtkinter.CTkButton(self.yuzu_firmware_frame, text="Options", command=self.yuzu_firmware.options_menu)
        self.yuzu_firmware_options_button.grid(row=1, column=1, pady=(0,30))
        
        self.early_access_actions_frame.grid_propagate(False)
        self.mainline_actions_frame.grid_propagate(False)
        self.selected_channel.set(self.settings.app.default_yuzu_channel)
        self.switch_channel()
        
        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius = 0, bg_color = "transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = YuzuROMFrame(self.manage_roms_frame, self.yuzu, self.settings)
        self.rom_frame.grid(row=0, column=0,  padx=20, pady=20, sticky="nsew")
    
        Thread(target=self.fetch_versions, args=(False,)).start()
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
    def yuzu_start_button_event(self):
        self.select_yuzu_frame_by_name("start")
    def yuzu_manage_data_button_event(self):
        self.select_yuzu_frame_by_name("data")
    def yuzu_firmware_button_event(self):
        self.select_yuzu_frame_by_name("firmware")
    def manage_roms_button_event(self):
        self.select_yuzu_frame_by_name("roms")

    def select_yuzu_frame_by_name(self, name):
        self.yuzu_start_button.configure(fg_color=self.yuzu_start_button.cget("hover_color") if name == "start" else "transparent")
        self.yuzu_manage_data_button.configure(fg_color=self.yuzu_manage_data_button.cget("hover_color") if name == "data" else "transparent")
        self.manage_roms_button.configure(fg_color=self.manage_roms_button.cget("hover_color") if name == "roms" else "transparent")
        self.yuzu_firmware_button.configure(fg_color=self.yuzu_firmware_button.cget("hover_color") if name == "firmware" else "transparent")
        if name == "start":
            self.yuzu_start_frame.grid(row=0, column=1, sticky="nsew" )
        else:
            self.yuzu_start_frame.grid_forget()
        if name == "data":
            self.yuzu_manage_data_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_manage_data_frame.grid_forget()
        if name == "roms":
            self.manage_roms_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.manage_roms_frame.grid_forget()
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
            
            
            
    def launch_mainline_button_event(self, event=None):
        if event is None:
            return 
        if self.launch_mainline_button.cget("state") == "disabled":
            return 
        if not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc", "yuzu.exe")):
            messagebox.showerror("Yuzu", "Installation of yuzu not found, please install yuzu using the button to the left")
            return 
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        self.configure_firmware_key_buttons("disabled")
        shift_clicked = True if event.state & 1 else False
        thread=Thread(target=self.yuzu.launch_yuzu_handler, args=("mainline", shift_clicked, ))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["mainline","early_access", "firmware_keys"],)).start()
    def install_mainline_button_event(self):
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc")) and not messagebox.askyesno("Yuzu Exists", "There is already an installation of yuzu at the specified install directory, overwrite this installation?"):
            return 
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        self.configure_firmware_key_buttons("disabled")
        
        thread = Thread(target=self.yuzu.launch_yuzu_installer) if self.settings.app.use_yuzu_installer == "True" else Thread(target=self.yuzu.install_release_handler, args=("mainline", ))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["mainline","early_access", "firmware_keys"],)).start()
        
    
    def launch_early_access_button_event(self, event=None):
        if event is None:
            return
        if self.launch_early_access_button.cget("state") == "disabled":
            return 
        if not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access", "yuzu.exe")):
            messagebox.showerror("Yuzu", "Installation of yuzu early access not found, please install yuzu early access using the button to the left")
            return 
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        self.configure_firmware_key_buttons("disabled")
        shift_clicked = True if event.state & 1 else False
        thread=Thread(target=self.yuzu.launch_yuzu_handler, args=("early_access", shift_clicked, ))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["mainline","early_access", "firmware_keys"],)).start()
    def install_early_access_button_event(self):
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")) and not messagebox.askyesno("Yuzu Exists", "There is already an installation of yuzu at the specified install directory, overwrite this installation?"):
            return 
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        self.configure_firmware_key_buttons("disabled")
        thread=Thread(target=self.yuzu.install_release_handler, args=("early_access", ))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["mainline", "early_access", "firmware_keys"],)).start()
   
    def delete_early_access_button_event(self):
        if not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")):
            messagebox.showinfo("Delete Yuzu EA", f"Could not find a yuzu EA installation at {os.path.join(self.settings.yuzu.install_directory, 'yuzu-windows-msvc-early-access')} ")
            return
        if not messagebox.askyesno("Delete Yuzu EA", "Are you sure you want to delete yuzu EA?"):
            return
    
        self.configure_early_access_buttons("disabled")
        thread = Thread(target=self.yuzu.delete_early_access)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["early_access"],)).start()
        
    def delete_mainline_button_event(self):
        if not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc")):
            messagebox.showinfo("Delete Yuzu", f"Could not find a yuzu installation at {os.path.join(self.settings.yuzu.install_directory, 'yuzu-windows-msvc')} ")
            return
        if not messagebox.askyesno("Delete Yuzu", "Are you sure you want to delete yuzu?"):
            return
        self.configure_mainline_buttons("disabled")
        thread=Thread(target=self.yuzu.delete_mainline)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["mainline"],)).start()
    
    def install_firmware_button_event(self):
        if self.yuzu.check_current_firmware() and not messagebox.askyesno("Firmware Exists", "You already seem to have firmware installed, install anyways?"):
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
        self.configure_firmware_key_buttons("disabled")
        self.configure_mainline_buttons("disabled")
        self.configure_early_access_buttons("disabled")
        thread = Thread(target=self.yuzu.install_key_handler)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["firmware_keys","mainline","early_access"],)).start()
    def import_data_button_event(self):
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.yuzu.import_yuzu_data, args=(self.yuzu_import_optionmenu.get(),))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()
    def export_data_button_event(self):
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.yuzu.export_yuzu_data, args=(self.yuzu_export_optionmenu.get(),))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()
    def delete_data_button_event(self):
        if not messagebox.askyesno("Confirmation", "This will delete the data from Yuzu's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.yuzu.delete_yuzu_data, args=(self.yuzu_delete_optionmenu.get(),))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()
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
        Thread(target=self.fetch_versions).start()
        self.update_version_text()
    def fetch_versions(self, installed_only=True):
        if not installed_only:
            mainline_release = self.yuzu.get_latest_release("mainline")
            early_access_release = self.yuzu.get_latest_release("early_access")
            firmware_keys_release = get_resources_release("Firmware", get_headers(self.settings.app.token))
            if not all(all( val for val in arr) for arr in (mainline_release, early_access_release, firmware_keys_release)):
                return 
            self.mainline_version = mainline_release[1].version
            self.early_access_version = early_access_release[1].version
            self.firmware_keys_version = firmware_keys_release[1].name.replace("Alpha.", "").replace(".zip", "")
        self.installed_mainline_version = self.metadata.get_installed_version("mainline")
        self.installed_early_access_version = self.metadata.get_installed_version("early_access")
        self.update_version_text()
    def update_version_text(self):
        if self.early_access_version is not None:
            self.install_early_access_button.configure(text=f"Install Yuzu EA {self.early_access_version}")
        if self.mainline_version is not None:
            self.install_mainline_button.configure(text=f"Install Yuzu {self.mainline_version}")
        if self.firmware_keys_version is not None:
            self.install_firmware_button.configure(text=f"Install Firmware {self.firmware_keys_version}")
            self.install_keys_button.configure(text=f"Install Keys {self.firmware_keys_version}")
        if self.installed_mainline_version != "":
            self.launch_mainline_button.configure(text=f"Launch Yuzu {self.installed_mainline_version}  ")
        else:
            self.launch_mainline_button.configure(text=f"Launch Yuzu  ")
        if self.installed_early_access_version != "":
            self.launch_early_access_button.configure(text=f"Launch Yuzu EA {self.installed_early_access_version}  ")
        else:
            self.launch_early_access_button.configure(text=f"Launch Yuzu EA  ")