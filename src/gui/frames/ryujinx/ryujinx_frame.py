from threading import Thread

import customtkinter
from CTkToolTip import CTkToolTip

from core.emulators.ryujinx.runner import Ryujinx
from gui.frames.emulator_frame import EmulatorFrame
from gui.frames.firmware_keys_frame import FirmwareKeysFrame
from gui.libs import messagebox
from gui.frames.ryujinx.ryujinx_rom_frame import RyujinxROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector

FOLDERS = ["bis", "games", "mods", "profiles", "sdcard", "system"]


class RyujinxFrame(EmulatorFrame):
    def __init__(self, master, paths, settings, versions, assets, cache, event_manager):
        super().__init__(parent_frame=master, paths=paths, settings=settings, versions=versions, assets=assets)
        self.ryujinx = Ryujinx(self, settings, versions)
        self.root = master
        self.cache = cache
        self.ryujinx_version = None
        self.paths = paths
        self.event_manager = event_manager
        self.installed_firmware_version = "Unknown"
        self.installed_key_version = "Unknown"
        self.installed_ryujinx_version = ""
        self.add_to_frame()

    def add_to_frame(self):
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
        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.assets.ryujinx_banner)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.actions_frame.grid(row=2, column=0, columnspan=3)

        self.actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_button = customtkinter.CTkButton(self.actions_frame, height=40, width=225, image=self.assets.play_image, text="Launch Ryujinx  ", command=self.launch_ryujinx_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_button.bind("<Button-1>", command=self.launch_ryujinx_button_event)
        CTkToolTip(self.launch_button, message="Click me to launch Ryujinx.\nHold shift to toggle the update behaviour.\nIf automatic updates are disabled, shift-clicking will update the emulator\nand otherwise it will skip the update.")
        self.install_button = customtkinter.CTkButton(self.actions_frame, text="Install Ryujinx", command=self.install_ryujinx_button_event)
        self.install_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.install_button.bind("<Button-1>", command=self.install_ryujinx_button_event)
        CTkToolTip(self.install_button, message="Click me to download and install the latest release of Ryujinx from the internet\nShift-Click me to install Ryujinx with a custom archive")

        self.delete_button = customtkinter.CTkButton(self.actions_frame, text="Delete Ryujinx", fg_color="red", hover_color="darkred", command=self.delete_ryujinx_button_event)
        self.delete_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        CTkToolTip(self.delete_button, message="Click me to delete the installation of Ryujinx at the directory specified in settings.")

        self.firmware_keys_frame = FirmwareKeysFrame(self.center_frame, self)
        self.firmware_keys_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=3)

        self.log_frame = customtkinter.CTkFrame(self.center_frame, fg_color='transparent', border_width=0)
        self.log_frame.grid(row=4, column=0, padx=80, sticky="ew")
        self.log_frame.grid_propagate(False)
        self.log_frame.grid_columnconfigure(0, weight=3)
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
        # create ryujinx downloader button, frame and widgets

        self.actions_frame.grid_propagate(False)

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = RyujinxROMFrame(self.manage_roms_frame, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0,  padx=20, pady=20, sticky="nsew")

    def manage_roms_button_event(self):
        self.rom_frame.current_roms_frame.check_titles_db()
        self.select_frame_by_name("roms")

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

    def launch_ryujinx_button_event(self, event=None):
        if event is None or self.launch_button.cget("state") == "disabled":
            return
        auto_update = self.settings.auto_emulator_updates if not event.state & 1 else not self.settings.auto_emulator_updates
        self.configure_action_buttons("disabled")
        self.event_manager.add_event(
            event_id="launch_ryujinx",
            func=self.launch_ryujinx_handler,
            kwargs={"auto_update": auto_update},
            completion_functions=[lambda: self.enable_buttons(["action"])],
        )

    def launch_ryujinx_handler(self, auto_update):
        if auto_update:
            update = self.install_ryujinx_handler(update_mode=True)
            if not update.get("status", False):
                return update
        
        launch_result = self.ryujinx.launch_ryujinx()
        
        if not launch_result["status"]:
            return {
                "message_func": messagebox.showerror,
                "message_args": (self.root, "Error", launch_result["message"]),
            }
        if launch_result["error_encountered"]:
            return {
                "message_func": messagebox.showerror,
                "message_args": (self.root, "Error", launch_result["message"]),
            }
        
        return {}
    
    def install_ryujinx_button_event(self, event=None):
        if event is None or self.install_button.cget("state") == "disabled":
            return
        if (
            (self.settings.ryujinx.install_directory / "publish").is_dir() and (
                any((self.settings.ryujinx.install_directory / "publish").iterdir()) and (
                    messagebox.askyesno(
                        self.root,
                        "Confirmation", "An installation of Ryujinx already exists. Do you want to overwrite it?"
                    ) != "yes"
                )
            )
        ):
            return
        path_to_archive = None
        
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Ryujinx Archive", text="Enter path to Ryujinx archive: ").get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror(self.root, "Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
        
        self.configure_action_buttons("disabled")
        self.event_manager.add_event(
            event_id="install_ryujinx",
            func=self.install_ryujinx_handler,
            kwargs={"archive_path": path_to_archive},
            completion_functions=[lambda: self.enable_buttons(["action"])],
            allow_no_output=False,
            event_error_function=lambda: messagebox.showerror(self.root, "Error", "An unexpected error occured while installing Ryujinx. Please check the logs for more information.")
        )
        
    def install_ryujinx_handler(self, update_mode=False, archive_path=None):
        custom_install = archive_path is not None
        
        if archive_path is None:
            release_fetch_result = self.ryujinx.get_release()
            if not release_fetch_result["status"]:
                return {
                    "message_func": messagebox.showerror,
                    "message_args": (self.root, "Ryujinx", f"Failed to fetch the latest release of Ryujinx: {release_fetch_result['message']}")
                }
            
            if update_mode and release_fetch_result["release"]["version"] == self.versions.get_version("ryujinx"):
                return {
                    "status": True
                }
            
            download_result = self.ryujinx.download_release(release_fetch_result["release"]) 
            if not download_result["status"]:
                return ({
                    "message_func": messagebox.showerror,
                    "message_args": (self.root, "Ryujinx", f"Failed to download the latest release of Ryujinx: {download_result['message']}")
                })
                
            archive_path = download_result["download_path"]

        extract_result = self.ryujinx.extract_release(archive_path)
        if not extract_result["status"]:
            return ({
                "message_func": messagebox.showerror,
                "message_args": (self.root, "ryujinx", f"Failed to extract the latest release of ryujinx: {extract_result['message']}")
            })

        self.metadata.set_version("ryujinx", release_fetch_result["release"]["version"] if not custom_install else "")
        return ({
            "message_func": messagebox.showsuccess,
            "message_args": (self.root, "ryujinx", f"Successfully installed ryujinx to {self.settings.ryujinx.install_directory}"),
            "status": True
        })

    def delete_ryujinx_button_event(self, event=None):
        if not (self.settings.ryujinx.install_directory / "publish").is_dir() or not any((self.settings.ryujinx.install_directory / "publish").iterdir()):
            messagebox.showerror(self.root, "Error", f"Could not find a Ryujinx installation at {self.settings.ryujinx.install_directory}")
            return
        if messagebox.askyesno(self.root, "Confirmation", "This will delete the Ryujinx installation. This action cannot be undone, are you sure you wish to continue?", icon="warning") != "yes":
            return
        self.configure_action_buttons("disabled")
        self.event_manager.add_event(
            event_id="delete_ryujinx",
            func=self.delete_ryujinx_handler,
            allow_no_output=False,
            event_error_function=lambda: messagebox.showerror(self.root, "Error", "An unexpected error occured while deleting Ryujinx. Please check the logs for more information."),
            completion_functions=[lambda: self.enable_buttons(["action"])],
        )
    def delete_ryujinx_handler(self):
        delete_result = self.ryujinx.delete_ryujinx()
        if not delete_result["status"]:
            return {
                "message_func": messagebox.showerror,
                "message_args": (self.root, "Error", delete_result["message"]),
            }
        return {
            "message_func": messagebox.showsuccess,
            "message_args": (self.root, "Success", delete_result["message"]),
        }

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

    def enable_buttons(self, buttons):
        for button in buttons:
            if button == "action":
                self.configure_action_buttons("normal", text="Launch Ryujinx  ", width=200)
            elif button == "firmware_keys":
                self.firmware_keys_frame.configure_firmware_key_buttons("normal")
            elif button == "data":
                self.configure_data_buttons(state="normal")
        self.fetch_versions()

    def fetch_versions(self, installed_only=True):
        self.installed_ryujinx_version = self.metadata.get_version("ryujinx")
        self.installed_firmware_version = self.metadata.get_version("ryujinx_firmware")
        self.installed_key_version = self.metadata.get_version("ryujinx_keys")
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
