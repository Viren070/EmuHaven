import os
from threading import Thread

import customtkinter
from CTkToolTip import CTkToolTip
from PIL import Image

from core.emulators.yuzu.runner import Yuzu
from core.paths import Paths
from core.utils.thread_event_manager import ThreadEventManager
from gui.frames.emulator_frame import EmulatorFrame
from gui.frames.firmware_keys_frame import FirmwareKeysFrame
from gui.frames.progress_frame import ProgressFrame
from gui.frames.yuzu.yuzu_rom_frame import YuzuROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector
from gui.libs import messagebox


FOLDERS = ["amiibo", "cache", "config", "crash_dumps", "dump", "icons", "keys", "load", "log", "nand", "play_time", "screenshots", "sdmc", "shader", "tas", "sysdata"]


class YuzuFrame(EmulatorFrame):
    def __init__(self, master, paths, settings, versions, assets, cache, event_manager: ThreadEventManager):
        super().__init__(parent_frame=master, paths=paths, settings=settings, versions=versions, assets=assets)
        self.yuzu = Yuzu(self, settings, versions)
        self.cache = cache
        self.paths = paths
        self.versions = versions
        self.event_manager = event_manager
        self.mainline_version = None
        self.early_access_version = None
        self.installed_firmware_version = "Unknown"
        self.installed_key_version = "Unknown"
        self.installed_mainline_version = ""
        self.installed_early_access_version = ""
        self.add_to_frame()

    def add_to_frame(self):

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

        self.mainline_image = self.assets.yuzu_mainline
        self.early_access_image = self.assets.yuzu_early_access
        self.selected_channel = customtkinter.StringVar()
        self.version_optionmenu = customtkinter.CTkOptionMenu(self.center_frame, variable=self.selected_channel, command=self.switch_channel, values=["Mainline", "Early Access"])
        self.version_optionmenu.grid(row=0, column=0, padx=10, pady=20, sticky="ne")

        # Image button
        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.assets.yuzu_mainline)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.actions_frame.grid(row=2, column=0, columnspan=3)

        self.actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_yuzu_button = customtkinter.CTkButton(self.actions_frame, height=40, width=200, image=self.assets.play_image, text="Launch Yuzu  ", command=self.launch_yuzu_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_yuzu_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_yuzu_button.bind("<Button-1>", command=self.launch_yuzu_button_event)
        
        self.install_yuzu_button = customtkinter.CTkButton(self.actions_frame, text="Install Yuzu", command=self.install_yuzu_button_event)
        self.install_yuzu_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.install_yuzu_button.bind("<Button-1>", command=self.install_yuzu_button_event)
        
        self.delete_yuzu_button = customtkinter.CTkButton(self.actions_frame, text="Delete Yuzu", fg_color="red", hover_color="darkred", command=self.delete_yuzu_button_event)
        self.delete_yuzu_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        CTkToolTip(self.delete_yuzu_button, message="Click me to delete the installation of yuzu at the directory specified in settings.")

    
        self.firmware_keys_frame = FirmwareKeysFrame(self.center_frame, frame_obj=self, emulator_obj=self.yuzu)
        self.firmware_keys_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=3)

        self.yuzu_log_frame = customtkinter.CTkFrame(self.center_frame, fg_color='transparent', border_width=0)
        self.yuzu_log_frame.grid(row=4, column=0, padx=80, sticky="ew")
        self.yuzu_log_frame.grid_propagate(False)
        self.yuzu_log_frame.grid_columnconfigure(0, weight=3)
        self.yuzu.main_progress_frame = ProgressFrame(self.yuzu_log_frame)
        # create yuzu 'Manage Data' frame and widgets
        self.manage_data_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_data_frame.grid_columnconfigure(0, weight=1)
        self.manage_data_frame.grid_columnconfigure(1, weight=1)
        self.manage_data_frame.grid_rowconfigure(0, weight=1)
        self.manage_data_frame.grid_rowconfigure(1, weight=2)
        self.yuzu_data_actions_frame = customtkinter.CTkFrame(self.manage_data_frame, height=150)
        self.yuzu_data_actions_frame.grid(row=0, column=0, padx=20, columnspan=3, pady=20, sticky="ew")
        self.yuzu_data_actions_frame.grid_columnconfigure(1, weight=1)

        self.yuzu_import_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data", "Custom..."])
        self.yuzu_export_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data", "Custom..."])
        self.yuzu_delete_optionmenu = customtkinter.CTkOptionMenu(self.yuzu_data_actions_frame, width=300, values=["All Data", "Save Data", "Custom..."])

        self.yuzu_import_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Import", command=self.import_data_button_event)
        self.yuzu_export_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Export", command=self.export_data_button_event)
        self.yuzu_delete_button = customtkinter.CTkButton(self.yuzu_data_actions_frame, text="Delete", command=self.delete_data_button_event, fg_color="red", hover_color="darkred")

        self.yuzu_import_optionmenu.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_import_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.yuzu_export_optionmenu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_export_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.yuzu_delete_optionmenu.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_delete_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.yuzu_data_log = customtkinter.CTkFrame(self.manage_data_frame)
        self.yuzu_data_log.grid(row=1, column=0, padx=20, pady=20, columnspan=3, sticky="new")
        self.yuzu_data_log.grid_columnconfigure(0, weight=1)
        self.yuzu_data_log.grid_rowconfigure(1, weight=1)
        self.yuzu.data_progress_frame = ProgressFrame(self.yuzu_data_log)
        # create yuzu downloader button, frame and widgets

        self.actions_frame.grid_propagate(False)
        self.selected_channel.set(self.settings.yuzu.release_channel.title().replace("_", " "))
        self.switch_channel()

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = YuzuROMFrame(self.manage_roms_frame, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0,  padx=20, pady=20, sticky="nsew")

    def manage_roms_button_event(self):
        self.rom_frame.current_roms_frame.check_titles_db()
        self.select_frame_by_name("roms")

    def configure_buttons(
        self,
        state="disabled",
        launch_yuzu_button_text=None,
        install_yuzu_button_text=None,
        delete_yuzu_button_text=None,
        install_firmware_button_text="Install",
        install_keys_button_text="Install",
    ):
        if launch_yuzu_button_text is None:
            launch_yuzu_button_text = f"Launch Yuzu{" EA" if self.settings.yuzu.release_channel == "early_access" else ""}"
        if install_yuzu_button_text is None:
            install_yuzu_button_text = f"Install Yuzu{" EA" if self.settings.yuzu.release_channel == "early_access" else ""}"
        if delete_yuzu_button_text is None:
            delete_yuzu_button_text = f"Delete Yuzu{" EA" if self.settings.yuzu.release_channel == "early_access" else ""}"

        self.launch_yuzu_button.configure(state=state, text=launch_yuzu_button_text)
        self.install_yuzu_button.configure(state=state, text=install_yuzu_button_text)
        self.delete_yuzu_button.configure(state=state, text=delete_yuzu_button_text)
        self.firmware_keys_frame.install_firmware_button.configure(state=state, text=install_firmware_button_text)
        self.firmware_keys_frame.install_keys_button.configure(state=state, text=install_keys_button_text)
        self.firmware_keys_frame.update_installed_versions()
    
    def switch_channel(self, value=None):
        value = self.selected_channel.get().lower().replace(" ", "_")
        self.settings.yuzu.release_channel = value
        self.settings.save()
        self.image_button.configure(image=self.assets.yuzu_early_access if value == "early_access" else self.assets.yuzu_mainline)
        self.configure_buttons(state="normal")

    def launch_yuzu_button_event(self, event=None):
        if event is None or self.launch_yuzu_button.cget("state") == "disabled":
            return
        if self.launch_yuzu_button.cget("state") == "disabled":
            return
        self.configure_buttons(launch_yuzu_button_text="Launching...")
        self.event_manager.add_event(
            event_id="launch_yuzu",
            func=self.launch_yuzu_handler,
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Launch Yuzu", "An unexpected error has occured while launching Yuzu.\n\nPlease check the logs for more information and report this issue.")],
        )

    def launch_yuzu_handler(self):
        yuzu_path = self.settings.yuzu.install_directory / ("yuzu-windows-msvc-early-access" if self.settings.yuzu.release_channel == "early_access" else "yuzu-windows-msvc") / "yuzu.exe"
        if not yuzu_path.is_file():
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Launch Yuzu", f"Installation of yuzu {self.settings.yuzu.release_channel.replace('_', ' ').title()} not found.\nYou may use a ZIP archive to install Yuzu by using the Install button."),
                }
            }

        run_status = self.yuzu.launch_yuzu()
        if not run_status["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Launch Yuzu", run_status["message"]),
                }
            }
        if run_status["error_encountered"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Launch Yuzu", "It seems that yuzu has encountered an error."),
                }
            }

        return {}

    def install_yuzu_button_event(self, event=None):
        if event is None or self.install_yuzu_button.cget("state") == "disabled":
            return
        yuzu_path = self.settings.yuzu.install_directory / ("yuzu-windows-msvc-early-access" if self.settings.yuzu.release_channel == "early_access" else "yuzu-windows-msvc")
        if yuzu_path.is_dir() and any(yuzu_path.iterdir()) and messagebox.askyesno(self.winfo_toplevel(), "Directory Exists", "The directory already exists. Are you sure you want to overwrite the contents inside?") != "yes":
            return
        
        path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Yuzu Archive", text="Enter path to yuzu archive: ")
        path_to_archive = path_to_archive.get_input()
        if not path_to_archive["status"]:
            if path_to_archive["cancelled"]:
                return
            messagebox.showerror(self.winfo_toplevel(), "Install Yuzu", path_to_archive["message"])
        path_to_archive = path_to_archive["path"]

        self.configure_buttons(install_yuzu_button_text="Installing...")
        self.event_manager.add_event(
            event_id="install_yuzu",
            func=self.install_yuzu_handler,
            kwargs={"archive_path": path_to_archive},
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Install Yuzu", "An unexpected error has occured while installing Yuzu.\n\nPlease check the logs for more information and report this issue.")],
        )

    def install_yuzu_handler(self, archive_path):
        install_status = self.yuzu.install_yuzu(archive_path)
        if not install_status["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Install Yuzu", install_status["message"]),
                }
            }
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Install Yuzu", "Yuzu has been installed successfully."),
            }
        }

    def delete_yuzu_button_event(self):
        yuzu_path = self.settings.yuzu.install_directory / ("yuzu-windows-msvc-early-access" if self.settings.yuzu.release_channel == "early_access" else "yuzu-windows-msvc")
        if messagebox.askyesno(self.winfo_toplevel(), "Delete Yuzu", f"Are you sure you want to delete yuzu and its contents from '{yuzu_path}'?") != "yes":
            return
        self.configure_buttons(delete_yuzu_button_text="Deleting...")
        self.event_manager.add_event(
            event_id="delete_yuzu",
            func=self.delete_yuzu_handler,
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Delete Yuzu", "An unexpected error has occured while deleting Yuzu.\n\nPlease check the logs for more information and report this issue either on the GitHub page or Discord server.")],
        )

    def delete_yuzu_handler(self):
        delete_result = self.yuzu.delete_yuzu()
        if not delete_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Delete Yuzu", delete_result["message"]),
                }
            }

        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Delete Yuzu", "Yuzu has been deleted successfully."),
            }
        }

    def import_data_button_event(self):
        directory = None
        folders = None
        import_option = self.yuzu_import_optionmenu.get()

        if import_option == "Custom...":
            directory, folders = FolderSelector(
                title="Choose directory and folders to import",
                allowed_folders=FOLDERS
            ).get_input()
        else:
            directory = PathDialog(title="Import Directory", text="Enter directory to import from: ", directory=True).get_input()
            directory = directory.get_input()
            if not directory["status"]:
                if directory["cancelled"]:
                    return
                messagebox.showerror(self.winfo_toplevel(), "Import Yuzu Data", directory["message"])
            directory = directory["path"]

        if directory is None:
            return

        self.configure_data_buttons(state="disabled")
        thread_args = (import_option, directory, folders, ) if folders else (import_option, directory, )
        thread = Thread(target=self.yuzu.import_yuzu_data, args=thread_args)
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
        if self.yuzu_export_optionmenu.get() == "Custom...":
            user_directory, folders = FolderSelector(title="Choose folders to export", predefined_directory=self.settings.yuzu.user_directory, allowed_folders=FOLDERS).get_input()
            if user_directory is None or folders is None:
                return
            args = ("Custom...", directory, folders,)
        else:
            args = (self.yuzu_export_optionmenu.get(), directory,)

        self.configure_data_buttons(state="disabled")
        thread = Thread(target=self.yuzu.export_yuzu_data, args=args)
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    def delete_data_button_event(self):
        if self.yuzu_delete_optionmenu.get() == "Custom...":
            directory, folders = FolderSelector(title="Delete Directory", predefined_directory=self.settings.yuzu.user_directory, allowed_folders=FOLDERS).get_input()
            if directory is None or folders is None:
                return
            thread = Thread(target=self.yuzu.delete_yuzu_data, args=("Custom...", folders,))
        else:
            thread = Thread(target=self.yuzu.delete_yuzu_data, args=(self.yuzu_delete_optionmenu.get(),))
        if not messagebox.askyesno("Confirmation", "This will delete the data from Yuzu's directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        self.configure_data_buttons(state="disabled")
        thread.start()
        Thread(target=self.enable_buttons_after_thread, args=(thread, ["data"],)).start()

    