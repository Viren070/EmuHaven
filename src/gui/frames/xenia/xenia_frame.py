import os
from threading import Thread
from tkinter import messagebox

import customtkinter
from CTkToolTip import CTkToolTip
from PIL import Image

from core.emulators.xenia.runner import Xenia
from gui.frames.emulator_frame import EmulatorFrame
from gui.frames.progress_frame import ProgressFrame
from gui.frames.xenia.xenia_rom_frame import XeniaROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector

FOLDERS = ["cache", "content", "xenia.config.toml"]


class XeniaFrame(EmulatorFrame):
    def __init__(self, parent_frame, settings, metadata, cache):
        super().__init__(parent_frame, settings, metadata)
        self.xenia = Xenia(self, settings, metadata)
        self.cache = cache

        self.add_to_frame()

    def add_to_frame(self):
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                 dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.xenia_banner = customtkinter.CTkImage(Image.open(self.settings.get_image_path("xenia_banner")), size=(276, 129))
        self.xenia_canary_banner = customtkinter.CTkImage(Image.open(self.settings.get_image_path("xenia_canary_banner")), size=(276, 129))

        # create yuzu 'Play' frame and widgets
        self.start_frame = customtkinter.CTkFrame(self, corner_radius=0, border_width=0)
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)

        self.center_frame = customtkinter.CTkFrame(self.start_frame, border_width=0)
        self.center_frame.grid(row=0, column=0, sticky="nsew")
        # self.center_frame.grid_propagate(False)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=2)

        self.selected_channel = customtkinter.StringVar()
        self.version_optionmenu = customtkinter.CTkOptionMenu(self.center_frame, variable=self.selected_channel, command=self.switch_channel, values=["Master", "Canary"])
        self.version_optionmenu.grid(row=0, column=0, padx=10, pady=20, sticky="ne")

        # Image button
        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.xenia_banner)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.actions_frame.grid(row=2, column=0, columnspan=3)

        self.actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_button = customtkinter.CTkButton(self.actions_frame, height=40, width=200, image=self.play_image, text="Launch Xenia  ", command=self.launch_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_button.bind("<Button-1>", command=self.launch_button_event)
        CTkToolTip(self.launch_button, message="Click me to launch Xenia.\nHold shift to toggle the update behaviour.\nIf automatic updates are disabled, shift-clicking will update the emulator\nand otherwise it will skip the update.")

        self.install_button = customtkinter.CTkButton(self.actions_frame, text="Install Xenia", command=self.install_button_event)
        self.install_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.install_button.bind("<Button-1>", command=self.install_button_event)
        CTkToolTip(self.install_button, message="Click me to download and install the latest release of Xenia from the internet\nShift-Click me to install xenia with a custom archive")

        self.delete_button = customtkinter.CTkButton(self.actions_frame, text="Delete Xenia", fg_color="red", hover_color="darkred", command=self.delete_button_event)
        self.delete_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        CTkToolTip(self.delete_button, message="Click me to delete the installation of Xenia at the directory specified in settings.")
        # Early Access Actions Frame

        self.log_frame = customtkinter.CTkFrame(self.center_frame, fg_color='transparent', border_width=0)
        self.log_frame.grid(row=4, column=0, padx=80, sticky="ew")
        self.log_frame.grid_propagate(False)
        self.log_frame.grid_columnconfigure(0, weight=3)
        self.xenia.main_progress_frame = ProgressFrame(self.log_frame)
        # create yuzu 'Manage Data' frame and widgets
        self.manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_data_frame.grid_columnconfigure(0, weight=1)
        self.manage_data_frame.grid_columnconfigure(1, weight=1)
        self.manage_data_frame.grid_rowconfigure(0, weight=1)
        self.manage_data_frame.grid_rowconfigure(1, weight=2)
        self.data_actions_frame = customtkinter.CTkFrame(self.manage_data_frame, height=150)
        self.data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.data_actions_frame.grid_columnconfigure(1, weight=1)

        self.import_data_optionmenu = customtkinter.CTkOptionMenu(self.data_actions_frame, width=300, values=["All Data", "Custom"])
        self.export_data_optionmenu = customtkinter.CTkOptionMenu(self.data_actions_frame, width=300, values=["All Data", "Custom"])
        self.delete_data_optionmenu = customtkinter.CTkOptionMenu(self.data_actions_frame, width=300, values=["All Data", "Custom"])

        self.import_data_button = customtkinter.CTkButton(self.data_actions_frame, text="Import", command=self.import_data_button_event)
        self.export_data_button = customtkinter.CTkButton(self.data_actions_frame, text="Export", command=self.export_data_button_event)
        self.delete_data_button = customtkinter.CTkButton(self.data_actions_frame, text="Delete", command=self.delete_data_button_event, fg_color="red", hover_color="darkred")

        self.import_data_optionmenu.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.import_data_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.export_data_optionmenu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.export_data_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.delete_data_optionmenu.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.delete_data_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.data_log = customtkinter.CTkFrame(self.manage_data_frame)
        self.data_log.grid(row=1, column=0, padx=20, pady=20, columnspan=3, sticky="new")
        self.data_log.grid_columnconfigure(0, weight=1)
        self.data_log.grid_rowconfigure(1, weight=1)
        self.xenia.data_progress_frame = ProgressFrame(self.data_log)
        # create yuzu downloader button, frame and widgets
        self.actions_frame.grid_propagate(False)
        self.selected_channel.set(self.settings.xenia.current_xenia_channel)
        self.switch_channel()

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = XeniaROMFrame(self.manage_roms_frame, self.xenia, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0,  padx=20, pady=20, sticky="nsew")

    def manage_roms_button_event(self):
        self.select_frame_by_name("roms")

    def configure_data_buttons(self, **kwargs):
        self.delete_data_button.configure(**kwargs)
        self.import_data_button.configure(**kwargs)
        self.export_data_button.configure(**kwargs)

    def configure_action_buttons(self, state, **kwargs):
        self.launch_button.configure(state=state, **kwargs)
        self.install_button.configure(state=state)
        self.delete_button.configure(state=state)

    def switch_channel(self, value=None):
        value = self.selected_channel.get()
        self.settings.xenia.current_xenia_channel = value
        self.settings.update_file()
        if value == "Master":
            self.image_button.configure(image=self.xenia_banner)
            self.launch_button.configure(text="Launch Xenia ")
            self.install_button.configure(text="Install Xenia")
            self.delete_button.configure(text="Delete Xenia")
        elif value == "Canary":
            self.image_button.configure(image=self.xenia_canary_banner)
            self.launch_button.configure(text="Launch Xenia Canary")
            self.install_button.configure(text="Install Xenia Canary")
            self.delete_button.configure(text="Delete Xenia Canary")
        self.fetch_versions()

    def launch_button_event(self, event=None):
        if event is None or self.launch_button.cget("state") == "disabled":
            return
        if not os.path.exists(os.path.join(self.settings.xenia.install_directory, self.selected_channel.get(), "xenia.exe" if self.selected_channel.get() == "Master" else "xenia_canary.exe")):
            messagebox.showerror("Error", f"Could not find a Xenia {self.selected_channel.get()} installation at {os.path.join(self.settings.xenia.install_directory, self.selected_channel.get())}.")
            return
        skip_update = True if event.state & 1 else False
        skip_update = not skip_update if self.settings.app.disable_automatic_updates == "True" else skip_update
        self.configure_action_buttons("disabled")
        thread = Thread(target=self.xenia.launch_xenia_handler, args=(self.selected_channel.get(), skip_update))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["action"],)).start()

    def install_button_event(self, event=None):
        if event is None or self.install_button.cget("state") == "disabled":
            return
        if os.path.exists(os.path.join(self.settings.xenia.install_directory, self.selected_channel.get())) and not messagebox.askyesno("Directory Exists", f"The directory {os.path.join(self.settings.xenia.install_directory, self.selected_channel.get())} already exists, do you wish to continue?"):
            return
        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Xenia Archive", text=f"Enter path to Xenia {self.selected_channel.get()} archive: ").get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror("Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
        self.configure_action_buttons("disabled")
        thread = Thread(target=self.xenia.install_xenia_handler, args=(self.selected_channel.get(), path_to_archive))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["action"],)).start()

    def delete_button_event(self, event=None):
        if not os.path.exists(os.path.join(self.settings.xenia.install_directory, self.selected_channel.get())):
            messagebox.showerror("Error", f"Could not find a Xenia {self.selected_channel.get()} installation at {os.path.join(self.settings.xenia.install_directory, self.selected_channel.get())}.")
            return
        if not messagebox.askyesno("Confirmation", "This will delete the Xenia installation. This action cannot be undone, are you sure you wish to continue?"):
            return
        self.configure_action_buttons("disabled")
        thread = Thread(target=self.xenia.delete_xenia, args=(self.selected_channel.get(),))
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["action"],)).start()

    def import_data_button_event(self):
        directory = None
        folders = None
        import_option = self.import_data_optionmenu.get()

        if import_option == "Custom":
            directory, folders = FolderSelector(
                title="Choose directory and folders to import",
                allowed_folders=FOLDERS,
                show_files=True,
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
        thread_args = (import_option, directory, folders, ) if folders else (import_option, directory, )
        thread = Thread(target=self.xenia.import_xenia_data, args=thread_args)
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
        if self.export_data_optionmenu.get() == "Custom":
            user_directory, folders = FolderSelector(title="Choose folders to export", predefined_directory=self.settings.xenia.user_directory, allowed_folders=FOLDERS, show_files=True).get_input()
            if user_directory is None or folders is None:
                return
            args = ("Custom", directory, folders,)
        else:
            args = (self.export_data_optionmenu.get(), directory,)

        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.xenia.export_xenia_data, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def delete_data_button_event(self):
        if self.delete_data_optionmenu.get() == "Custom":
            directory, folders = FolderSelector(title="Delete Directory", predefined_directory=self.settings.xenia.user_directory, allowed_folders=FOLDERS, show_files=True).get_input()
            if directory is None or folders is None:
                return
            thread = Thread(target=self.xenia.delete_xenia_data, args=("Custom", folders,))
        else:
            thread = Thread(target=self.xenia.delete_xenia_data, args=(self.delete_data_optionmenu.get(),))
        if not messagebox.askyesno("Confirmation", "This will delete the data from Yuzu's directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        self.configure_data_buttons(state="disabled")
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def enable_buttons_after_thread(self, thread, buttons):
        thread.join()
        for button in buttons:
            if button == "action":
                self.configure_action_buttons("normal", text="Launch Xenia  ", width=200)
            elif button == "data":
                self.configure_data_buttons(state="normal")
        self.fetch_versions()

    def fetch_versions(self, installed_only=True):
        self.installed_xenia_version = self.metadata.get_installed_version("xenia_master")
        self.installed_xenia_canary_version = self.metadata.get_installed_version("xenia_canary")
        self.update_version_text()

    def update_version_text(self):
        if self.launch_button.cget("state") == "disabled":
            return
        if self.selected_channel.get() == "Master" and self.installed_xenia_version is not None:
            self.launch_button.configure(text=f"Launch Xenia {self.installed_xenia_version.replace("-master", "")}")
        elif self.selected_channel.get() == "Canary":
            pass  # there are no versions for xenia just commit hashes and it is better to not display these
