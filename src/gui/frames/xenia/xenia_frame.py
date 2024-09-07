import customtkinter
from CTkToolTip import CTkToolTip

from core.emulators.xenia.runner import Xenia
from core.utils.thread_event_manager import ThreadEventManager
from gui.frames.emulator_frame import EmulatorFrame
from gui.frames.xenia.xenia_rom_frame import XeniaROMFrame
from gui.libs import messagebox
from gui.progress_handler import ProgressHandler
from gui.windows.path_dialog import PathDialog


class XeniaFrame(EmulatorFrame):
    def __init__(self, master, paths, settings, versions, assets, cache, event_manager: ThreadEventManager):
        super().__init__(parent_frame=master, paths=paths, settings=settings, versions=versions, assets=assets, exclude_data=True)
        self.xenia = Xenia(self, settings, versions)
        self.paths = paths
        self.cache = cache
        self.event_manager = event_manager
        self.add_to_frame()

    def add_to_frame(self):

        # create xenia 'Play' frame and widgets
        self.start_frame = customtkinter.CTkFrame(self, corner_radius=0, border_width=0)
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)

        self.center_frame = customtkinter.CTkFrame(self.start_frame, corner_radius=0)
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

        self.launch_xenia_button = customtkinter.CTkButton(self.actions_frame, height=40, width=200, image=self.assets.play_image, text="Launch Xenia  ", command=self.launch_xenia_button_event, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.launch_xenia_button.grid(row=0, column=2, padx=30, pady=15, sticky="n")
        self.launch_xenia_button.bind("<Button-1>", command=self.launch_xenia_button_event)
        CTkToolTip(self.launch_xenia_button, message="Click me to launch Xenia.\nHold shift to toggle the update behaviour.\nIf automatic updates are disabled, shift-clicking will update the emulator\nand otherwise it will skip the update.")

        self.install_xenia_button = customtkinter.CTkButton(self.actions_frame, text="Install Xenia", command=self.install_xenia_button_event)
        self.install_xenia_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.install_xenia_button.bind("<Button-1>", command=self.install_xenia_button_event)
        CTkToolTip(self.install_xenia_button, message="Click me to download and install the latest release of Xenia from the internet\nShift-Click me to install xenia with a custom archive")

        self.delete_xenia_button = customtkinter.CTkButton(self.actions_frame, text="Delete Xenia", fg_color="red", hover_color="darkred", command=self.delete_xenia_button_event)
        self.delete_xenia_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        CTkToolTip(self.delete_xenia_button, message="Click me to delete the installation of Xenia at the directory specified in settings.")
        # Early Access Actions Frame

        self.log_frame = customtkinter.CTkFrame(self.center_frame, fg_color='transparent', border_width=0)
        self.log_frame.grid(row=4, column=0, padx=80, sticky="ew")
        self.log_frame.grid_propagate(False)
        self.log_frame.grid_columnconfigure(0, weight=3)
        self.main_progress_frame = ProgressHandler(self.log_frame)
        
        self.manage_data_frame = customtkinter.CTkFrame(self.start_frame, corner_radius=0, border_width=0)
        # create xenia downloader button, frame and widgets
        self.actions_frame.grid_propagate(True)
        self.selected_channel.set(self.settings.xenia.release_channel.title())
        self.switch_channel()

        self.manage_roms_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        self.manage_roms_frame.grid_columnconfigure(0, weight=1)
        self.manage_roms_frame.grid_rowconfigure(0, weight=1)
        self.rom_frame = XeniaROMFrame(self.manage_roms_frame, self.xenia, self.settings, self.cache)
        self.rom_frame.grid(row=0, column=0,  padx=20, pady=20, sticky="nsew")

    def switch_channel(self, value=None):
        value = self.selected_channel.get()
        self.settings.xenia.release_channel = value.lower()
        self.settings.save()
        self.image_button.configure(image=self.assets.xenia_canary_banner if value == "Canary" else self.assets.xenia_banner)
        self.configure_buttons(state="normal")

    def configure_buttons(
        self,
        state="disabled",
        launch_xenia_button_text=None,
        install_xenia_button_text=None,
        delete_xenia_button_text=None,
    ):
        if launch_xenia_button_text is None:
            launch_xenia_button_text = f"Launch Xenia {self.settings.xenia.release_channel.title()}"
        if install_xenia_button_text is None:
            install_xenia_button_text = f"Install Xenia {self.settings.xenia.release_channel.title()}"
        if delete_xenia_button_text is None:
            delete_xenia_button_text = f"Delete Xenia {self.settings.xenia.release_channel.title()}"

        self.launch_xenia_button.configure(state=state, text=launch_xenia_button_text)
        self.install_xenia_button.configure(state=state, text=install_xenia_button_text)
        self.delete_xenia_button.configure(state=state, text=delete_xenia_button_text)

    def launch_xenia_button_event(self, event=None):
        if event is None or self.launch_xenia_button.cget("state") == "disabled":
            return
        auto_update = self.settings.auto_emulator_updates if not event.state & 1 else not self.settings.auto_emulator_updates
        self.configure_buttons(state="disabled", launch_xenia_button_text="Checking for updates..." if auto_update else "Launching...")
        self.event_manager.add_event(
            event_id="launch_xenia",
            func=self.launch_xenia_handler,
            kwargs={"auto_update": auto_update},
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occured while launching Xenia. Please check the logs for more information and report this issue.")]
        )

        
    def launch_xenia_handler(self, auto_update):
        if auto_update:
            self.configure_buttons(launch_xenia_button_text="Checking for updates...")
            update = self.install_xenia_handler(update_mode=True)
            if not update.get("status", False):
                self.configure_buttons(launch_xenia_button_text="Oops!")
                return update
        
        self.configure_buttons(launch_xenia_button_text="Launched!")
        launch_result = self.xenia.launch_xenia()
        
        if not launch_result["run_status"]:
            self.configure_buttons(launch_xenia_button_text="Oops!")
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", launch_result["message"]),
                }
            }
        if launch_result["error_encountered"]:
            self.configure_buttons(launch_xenia_button_text="Oops!")
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", launch_result["message"]),
                }
            }
        
        return {}
    
    def install_xenia_button_event(self, event=None):
        if event is None or self.install_xenia_button.cget("state") == "disabled":
            return
        if (
            (self.settings.xenia.install_directory / self.selected_channel.get()).is_dir() and (
                any((self.settings.xenia.install_directory / self.selected_channel.get()).iterdir()) and (
                    messagebox.askyesno(
                        self.winfo_toplevel(),
                        "Confirmation", f"An installation of Xenia {self.selected_channel.get()} already exists. Do you want to overwrite it?"
                    ) != "yes"
                )
            )
        ):
            return
        path_to_archive = None
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Xenia Archive", text=f"Enter path to Xenia {self.selected_channel.get()} archive: ").get_input()
            path_to_archive = path_to_archive.get_input()
            if not path_to_archive["status"]:
                if path_to_archive["cancelled"]:
                    return
                messagebox.showerror(self.winfo_toplevel(), "Install Xenia", path_to_archive["message"])
                return
            path_to_archive = path_to_archive["path"]
        self.configure_buttons(install_xenia_button_text="Installing...")
        self.event_manager.add_event(
            event_id="install_xenia",
            func=self.install_xenia_handler,
            kwargs={"archive_path": path_to_archive},
            completion_functions=[lambda: self.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occured while installing Xenia. Please check the logs for more information and report this issue.")]
        )
        
    def install_xenia_handler(self, update_mode=False, archive_path=None):
        custom_install = archive_path is not None
        
        if archive_path is None:
            release_fetch_result = self.xenia.get_xenia_release()
            if not release_fetch_result["status"]:
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self.winfo_toplevel(), "Xenia", f"Failed to fetch the {self.settings.xenia.release_channel} latest release of Xenia:\n\n{release_fetch_result['message']}"),
                    }
                }
            
            if update_mode:
                if release_fetch_result["release"]["version"] == self.xenia.get_installed_version(release_channel=self.settings.xenia.release_channel):
                    return {
                        "status": True
                    }
                self.configure_buttons(launch_xenia_button_text="Updating...")
            self.main_progress_frame.start_operation(title="Installing Xenia", total_units=release_fetch_result["release"]["size"] / 1024 / 1024, units=" MiB", status="Downloading...")
            download_result = self.xenia.download_xenia_release(release_fetch_result["release"], progress_handler=self.main_progress_frame) 
            if not download_result["status"]:
                if "cancelled" in download_result["message"]:
                    return {
                        "message": {
                            "function": messagebox.showinfo,
                            "arguments": (self.winfo_toplevel(), "Xenia", "Cancelled download of Xenia"),
                        }
                    }
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self.winfo_toplevel(), "Xenia", f"Failed to download the latest {self.settings.xenia.release_channel} release of Xenia:\n\n{download_result['message']}"),
                    }
                }
                
            archive_path = download_result["download_path"]

        self.main_progress_frame.start_operation(title="Installing Xenia", total_units=0, units=" Files", status="Extracting...")
        extract_result = self.xenia.extract_xenia_release(archive_path, progress_handler=self.main_progress_frame)
        if not extract_result["status"]:
            if "cancelled" in extract_result["message"]:
                return {
                    "message": {
                        "function": messagebox.showinfo,
                        "arguments": (self.winfo_toplevel(), "Xenia", "Cancelled installation of Xenia"),
                    }
                }
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Xenia", f"Failed to extract Xenia:\n\n{extract_result['message']}"),
                }
            }

        self.metadata.set_version(f"xenia_{self.settings.xenia.release_channel}", release_fetch_result["release"]["version"] if not custom_install else "")
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Xenia", f"Successfully installed xenia to {self.settings.xenia.install_directory}"),
            },
            "status": True
        }

    def delete_xenia_button_event(self, event=None):
        if not (self.settings.xenia.install_directory / self.selected_channel.get()).is_dir() or not any((self.settings.xenia.install_directory / self.selected_channel.get()).iterdir()):
            messagebox.showerror(self.winfo_toplevel(), "Error", f"Could not find a Xenia {self.selected_channel.get()} installation at {self.settings.xenia.install_directory}")
            return
        if messagebox.askyesno(self.winfo_toplevel(), "Confirmation", "This will delete the Xenia installation. This action cannot be undone, are you sure you wish to continue?", icon="warning") != "yes":
            return
        self.configure_buttons(delete_xenia_button_text="Deleting...")
        self.event_manager.add_event(
            event_id="delete_xenia",
            func=self.delete_xenia_handler,
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unexpected error occured while deleting Xenia. Please check the logs for more information and report this issue.")],
            completion_functions=[lambda: self.configure_buttons(state="normal")],
        )

    def delete_xenia_handler(self):
        delete_result = self.xenia.delete_xenia()
        if not delete_result["status"]:
            return {
                "message_func": messagebox.showerror,
                "message_args": (self.winfo_toplevel(), "Error", delete_result["message"]),
            }
        return {
            "message_func": messagebox.showsuccess,
            "message_args": (self.winfo_toplevel(), "Success", delete_result["message"]),
        }
