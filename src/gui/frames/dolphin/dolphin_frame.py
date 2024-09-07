import os
from threading import Thread

import customtkinter
from CTkToolTip import CTkToolTip

from core.emulators.dolphin.runner import Dolphin
from gui.frames.dolphin.dolphin_rom_frame import DolphinROMFrame
from gui.windows.path_dialog import PathDialog
from gui.windows.folder_selector import FolderSelector
from gui.frames.emulator_frame import EmulatorFrame
from gui.libs import messagebox
from gui.progress_handler import ProgressHandler
from core.paths import Paths
from core import constants
from core.utils.thread_event_manager import ThreadEventManager



class DolphinFrame(EmulatorFrame):
    def __init__(self, master, paths, settings, versions, assets, cache, event_manager: ThreadEventManager):
        super().__init__(parent_frame=master, paths=paths, settings=settings, versions=versions, assets=assets)
        self.dolphin = Dolphin(settings, versions)
        self.paths = paths
        self.event_manager = event_manager
        self.cache = cache
        self.dolphin_version = None
        self.installed_dolphin_version = None
        self.add_to_frame()

    def add_to_frame(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.start_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)

        self.center_frame = customtkinter.CTkFrame(self.start_frame, corner_radius=0)
        self.center_frame.grid(row=0, column=0, sticky="nsew")
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=2)

        self.selected_channel = customtkinter.StringVar()
        self.selected_channel.set(self.settings.dolphin.release_channel.title())
        self.channel_optionmenu = customtkinter.CTkOptionMenu(self.center_frame, variable=self.selected_channel, command=self.switch_channel, values=["Release", "Development"])
        self.channel_optionmenu.grid(row=0, column=0, padx=10, pady=20, sticky="ne")

        self.image_button = customtkinter.CTkButton(self.center_frame, text="", fg_color='transparent', hover=False, bg_color='transparent', border_width=0, image=self.assets.dolphin_banner)
        self.image_button.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=20)

        self.dolphin_actions_frame = customtkinter.CTkFrame(self.center_frame)
        self.dolphin_actions_frame.grid(row=1, column=0, columnspan=3)

        self.dolphin_actions_frame.grid_columnconfigure(0, weight=1)  # Stretch horizontally
        self.dolphin_actions_frame.grid_columnconfigure(1, weight=1)  # Stretch horizontally
        self.dolphin_actions_frame.grid_columnconfigure(2, weight=1)  # Stretch horizontally

        self.launch_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, width=250, height=40, text="Launch Dolphin  ", image=self.assets.play_image, font=customtkinter.CTkFont(size=15, weight="bold"), command=self.launch_dolphin_button_event)
        self.launch_dolphin_button.grid(row=0, column=1, padx=30, pady=15, sticky="nsew")
        self.launch_dolphin_button.bind("<Button-1>", command=self.launch_dolphin_button_event)
        CTkToolTip(self.launch_dolphin_button, message="Click me to launch Dolphin.\nHold shift to toggle the update behaviour.\nIf automatic updates are disabled, shift-clicking will update the emulator\nand otherwise it will skip the update.")

        self.install_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Install Dolphin", command=self.install_dolphin_button_event)
        self.install_dolphin_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.install_dolphin_button.bind("<Button-1>", command=self.install_dolphin_button_event)
        CTkToolTip(self.install_dolphin_button, message="Click me to download and install the latest release of Dolphin\nShift-Click me to use a custom archive of Dolphin to install it.")

        self.delete_dolphin_button = customtkinter.CTkButton(self.dolphin_actions_frame, text="Delete Dolphin", fg_color="red", hover_color="darkred", command=self.delete_dolphin_button_event)
        self.delete_dolphin_button.grid(row=0, column=2, padx=10, sticky="ew", pady=5)
        CTkToolTip(self.delete_dolphin_button, message="Click me to delete the installation of Dolphin at the specified path in the settings menu.")

        self.dolphin_log_frame = customtkinter.CTkFrame(self.center_frame, border_width=0, fg_color='transparent')
        self.dolphin_log_frame.grid(row=3, column=0, padx=80, sticky="ew")
        self.dolphin_log_frame.grid_propagate(False)
        self.dolphin_log_frame.grid_columnconfigure(0, weight=3)
        self.main_progress_frame = ProgressHandler(self.dolphin_log_frame)
        
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
        self.data_progress_handler = ProgressHandler(self.dolphin_data_log)

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = DolphinROMFrame(self.manage_roms_frame, self.dolphin, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def switch_channel(self, *args):
        value = self.selected_channel.get()
        self.settings.dolphin.release_channel = value.lower()
        self.settings.save()

    def configure_buttons(
        self,
        state="disabled",
        launch_dolphin_button_text="Launch Dolphin",
        install_dolphin_button_text="Install Dolphin",
        delete_dolphin_button_text="Delete Dolphin",
    ):
        self.launch_dolphin_button.configure(state=state, text=launch_dolphin_button_text)
        self.install_dolphin_button.configure(state=state, text=install_dolphin_button_text)
        self.delete_dolphin_button.configure(state=state, text=delete_dolphin_button_text)
        
    def configure_data_buttons(self, state="disabled", import_text="Import", export_text="Export", delete_text="Delete"):
        self.dolphin_import_button.configure(state=state, text=import_text)
        self.dolphin_export_button.configure(state=state, text=export_text)
        self.dolphin_delete_button.configure(state=state, text=delete_text)

    
    def launch_dolphin_button_event(self, event=None):
        if event is None or self.launch_dolphin_button.cget("state") == "disabled":
            return
        self.configure_buttons(launch_dolphin_button_text="Launching...")
        update_mode = not self.settings.auto_emulator_updates if event.state & 1 else self.settings.auto_emulator_updates
        self.event_manager.add_event(
            "launch_dolphin",
            self.launch_dolphin_handler,
            kwargs={"update_mode": update_mode}, 
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occurred while launching Dolphin.\nPlease check the logs for more information and report this issue.")]
            )
        
    def launch_dolphin_handler(self, update_mode):
        if update_mode:
            self.configure_buttons(launch_dolphin_button_text="Checking for updates...")
            update_result = self.install_dolphin_handler(update_mode=True)
            if not update_result.get("status", False):
                return update_result
        self.configure_buttons(launch_dolphin_button_text="Launched!")
        status = self.dolphin.launch_dolphin()
        
        if not status["run_status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"Failed to launch Dolphin: {status['message']}"),
                }
            }

        if status["error_encountered"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"An error was encountered while launching/running Dolphin: {status['message']}"),
                }
            }

        return {}

    def install_dolphin_button_event(self, event=None):
        if event is None or self.install_dolphin_button.cget("state") == "disabled":
            return
        
        if self.settings.dolphin.install_directory.is_dir() and any(self.settings.dolphin.install_directory.iterdir()):
            if messagebox.askyesno(self.winfo_toplevel(), "Directory Exists", "The directory already exists. Are you sure you want to overwrite the contents inside?") != "yes":
                return
            # Delete the contents of the directory
            delete_result = self.dolphin.delete_dolphin()
            if not delete_result["status"]:
                messagebox.showerror(self.winfo_toplevel(), "Error", f"Failed to delete the contents of the directory: {delete_result['message']}")
                return

        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip", ".7z", ), title="Custom Dolphin Archive", text="Type path to Dolphin Archive: ")
            path_to_archive = path_to_archive.get_input()
            if not path_to_archive["status"]:
                if path_to_archive["cancelled"]:
                    return
                messagebox.showerror(self.winfo_toplevel(), "Install Dolphin", path_to_archive["message"])
                return
            path_to_archive = path_to_archive["path"]

        self.configure_buttons(install_dolphin_button_text="Installing...")
        
        self.event_manager.add_event(
            "install_dolphin", 
            self.install_dolphin_handler, 
            kwargs={"archive_path": path_to_archive}, 
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occurred while installing Dolphin.\nPlease check the logs for more information and report this issue.")]
            )
        
        
    def install_dolphin_handler(self, archive_path=None, update_mode=False):
        
        custom_install = archive_path is not None
        
        if archive_path is None:
            release_fetch_result = self.dolphin.get_dolphin_release()
            if not release_fetch_result["status"]:
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self.winfo_toplevel(), "Dolphin", f"Failed to fetch the latest release of Dolphin: {release_fetch_result['message']}"),
                    }
                }

            if update_mode:
                if release_fetch_result["release"]["version"] == self.dolphin.get_installed_version():
                    return {
                        "status": True,
                    }
                self.configure_buttons(launch_dolphin_button_text="Updating...")
            
            self.main_progress_frame.start_operation(title="Install Dolphin", total_units=0, units=" MiB", status="Downloading...")
            download_result = self.dolphin.download_release(release_fetch_result["release"], progress_handler=self.main_progress_frame) 
            if not download_result["status"]:
                if "cancelled" in download_result["message"]:
                    return {
                        "message": {
                            "function": messagebox.showinfo,
                            "arguments": (self.winfo_toplevel(), "Dolphin", "The download was cancelled."),
                        }
                    }
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self.winfo_toplevel(), "Dolphin", f"Failed to download the latest release of Dolphin:\n\n{download_result['message']}"),
                    }
                }
                
            archive_path = download_result["download_path"]

        self.main_progress_frame.start_operation(title="Install Dolphin", total_units=1, units=" Files", status="Extracting...")
        self.main_progress_frame.set_cancel_button_state(state="disabled")
        extract_result = self.dolphin.extract_release(archive_path, progress_handler=self.main_progress_frame)
        if not extract_result["status"]:
            if "cancelled" in extract_result["message"]:
                return {
                    "message": {
                        "function": messagebox.showinfo,
                        "arguments": (self.winfo_toplevel(), "Dolphin", "The extraction was cancelled."),
                    }
                }
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Dolphin", f"Failed to extract the latest release of Dolphin:\n\n{extract_result['message']}"),
                }
            }

        self.metadata.set_version("dolphin", release_fetch_result["release"]["version"] if not custom_install else "")
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Dolphin", f"Successfully installed Dolphin to {self.settings.dolphin.install_directory}"),
            },
            "status": True
        }
        

    def delete_dolphin_button_event(self):
        if not self.settings.dolphin.install_directory.is_dir() or not any(self.settings.dolphin.install_directory.iterdir()):
            messagebox.showinfo(self.winfo_toplevel(), "Delete Dolphin", f"The Dolphin Installation directory is either empty or does not exist:\n {self.settings.dolphin.install_directory}")
            return 

        if messagebox.askyesno(self.winfo_toplevel(), "Confirmation", f"Are you sure you want to delete the contents of `{self.settings.dolphin.install_directory}`") != "yes":
            return

        self.configure_buttons(delete_dolphin_button_text="Deleting...")
        self.event_manager.add_event(
            "delete_dolphin", 
            self.delete_dolphin_handler, 
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occurred while deleting Dolphin.\nPlease check the logs for more information and report this issue.")]
            )

    def delete_dolphin_handler(self):
        if not self.settings.dolphin.install_directory.is_dir() or not any(self.settings.dolphin.install_directory.iterdir()):
            return {
                "message": {
                    "function": messagebox.showinfo,
                    "arguments": (self.winfo_toplevel(), "Delete Dolphin", f"The Dolphin Installation directory is either empty or does not exist:\n {self.settings.dolphin.install_directory}"),
                }
            }
        delete_result = self.dolphin.delete_dolphin()
        if not delete_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"Failed to delete the contents of the directory: {delete_result['message']}"),
                }
            }

        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Delete Dolphin", f"Successfully deleted the contents of `{self.settings.dolphin.install_directory}`"),
            }
        }

    def import_data_button_event(self):

        import_option = self.dolphin_import_optionmenu.get()

        if import_option == "Custom":
            directory, folders = FolderSelector(
                title="Choose directory and folders to import",
                allowed_folders=constants.Dolphin.USER_FOLDERS.value
            ).get_input()
        else:
            directory = PathDialog(title="Import Directory", text="Enter directory to import from: ", directory=True).get_input()
            if not directory["status"]:
                if directory["cancelled"]:
                    return
                messagebox.showerror(self.winfo_toplevel(), "Error", directory["message"])
                return
            directory = directory["path"]
            folders = constants.Dolphin.USER_FOLDERS.value

        self.configure_data_buttons(import_text="Importing...")
        self.event_manager.add_event(
            event_id="import_dolphin_data",
            func=self.import_data_handler,
            kwargs={"import_directory": directory, "folders": folders},
            completion_functions=[lambda: self.configure_data_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occurred while importing Dolphin data.\nPlease check the logs for more information and report this issue.")]
        )

    def import_data_handler(self, import_directory, folders):
        self.data_progress_handler.start_operation(
            title="Import Dolphin Data",
            total_units=0,
            units=" Files",
            status="Importing..."
        )
        import_result = self.dolphin.import_dolphin_data(
            import_directory=import_directory,
            folders=folders,
            progress_handler=self.data_progress_handler
        )
        if not import_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"Failed to import Dolphin data: {import_result['message']}"),
                }
            }
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Import Dolphin Data", f"Successfully imported Dolphin data from {import_directory}"),
            }
        }

    def export_data_button_event(self):
        export_directory = PathDialog(title="Export Directory", text="Enter directory to export to: ", directory=True)
        export_directory = export_directory.get_input()
        if not export_directory["status"]:
            if export_directory["cancelled"]:
                return
            messagebox.showerror("Error", export_directory["message"])
            return
        export_directory = export_directory["path"]
        
        if self.dolphin_export_optionmenu.get() == "Custom":
            _, folders = FolderSelector(title="Choose folders to export", predefined_directory=self.dolphin.get_user_directory(), allowed_folders=constants.Dolphin.USER_FOLDERS.value).get_input()
            if folders is None:
                return
        else:
            folders = constants.Dolphin.USER_FOLDERS.value
        
        self.configure_data_buttons(export_text="Exporting...")
        
        self.event_manager.add_event(
            event_id="export_dolphin_data",
            func=self.export_data_handler,
            kwargs={"export_directory": export_directory, "folders": folders},
            completion_functions=[lambda: self.configure_data_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occurred while exporting Dolphin data.\nPlease check the logs for more information and report this issue.")]
        )
        
    def export_data_handler(self, export_directory, folders):
        self.data_progress_handler.start_operation(
            title="Export Dolphin Data",
            total_units=0,
            units=" Files",
            status="Exporting..."
        )
        export_result = self.dolphin.export_dolphin_data(
            export_directory=export_directory,
            folders=folders,
            progress_handler=self.data_progress_handler
        )
        if not export_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"Failed to export Dolphin data: {export_result['message']}"),
                }
            }
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Export Dolphin Data", f"Successfully exported Dolphin data to {export_directory}"),
            }
        }

    def delete_data_button_event(self):
        if self.dolphin_delete_optionmenu.get() == "Custom":
            _, folders = FolderSelector(title="Choose folders to delete", predefined_directory=self.dolphin.get_user_directory(), allowed_folders=constants.Dolphin.USER_FOLDERS.value).get_input()
            if folders is None:
                return
        else:
            folders = constants.Dolphin.USER_FOLDERS.value

        if messagebox.askyesno(self.winfo_toplevel(), "Confirmation", "This will delete the data from Dolphin's directory. This action cannot be undone, are you sure you wish to continue?") != "yes":
            return
        self.configure_data_buttons(delete_text="Deleting...")
        self.event_manager.add_event(
            event_id="delete_dolphin_data",
            func=self.delete_data_handler,
            kwargs={"folders": folders},
            completion_functions=[lambda: self.configure_data_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occurred while deleting Dolphin data.\nPlease check the logs for more information and report this issue.")]
        )

    def delete_data_handler(self, folders):
        self.data_progress_handler.start_operation(
            title="Delete Dolphin Data",
            total_units=0,
            units=" Files",
            status="Deleting..."
        )
        delete_result = self.dolphin.delete_dolphin_data(folders_to_delete=folders, progress_handler=self.data_progress_handler)
        if not delete_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"Failed to delete Dolphin data: {delete_result['message']}"),
                }
            }
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Delete Dolphin Data", "Successfully deleted Dolphin data"),
            }
        }
