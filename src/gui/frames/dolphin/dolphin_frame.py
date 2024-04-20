import os
from threading import Thread
from tkinter import messagebox

import customtkinter
from CTkToolTip import CTkToolTip
from PIL import Image

from emulators.dolphin import Dolphin
from gui.frames.dolphin.dolphin_rom_frame import DolphinROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector
from gui.frames.progress_frame import ProgressFrame
from gui.frames.emulator_frame import EmulatorFrame

DOLPHIN_FOLDERS = ["Backup", "Cache", "Config", "Dump", "GameSettings", "GBA", "GC", "Load", "Logs", "Maps", "ResourcePacks", "SavedAssembly", "ScreenShots", "Shaders", "StateSaves", "Styles", "Themes", "Wii"]


class DolphinFrame(EmulatorFrame):
    def __init__(self, parent_frame, settings, metadata, cache):
        super().__init__(parent_frame, settings, metadata)
        self.dolphin = Dolphin(self, settings, metadata)
        self.cache = cache
        self.dolphin_version = None
        self.installed_dolphin_version = None
        self.add_to_frame()

    def add_to_frame(self):
        self.dolphin_banner = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("dolphin_banner_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("dolphin_banner_dark")), size=(276, 129))
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                 dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.start_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)

        self.center_frame = customtkinter.CTkFrame(self.start_frame)
        self.center_frame.grid(row=0, column=0, sticky="nsew")
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=2)

        self.selected_channel = customtkinter.StringVar()
        self.selected_channel.set(self.settings.dolphin.current_channel.title())
        self.channel_optionmenu = customtkinter.CTkOptionMenu(self.center_frame, variable=self.selected_channel, command=self.switch_channel, values=["Beta", "Development"])
        self.channel_optionmenu.grid(row=0, column=0, padx=10, pady=20, sticky="ne")

        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.dolphin_banner)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.dolphin_actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.dolphin_actions_frame.grid(row=1, column=0, columnspan=3)

        self.dolphin_actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.dolphin_actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.dolphin_actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, width=250, height=40, text="Launch Dolphin  ", image=self.play_image, font=customtkinter.CTkFont(size=15, weight="bold"), command=self.launch_dolphin_button_event)
        self.launch_dolphin_button.grid(row=0, column=1, padx=30, pady=15, sticky="nsew")
        self.launch_dolphin_button.bind("<Button-1>", command=self.launch_dolphin_button_event)
        CTkToolTip(self.launch_dolphin_button, message="Click me to launch Dolphin.\nHold shift to toggle the update behaviour.\nIf automatic updates are disabled, shift-clicking will update the emulator\nand otherwise it will skip the update.")

        self.install_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Install Dolphin", command=self.install_dolphin_button_event)
        self.install_dolphin_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.install_dolphin_button.bind("<Button-1>", command=self.install_dolphin_button_event)
        CTkToolTip(self.install_dolphin_button, message="Click me to download and install the latest beta release of Dolphin\nShift-Click me to use a custom archive of Dolphin to install it.")

        self.delete_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Delete Dolphin", fg_color="red", hover_color="darkred", command=self.delete_dolphin_button_event)
        self.delete_dolphin_button.grid(row=0, column=2, padx=10, sticky="ew", pady=5)
        CTkToolTip(self.delete_dolphin_button, message="Click me to delete the installation of Dolphin at the specified path in the settings menu.")

        self.dolphin_log_frame = customtkinter.CTkFrame(self.center_frame, border_width=0, fg_color='transparent')
        self.dolphin_log_frame.grid(row=3, column=0, padx=80, sticky="ew")
        self.dolphin_log_frame.grid_propagate(False)
        self.dolphin_log_frame.grid_columnconfigure(0, weight=3)
        self.dolphin.main_progress_frame = ProgressFrame(self.dolphin_log_frame)

        self.manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_data_frame.grid_columnconfigure(0, weight=1)
        self.manage_data_frame.grid_columnconfigure(1, weight=1)
        self.manage_data_frame.grid_rowconfigure(0, weight=1)
        self.manage_data_frame.grid_rowconfigure(1, weight=2)
        self.dolphin_data_actions_frame = customtkinter.CTkFrame(self.manage_data_frame, height=150)
        self.dolphin_data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.dolphin_data_actions_frame.grid_columnconfigure(1, weight=1)

        self.dolphin_import_optionmenu = customtkinter.CTkOptionMenu(self.dolphin_data_actions_frame, width=300, values=["All Data", "Custom"])
        self.dolphin_export_optionmenu = customtkinter.CTkOptionMenu(self.dolphin_data_actions_frame, width=300, values=["All Data", "Custom"])
        self.dolphin_delete_optionmenu = customtkinter.CTkOptionMenu(self.dolphin_data_actions_frame, width=300, values=["All Data", "Custom"])

        self.dolphin_import_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Import", command=self.import_data_button_event)
        self.dolphin_export_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Export", command=self.export_data_button_event)
        self.dolphin_delete_button = customtkinter.CTkButton(self.dolphin_data_actions_frame, text="Delete", command=self.delete_data_button_event,  fg_color="red", hover_color="darkred")

        self.dolphin_import_optionmenu.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_import_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.dolphin_export_optionmenu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_export_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.dolphin_delete_optionmenu.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_delete_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.dolphin_data_log = customtkinter.CTkFrame(self.manage_data_frame)
        self.dolphin_data_log.grid(row=1, column=0, padx=20, pady=20, columnspan=3, sticky="new")
        self.dolphin_data_log.grid_columnconfigure(0, weight=1)
        self.dolphin_data_log.grid_rowconfigure(1, weight=1)
        self.dolphin.data_progress_frame = ProgressFrame(self.dolphin_data_log)

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = DolphinROMFrame(self.manage_roms_frame, self.dolphin, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def switch_channel(self, *args):
        value = self.selected_channel.get()
        self.settings.dolphin.current_channel = value.lower()
        self.settings.update_file()

    def configure_data_buttons(self, **kwargs):
        self.dolphin_delete_button.configure(**kwargs)
        self.dolphin_import_button.configure(**kwargs)
        self.dolphin_export_button.configure(**kwargs)

    def configure_buttons(self, state, **kwargs):
        self.launch_dolphin_button.configure(state=state, **kwargs)
        self.install_dolphin_button.configure(state=state)
        self.delete_dolphin_button.configure(state=state)

    def launch_dolphin_button_event(self, event=None):
        if event is None or self.launch_dolphin_button.cget("state") == "disabled":
            return
        if not os.path.exists(os.path.join(self.settings.dolphin.install_directory, "Dolphin.exe")):
            messagebox.showerror("Dolphin", f"Installation of Dolphin not found at {os.path.join(self.settings.dolphin.install_directory, 'Dolphin.exe')}")
            return
        self.configure_buttons("disabled", text="Launching...")
        shift_clicked = True if event.state & 1 else False
        shift_clicked = not shift_clicked if self.settings.app.disable_automatic_updates == "True" else shift_clicked
        thread = Thread(target=self.dolphin.launch_dolphin_handler, args=(self.selected_channel.get().lower(), shift_clicked,))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["main"])).start()

    def install_dolphin_button_event(self, event=None):
        if event is None or self.install_dolphin_button.cget("state") == "disabled":
            return
        if os.path.exists(self.settings.dolphin.install_directory) and not messagebox.askyesno("Directory Exists", "The directory already exists. Are you sure you want to overwrite the contents inside?"):
            return

        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip", ".7z", ), title="Custom Dolphin Archive", text="Type path to Dolphin Archive: ")
            path_to_archive = path_to_archive.get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror("Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
            args = (None, path_to_archive, )
        else:
            args = (self.selected_channel.get().lower(), None)
        self.configure_buttons("disabled")
        thread = Thread(target=self.dolphin.install_dolphin_handler, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["main"], )).start()

    def delete_dolphin_button_event(self):
        if not os.path.exists(self.settings.dolphin.install_directory):
            messagebox.showinfo("Delete Dolphin", f"The dolphin installation directory does not exist:\n {self.settings.dolphin.install_directory}")
            return
        if not messagebox.askyesno("Confirmation", f"Are you sure you want to delete the contents of `{self.settings.dolphin.install_directory}`"):
            return
        self.configure_buttons("disabled")
        thread = Thread(target=self.dolphin.delete_dolphin)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["main"], )).start()

    def import_data_button_event(self):
        directory = None
        folders = None
        import_option = self.dolphin_import_optionmenu.get()

        if import_option == "Custom":
            directory, folders = FolderSelector(
                title="Choose directory and folders to import",
                allowed_folders=DOLPHIN_FOLDERS
            ).get_input()
        else:
            directory = PathDialog(title="Import Directory", text="Enter directory to import from: ", directory=True).get_input()
            if directory and directory[1] is not None:
                directory = directory[1]
            else:
                messagebox.showerror("Error", "The path you have provided is invalid")
                return
        self.configure_data_buttons(state="disabled")
        thread_args = (import_option, directory, folders, ) if folders else (import_option, directory, )
        thread = Thread(target=self.dolphin.import_dolphin_data, args=thread_args)
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
        if self.dolphin_export_optionmenu.get() == "Custom":
            user_directory, folders = FolderSelector(title="Choose folders to export", predefined_directory=self.settings.dolphin.user_directory, allowed_folders=DOLPHIN_FOLDERS).get_input()
            if user_directory is None or folders is None:
                return
            args = ("Custom", directory, folders, )
        else:
            args = (self.dolphin_export_optionmenu.get(), directory, )
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.dolphin.export_dolphin_data, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def delete_data_button_event(self):
        if self.dolphin_delete_optionmenu.get() == "Custom":
            directory, folders = FolderSelector(title="Choose folders to delete", predefined_directory=self.settings.dolphin.user_directory, allowed_folders=DOLPHIN_FOLDERS).get_input()
            if directory is None or folders is None:
                return
            args = ("Custom", folders)
        else:
            args = (self.dolphin_delete_optionmenu.get(), )
        if not messagebox.askyesno("Confirmation", "This will delete the data from Dolphin's directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.dolphin.delete_dolphin_data, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def enable_buttons_after_thread(self, thread, buttons):
        if not isinstance(buttons, list):
            raise TypeError("Expected list of button types")
        thread.join()
        for button in buttons:
            if button == "main":
                self.configure_buttons("normal", text="Launch Dolphin  ", width=230)
            elif button == "data":
                self.configure_data_buttons(state="normal")
        self.fetch_versions()

    def fetch_versions(self, installed_only=True):
        if not installed_only:
            pass
        self.installed_dolphin_version = self.metadata.get_installed_version("dolphin")
        self.update_version_text()

    def update_version_text(self):

        if self.dolphin_version is not None and self.install_dolphin_button.cget("state") != "disabled":
            self.install_dolphin_button.configure(text=f"Install Dolphin {self.dolphin_version}")
        if self.installed_dolphin_version != "":
            if self.launch_dolphin_button.cget("state") != "disabled":
                self.launch_dolphin_button.configure(text=f"Launch Dolphin {self.installed_dolphin_version}  ")
        else:
            self.launch_dolphin_button.configure(text="Launch Dolphin  ")
