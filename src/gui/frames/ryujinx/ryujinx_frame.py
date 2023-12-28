import os
from threading import Thread
from tkinter import messagebox

import customtkinter
from CTkToolTip import CTkToolTip
from PIL import Image

from emulators.ryujinx import Ryujinx
from gui.frames.emulator_frame import EmulatorFrame
from gui.frames.firmware_keys_frame import FirmwareKeysFrame
from gui.frames.progress_frame import ProgressFrame
from gui.frames.ryujinx.ryujinx_rom_frame import RyujinxROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector

FOLDERS = ["bis", "games", "mods", "profiles", "sdcard", "system"]
class RyujinxFrame(EmulatorFrame):
    def __init__(self, parent_frame, settings, metadata, cache):
        super().__init__(parent_frame, settings, metadata)
        self.ryujinx = Ryujinx(self, settings, metadata)
        self.cache = cache
        self.ryujinx_version = None
        self.installed_firmware_version = "Unknown"
        self.installed_key_version = "Unknown"
        self.installed_ryujinx_version = ""
        self.add_to_frame()

    def add_to_frame(self):
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                 dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.ryujinx_banner = customtkinter.CTkImage(Image.open(self.settings.get_image_path("ryujinx_banner")), size=(276, 129))
        # create ryujinx 'Play' frame and widgets
        self.start_frame = customtkinter.CTkFrame(self, corner_radius=0, border_width=0)
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)

        self.center_frame = customtkinter.CTkFrame(self.start_frame, border_width=0)
        self.center_frame.grid(row=0, column=0, sticky="nsew")

        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=2)

        # Image button
        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.ryujinx_banner)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.actions_frame.grid(row=2, column=0, columnspan=3)

        self.actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_button = customtkinter.CTkButton(self.actions_frame, height=40, width=225, image=self.play_image, text="Launch Ryujinx  ", command=self.launch_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_button.bind("<Button-1>", command=self.launch_button_event)
        CTkToolTip(self.launch_button, message="Click me to launch Ryujinx.\nShift-click me to launch without checking for updates.")
        self.install_button = customtkinter.CTkButton(self.actions_frame, text="Install Ryujinx", command=self.install_button_event)
        self.install_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.install_button.bind("<Button-1>", command=self.install_button_event)
        CTkToolTip(self.install_button, message="Click me to download and install the latest release of Ryujinx from the internet\nShift-Click me to install Ryujinx with a custom archive")

        self.delete_button = customtkinter.CTkButton(self.actions_frame, text="Delete Ryujinx", fg_color="red", hover_color="darkred", command=self.delete_button_event)
        self.delete_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        CTkToolTip(self.delete_button, message="Click me to delete the installation of Ryujinx at the directory specified in settings.")

        self.firmware_keys_frame = FirmwareKeysFrame(self.center_frame, self)
        self.firmware_keys_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=3)

        self.log_frame = customtkinter.CTkFrame(self.center_frame, fg_color='transparent', border_width=0)
        self.log_frame.grid(row=4, column=0, padx=80, sticky="ew")
        self.log_frame.grid_propagate(False)
        self.log_frame.grid_columnconfigure(0, weight=3)
        self.ryujinx.main_progress_frame = ProgressFrame(self.log_frame)
        # create ryujinx 'Manage Data' frame and widgets
        self.manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_data_frame.grid_columnconfigure(0, weight=1)
        self.manage_data_frame.grid_columnconfigure(1, weight=1)
        self.manage_data_frame.grid_rowconfigure(0, weight=1)
        self.manage_data_frame.grid_rowconfigure(1, weight=2)
        self.data_actions_frame = customtkinter.CTkFrame(self.manage_data_frame, height=150)
        self.data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.data_actions_frame.grid_columnconfigure(1, weight=1)

        self.import_optionmenu = customtkinter.CTkOptionMenu(self.data_actions_frame, width=300, values=["All Data", "Save Data", "Custom..."])
        self.export_optionmenu = customtkinter.CTkOptionMenu(self.data_actions_frame, width=300, values=["All Data", "Save Data", "Custom..."])
        self.delete_optionmenu = customtkinter.CTkOptionMenu(self.data_actions_frame, width=300, values=["All Data", "Save Data", "Custom..."])

        self.import_data_button = customtkinter.CTkButton(self.data_actions_frame, text="Import", command=self.import_data_button_event)
        self.export_data_button = customtkinter.CTkButton(self.data_actions_frame, text="Export", command=self.export_data_button_event)
        self.delete_data_button = customtkinter.CTkButton(self.data_actions_frame, text="Delete", command=self.delete_data_button_event, fg_color="red", hover_color="darkred")

        self.import_optionmenu.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.import_data_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.export_optionmenu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.export_data_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.delete_optionmenu.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.delete_data_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.data_log = customtkinter.CTkFrame(self.manage_data_frame)
        self.data_log.grid(row=1, column=0, padx=20, pady=20, columnspan=3, sticky="new")
        self.data_log.grid_columnconfigure(0, weight=1)
        self.data_log.grid_rowconfigure(1, weight=1)
        self.ryujinx.data_progress_frame = ProgressFrame(self.data_log)
        # create ryujinx downloader button, frame and widgets

        self.actions_frame.grid_propagate(False)

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = RyujinxROMFrame(self.manage_roms_frame, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0,  padx=20, pady=20, sticky="nsew")

    def configure_data_buttons(self, **kwargs):
        self.delete_data_button.configure(**kwargs)
        self.import_data_button.configure(**kwargs)
        self.export_data_button.configure(**kwargs)

    def configure_action_buttons(self, state, **kwargs):
        self.launch_button.configure(state=state, **kwargs)
        self.install_button.configure(state=state)
        self.delete_button.configure(state=state)

    def install_firmware_handler(self, *args):
        self.ryujinx.install_firmware_handler(*args)

    def install_key_handler(self, *args):
        self.ryujinx.install_key_handler(*args)

    def launch_button_event(self, event=None):
        if event is None or self.launch_button.cget("state") == "disabled":
            return
        if not os.path.exists(os.path.join(self.settings.ryujinx.install_directory, "publish", "ryujinx.exe")):
            messagebox.showerror("Ryujinx", "Installation of Ryujinx not found, please install Ryujinx using the button to the left")
            return
        self.configure_action_buttons("disabled")
        self.firmware_keys_frame.configure_firmware_key_buttons("disabled")
        shift_clicked = True if event.state & 1 else False
        thread = Thread(target=self.ryujinx.launch_ryujinx_handler, args=(shift_clicked, ))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["action", "firmware_keys"],)).start()

    def install_button_event(self, event=None):
        if event is None or self.install_button.cget("state") == "disabled":
            return
        if os.path.exists(os.path.join(self.settings.ryujinx.install_directory, "publish")) and not messagebox.askyesno("Directory Exists", "The directory already exists. Are you sure you want to overwrite the contents inside?"):
            return
        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Ryujinx Archive", text="Enter path to Ryujinx archive: ")
            path_to_archive = path_to_archive.get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror("Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
        self.configure_action_buttons("disabled")
        self.firmware_keys_frame.configure_firmware_key_buttons("disabled")

        thread = Thread(target=self.ryujinx.install_release_handler, args=(False, path_to_archive, ))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["action", "firmware_keys"],)).start()

    def install_firmware_button_event(self, event=None):
        if event is None or self.firmware_keys_frame.install_firmware_button.cget("state") == "disabled":
            return
        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Firmware Archive", text="Type path to Firmware Archive: ")
            path_to_archive = path_to_archive.get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror("Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
            args = ("path", path_to_archive, )
        else:
            if self.firmware_keys_frame.firmware_option_menu.cget("state") == "disabled":
                messagebox.showerror("Error", "Please ensure that a correct version has been chosen from the menu to the left")
                return
            release = self.firmware_keys_frame.firmware_key_version_dict["firmware"][self.firmware_keys_frame.firmware_option_menu_variable.get()]
            args = ("release", release)
        self.firmware_keys_frame.configure_firmware_key_buttons("disabled")
        self.configure_action_buttons("disabled")
        thread = Thread(target=self.ryujinx.install_firmware_handler, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["firmware_keys", "action"], )).start()

    def install_keys_button_event(self, event=None):
        if event is None or self.firmware_keys_frame.install_keys_button.cget("state") == "disabled":
            return
        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip", ".keys"), title="Custom Key Archive", text="Type path to Key Archive: ")
            path_to_archive = path_to_archive.get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror("Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
            args = ("path", path_to_archive, )
        else:
            if self.firmware_keys_frame.key_option_menu.cget("state") == "disabled":
                messagebox.showerror("Error", "Please ensure that a correct version has been chosen from the menu to the left")
                return
            release = self.firmware_keys_frame.firmware_key_version_dict["keys"][self.firmware_keys_frame.key_option_menu_variable.get()]
            args = ("release", release, )
        self.firmware_keys_frame.configure_firmware_key_buttons("disabled")
        self.configure_action_buttons("disabled")

        thread = Thread(target=self.ryujinx.install_key_handler, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["firmware_keys", "action"],)).start()

    def delete_button_event(self):
        if not os.path.exists(os.path.join(self.settings.ryujinx.install_directory, "publish")):
            messagebox.showinfo("Delete Ryujinx", f"Could not find a Ryujinx installation at {os.path.join(self.settings.ryujinx.install_directory, 'publish')} ")
            return
        if not messagebox.askyesno("Confirmation", f"Are you sure you want to delete the contents of '{self.settings.ryujinx.install_directory}'?"):
            return
        self.configure_action_buttons("disabled")
        thread = Thread(target=self.ryujinx.delete_ryujinx)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["action"],)).start()

    def import_data_button_event(self):
        directory = None 
        folders = None 
        import_option = self.import_optionmenu.get()
        
        if import_option == "Custom...":
            directory, folders = FolderSelector(
                title="Choose directory and folders to import",
                allowed_folders=FOLDERS
            ).get_input()
        else:
            directory = PathDialog(title="Import Directory", text="Enter directory to import from: ", directory=True).get_input()
            if directory and directory[1] is not None:
                directory = directory[1]
            else:
                messagebox.showerror("Error", "The path you have provided is invalid")
                return
        if directory is None:
            return
        self.configure_data_buttons(state="disabled")
        thread_args = (import_option, directory, folders, ) if folders else (import_option, directory,)
        thread = Thread(target=self.ryujinx.import_ryujinx_data, args=thread_args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def export_data_button_event(self):
        directory = PathDialog(title="Export Directory", text="Enter directory to export to: ", directory=True)
        directory = directory.get_input()
        if not all(directory):
            if directory[1] is not None:
                messagebox.showerror("Error", "The path you have provided is invalid")
                return
            return
        directory = directory[1]
        if self.export_optionmenu.get() == "Custom...":
            user_directory, folders = FolderSelector(title="Choose folders to export", predefined_directory=self.settings.ryujinx.user_directory, allowed_folders=FOLDERS).get_input() 
            if user_directory is None or folders is None:
                return 
            args = ("Custom...", directory, folders)
        else:
            args = (self.export_optionmenu.get(), directory,)
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.ryujinx.export_ryujinx_data, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def delete_data_button_event(self):
        if self.delete_optionmenu.get() == "Custom...":
            directory, folders = FolderSelector(title="Delete Directory", predefined_directory=self.settings.ryujinx.user_directory, allowed_folders=FOLDERS).get_input()
            if directory is None or folders is None:
                return 
            args = ("Custom...", folders)
        else:   
            args = (self.delete_optionmenu.get(), )
        if not messagebox.askyesno("Confirmation", "This will delete the data from Ryujinx's directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.ryujinx.delete_ryujinx_data, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def enable_buttons_after_thread(self, thread, buttons):
        thread.join()
        for button in buttons:
            if button == "action":
                self.configure_action_buttons("normal", text="Launch Ryujinx  ", width=200)
            elif button == "firmware_keys":
                self.firmware_keys_frame.configure_firmware_key_buttons("normal")
            elif button == "data":
                self.configure_data_buttons(state="normal")
        self.fetch_versions()

    def fetch_versions(self, installed_only=True):
        self.installed_ryujinx_version = self.metadata.get_installed_version("ryujinx")
        self.installed_firmware_version = self.metadata.get_installed_version("ryujinx_firmware")
        self.installed_key_version = self.metadata.get_installed_version("ryujinx_keys")
        self.update_version_text()

    def update_version_text(self):
        if self.ryujinx_version is not None and self.install_button.cget("state") != "disabled":
            self.install_button.configure(text=f"Install Ryujinx {self.ryujinx_version}")
        if self.installed_ryujinx_version != "":
            if self.launch_button.cget("state") != "disabled":
                self.launch_button.configure(text=f"Launch Ryujinx {self.installed_ryujinx_version}  ")
        else:
            self.launch_button.configure(text="Launch Ryujinx  ")
        self.firmware_keys_frame.installed_firmware_version_label.configure(text=self.installed_firmware_version.replace("Rebootless Update", "RU") if self.installed_firmware_version != "" else "Not Installed")
        self.firmware_keys_frame.installed_key_version_label.configure(text=self.installed_key_version if self.installed_key_version != "" else "Not Installed")
