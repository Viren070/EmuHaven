import os
from threading import Thread

import customtkinter
from CTkToolTip import CTkToolTip
from PIL import Image

from core.emulators.xenia.runner import Xenia
from core.paths import Paths
from gui.libs import messagebox
from core.utils.thread_event_manager import ThreadEventManager
from gui.frames.emulator_frame import EmulatorFrame
from gui.frames.progress_frame import ProgressFrame
from gui.frames.xenia.xenia_rom_frame import XeniaROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector

FOLDERS = ["cache", "content", "xenia.config.toml"]


class XeniaFrame(EmulatorFrame):
    def __init__(self, master, paths, settings, versions, assets, cache, event_manager: ThreadEventManager):
        super().__init__(parent_frame=master, paths=paths, settings=settings, versions=versions, assets=assets)
        self.xenia = Xenia(self, settings, versions)
        self.root = master
        self.paths = paths
        self.cache = cache
        self.event_manager = event_manager
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

        self.selected_channel = customtkinter.StringVar()
        self.version_optionmenu = customtkinter.CTkOptionMenu(self.center_frame, variable=self.selected_channel, command=self.switch_channel, values=["Master", "Canary"])
        self.version_optionmenu.grid(row=0, column=0, padx=10, pady=20, sticky="ne")

        # Image button
        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.assets.xenia_banner)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.actions_frame.grid(row=2, column=0, columnspan=3)

        self.actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_button = customtkinter.CTkButton(self.actions_frame, height=40, width=200, image=self.assets.play_image, text="Launch Xenia  ", command=self.launch_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
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
        self.selected_channel.set(self.settings.xenia.release_channel.title())
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
        self.settings.xenia.release_channel = value.lower()
        self.settings.save()
        if value == "Master":
            self.image_button.configure(image=self.assets.xenia_banner)
            self.launch_button.configure(text="Launch Xenia ")
            self.install_button.configure(text="Install Xenia")
            self.delete_button.configure(text="Delete Xenia")
        elif value == "Canary":
            self.image_button.configure(image=self.assets.xenia_canary_banner)
            self.launch_button.configure(text="Launch Xenia Canary")
            self.install_button.configure(text="Install Xenia Canary")
            self.delete_button.configure(text="Delete Xenia Canary")
        self.fetch_versions()

    def launch_button_event(self, event=None):
        if event is None or self.launch_button.cget("state") == "disabled":
            return
        auto_update = self.settings.auto_emulator_updates if not event.state & 1 else not self.settings.auto_emulator_updates
        self.configure_action_buttons("disabled")
        self.event_manager.add_event(
            event_id="launch_xenia",
            func=self.launch_xenia_handler,
            kwargs={"auto_update": auto_update},
            completion_functions=[lambda: self.enable_buttons(["action"])],
        )

        
    def launch_xenia_handler(self, auto_update):
        if auto_update:
            update = self.install_xenia_handler(update_mode=True)
            if not update.get("status", False):
                return update
        
        launch_result = self.xenia.launch_xenia()
        
        if not launch_result["run_status"]:
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
    
    def install_button_event(self, event=None):
        if event is None or self.install_button.cget("state") == "disabled":
            return
        if (
            (self.settings.xenia.install_directory / self.selected_channel.get()).is_dir() and (
                any((self.settings.xenia.install_directory / self.selected_channel.get()).iterdir()) and (
                    messagebox.askyesno(
                        self.root,
                        "Confirmation", f"An installation of Xenia {self.selected_channel.get()} already exists. Do you want to overwrite it?"
                    ) != "yes"
                )
            )
        ):
            return
        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Xenia Archive", text=f"Enter path to Xenia {self.selected_channel.get()} archive: ").get_input()
            if not all(path_to_archive):
                if path_to_archive[1] is not None:
                    messagebox.showerror(self.root, "Error", "The path you have provided is invalid")
                return
            path_to_archive = path_to_archive[1]
        self.configure_action_buttons("disabled")
        self.event_manager.add_event(
            event_id="install_xenia",
            func=self.install_xenia_handler,
            kwargs={"archive_path": path_to_archive},
            completion_functions=[lambda: self.enable_buttons(["action"])],
            allow_no_output=False,
            event_error_function=lambda: messagebox.showerror(self.root, "Error", "An unexpected error occured while installing Xenia. Please check the logs for more information.")
        )
        
    def install_xenia_handler(self, update_mode=False, archive_path=None):
        custom_install = archive_path is not None
        
        if archive_path is None:
            release_fetch_result = self.xenia.get_xenia_release()
            if not release_fetch_result["status"]:
                return {
                    "message_func": messagebox.showerror,
                    "message_args": (self.root, "Xenia", f"Failed to fetch the {self.settings.xenia.release_channel} latest release of Xenia: {release_fetch_result['message']}")
                }
            
            if update_mode and release_fetch_result["release"]["version"] == self.versions.get_version(f"xenia_{self.settings.xenia.release_channel}"):
                return {
                    "status": True
                }
            
            download_result = self.xenia.download_xenia_release(release_fetch_result["release"]) 
            if not download_result["status"]:
                return ({
                    "message_func": messagebox.showerror,
                    "message_args": (self.root, "Xenia", f"Failed to download the latest {self.settings.xenia.release_channel} release of Xenia: {download_result['message']}")
                })
                
            archive_path = download_result["download_path"]

        extract_result = self.xenia.extract_xenia_release(archive_path)
        if not extract_result["status"]:
            return ({
                "message_func": messagebox.showerror,
                "message_args": (self.root, "xenia", f"Failed to extract the latest release of xenia: {extract_result['message']}")
            })

        self.metadata.set_version(f"xenia_{self.settings.xenia.release_channel}", release_fetch_result["release"]["version"] if not custom_install else "")
        return ({
            "message_func": messagebox.showsuccess,
            "message_args": (self.root, "xenia", f"Successfully installed xenia to {self.settings.xenia.install_directory}"),
            "status": True
        })

    def delete_button_event(self, event=None):
        if not (self.settings.xenia.install_directory / self.selected_channel.get()).is_dir() or not any((self.settings.xenia.install_directory / self.selected_channel.get()).iterdir()):
            messagebox.showerror(self.root, "Error", f"Could not find a Xenia {self.selected_channel.get()} installation at {self.settings.xenia.install_directory}")
            return
        if messagebox.askyesno(self.root, "Confirmation", "This will delete the Xenia installation. This action cannot be undone, are you sure you wish to continue?", icon="warning") != "yes":
            return
        self.configure_action_buttons("disabled")
        self.event_manager.add_event(
            event_id="delete_xenia",
            func=self.delete_xenia_handler,
            allow_no_output=False,
            event_error_function=lambda: messagebox.showerror(self.root, "Error", "An unexpected error occured while deleting Xenia. Please check the logs for more information."),
            completion_functions=[lambda: self.enable_buttons(["action"])],
        )
    def delete_xenia_handler(self):
        delete_result = self.xenia.delete_xenia()
        if not delete_result["status"]:
            return {
                "message_func": messagebox.showerror,
                "message_args": (self.root, "Error", delete_result["message"]),
            }
        return {
            "message_func": messagebox.showsuccess,
            "message_args": (self.root, "Success", delete_result["message"]),
        }
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

    def enable_buttons(self, buttons):
        for button in buttons:
            if button == "action":
                self.configure_action_buttons("normal", text="Launch Xenia  ", width=200)
            elif button == "data":
                self.configure_data_buttons(state="normal")
        self.fetch_versions()

    def fetch_versions(self, installed_only=True):
        self.installed_xenia_version = self.metadata.get_version("xenia")
        self.installed_xenia_canary_version = self.metadata.get_version("xenia_canary")
        self.update_version_text()

    def update_version_text(self):
        if self.launch_button.cget("state") == "disabled":
            return
        if self.selected_channel.get() == "Master" and self.installed_xenia_version is not None:
            self.launch_button.configure(text=f"Launch Xenia {self.installed_xenia_version.replace("-master", "")}")
        elif self.selected_channel.get() == "Canary":
            pass  # there are no versions for xenia just commit hashes and it is better to not display these
