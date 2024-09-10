import time

import customtkinter

from core.utils.thread_event_manager import ThreadEventManager
from gui.libs import messagebox
from gui.libs.CTkScrollableDropdown import CTkScrollableDropdown
from gui.windows.path_dialog import PathDialog


class FirmwareKeysFrame(customtkinter.CTkFrame):
    def __init__(self, master, frame_obj, emulator_obj):
        super().__init__(master)
        self.frame_obj = frame_obj
        self.event_manager = frame_obj.event_manager
        self.event_manager = ThreadEventManager(self)
        self.cache = frame_obj.cache
        self.settings = frame_obj.settings
        self.versions = frame_obj.versions
        self.emulator_obj = emulator_obj
        self.firmware_key_dict = {}
        self.fetching_versions = False
        self.fetched = False
        self.build_frame()
        self.update_installed_versions()

    def build_frame(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.firmware_option_menu_variable = customtkinter.StringVar()
        self.firmware_option_menu_variable.set("Click to fetch versions")
        self.key_option_menu_variable = customtkinter.StringVar()
        self.key_option_menu_variable.set("Click to fetch versions")
        # Firmware Row
        firmware_label = customtkinter.CTkLabel(self, text="Installed Firmware:")
        firmware_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.installed_firmware_version_label = customtkinter.CTkLabel(self, text="Unknown")
        self.installed_firmware_version_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.firmware_option_menu = customtkinter.CTkOptionMenu(self, state="disabled", variable=self.firmware_option_menu_variable, dynamic_resizing=False, width=200)
        self.firmware_option_menu.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.firmware_option_menu.bind("<Button-1>", command=self.request_fetch)

        self.install_firmware_button = customtkinter.CTkButton(self, text="Install", width=100, command=self.install_firmware_button_event)
        self.install_firmware_button.bind("<Button-1>", command=self.install_firmware_button_event)
        self.install_firmware_button.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Keys Row
        keys_label = customtkinter.CTkLabel(self, text="Installed Keys:")
        keys_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.installed_key_version_label = customtkinter.CTkLabel(self, text="Unknown")
        self.installed_key_version_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.key_option_menu = customtkinter.CTkOptionMenu(self, width=200, state="disabled", dynamic_resizing=False, variable=self.key_option_menu_variable)
        self.key_option_menu.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        self.key_option_menu.bind("<Button-1>", command=self.request_fetch)

        self.install_keys_button = customtkinter.CTkButton(self, text="Install", width=100, command=self.install_keys_button_event)
        self.install_keys_button.bind("<Button-1>", command=self.install_keys_button_event)
        self.install_keys_button.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    def install_firmware_button_event(self, event=None):
        if event is None or self.install_firmware_button.cget("state") == "disabled":
            return
        path_to_archive = None
        # check if firmware already installed
        if self.emulator_obj.check_current_firmware() and messagebox.askyesno(self.winfo_toplevel(), "Firmware Installation", "Firmware is already installed. Do you want to reinstall?", icon="warning") != "yes":
            return
        # obtain either an archive path or a release dict
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip",), title="Custom Firmware Archive", text="Type path to Firmware Archive: ")
            path_to_archive = path_to_archive.get_input()
            if not path_to_archive["status"]:
                if path_to_archive["cancelled"]:
                    return
                messagebox.showerror(self.winfo_toplevel(), "Install Firmware", path_to_archive["message"])
            path_to_archive = path_to_archive["path"]
            kwargs = {"firmware_archive": path_to_archive}
        else:
            if self.firmware_option_menu.cget("state") == "disabled":
                messagebox.showerror(self.winfo_toplevel(), "Error", "Please ensure that a correct version has been chosen from the menu to the left")
                return

            release = self.firmware_key_dict["firmware"][self.firmware_option_menu_variable.get()]
            kwargs = {"firmware_release": release}
        
        self.frame_obj.configure_buttons(install_firmware_button_text="Installing...")
        self.event_manager.add_event(
            event_id="install_firmware",
            func=self.install_firmware_handler,
            kwargs=kwargs,
            completion_functions=[lambda: self.frame_obj.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Firmware Installation", "An unexpected error occured while installing the firmware. Check the logs for more details and report this issue.")]
        )
        
    def install_firmware_handler(self, firmware_archive=None, firmware_release=None):
        
        custom_archive = firmware_archive is not None

        if firmware_archive is None:
            self.frame_obj.main_progress_frame.start_operation("Install Firmware", total_units=firmware_release["size"] / 1024 / 1024, units=" MiB", status="Downloading...")
            download_result = self.emulator_obj.download_firmware_release(firmware_release, progress_handler=self.frame_obj.main_progress_frame)
            if not download_result["status"]:
                if "cancelled" in download_result["message"]:
                    return {
                        "message": {
                            "function": messagebox.showinfo,
                            "arguments": (self.winfo_toplevel(), "Firmware Installation", "Firmware installation was cancelled"),
                        }
                    }
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self.winfo_toplevel(), "Firmware Installation", download_result["message"]),
                    }
                }
            firmware_archive = download_result["download_path"]
            
        elif not self.emulator_obj.verify_firmware_archive(firmware_archive):
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Firmware Installation", "The firmware archive is invalid or corrupt"),
                }
            }
        self.frame_obj.main_progress_frame.start_operation("Install Firmware", total_units=0, units=" Files", status="Extracting...")
        install_result = self.emulator_obj.install_firmware_from_archive(firmware_archive, progress_handler=self.frame_obj.main_progress_frame)
        if not install_result["status"]:
            if "cancelled" in install_result["message"]:
                return {
                    "message": {
                        "function": messagebox.showinfo,
                        "arguments": (self.winfo_toplevel(), "Firmware Installation", "Firmware installation was cancelled"),
                    }
                }
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Firmware Installation", install_result["message"]),
                }
            }
            
        if not custom_archive and self.settings.delete_files_after_installing:
            firmware_archive.unlink()
        self.versions.set_version(f"{self.emulator_obj.emulator}_firmware", firmware_release["version"].replace("v", "") if not custom_archive else "Unknown")
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Firmware Installation", "Firmware installation successful"),
            }
        }
        
    
    def install_keys_button_event(self, event=None):
        if event is None or self.install_keys_button.cget("state") == "disabled":
            return
        path_to_archive = None
        # check if firmware already installed
        if self.emulator_obj.check_current_keys()["prod.keys"] and messagebox.askyesno(self.winfo_toplevel(), "Key Installation", "Keys are already installed. Do you want to reinstall?", icon="warning") != "yes":
            return
        # obtain either an archive path or a release dict
        if event.state & 1:
            path_to_archive = PathDialog(filetypes=(".zip", ".keys"), title="Custom Keys", text="Type path to Key Archive or .keys file: ")
            path_to_archive = path_to_archive.get_input()
            if not path_to_archive["status"]:
                if path_to_archive["cancelled"]:
                    return
                messagebox.showerror(self.winfo_toplevel(), "Install Keys", path_to_archive["message"])
            path_to_archive = path_to_archive["path"]
            kwargs = {"keys_file": path_to_archive}
        else:
            if self.firmware_option_menu.cget("state") == "disabled":
                messagebox.showerror(self.winfo_toplevel(), "Error", "Please ensure that a correct version has been chosen from the menu to the left")
                return

            release = self.firmware_key_dict["keys"][self.key_option_menu_variable.get()]
            kwargs = {"keys_release": release}
        
        self.frame_obj.configure_buttons(install_keys_button_text="Installing...")
        self.event_manager.add_event(
            event_id="install_keys",
            func=self.install_keys_handler,
            kwargs=kwargs,
            completion_functions=[lambda: self.frame_obj.configure_buttons(state="normal")],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Key Installation", "An unexpected error occured while installing the keys. Check the logs for more details and report this issue.")]
        )
        
    def install_keys_handler(self, keys_file=None, keys_release=None):
        custom_keys = keys_file is not None
        
        if keys_file is None:
            self.frame_obj.main_progress_frame.start_operation("Install Keys", total_units=keys_release["size"] / 1024 / 1024, units=" MiB", status="Downloading...")
            download_result = self.emulator_obj.download_keys_release(keys_release, progress_handler=self.frame_obj.main_progress_frame)
            if not download_result["status"]:
                if "cancelled" in download_result["message"]:
                    return {
                        "message": {
                            "function": messagebox.showinfo,
                            "arguments": (self.winfo_toplevel(), "Key Installation", "Key installation was cancelled"),
                        }
                    }
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self.winfo_toplevel(), "Key Installation", f"Failed to download keys:\n\n{download_result["message"]}"),
                    }
                }
            key_archive = download_result["download_path"]
            
        elif not self.emulator_obj.verify_keys(keys_file):
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Key Installation", "Failed to install keys: \n\nInvalid or corrupt keys file or archive."),
                }
            }
        
        if custom_keys and keys_file.suffix == ".keys":
            install_result = self.emulator_obj.install_keys_from_file(keys_file)
        else:
            self.frame_obj.main_progress_frame.start_operation("Install Keys", total_units=0, units=" Files", status="Extracting...")
            install_result = self.emulator_obj.install_keys_from_archive(keys_file if custom_keys else key_archive, progress_handler=self.frame_obj.main_progress_frame)

        if not install_result["status"]:
            if "cancelled" in install_result["message"]:
                return {
                    "message": {
                        "function": messagebox.showinfo,
                        "arguments": (self.winfo_toplevel(), "Key Installation", "Key installation was cancelled"),
                    }
                }
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Key Installation", f"Failed to install keys:\n\n{install_result["message"]}"),
                }
            }
        if not custom_keys and self.settings.delete_files_after_installing:
            key_archive.unlink()
        self.versions.set_version(f"{self.emulator_obj.emulator}_keys", keys_release["version"].replace("v", "") if not custom_keys else "Unknown")
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Key Installation", "Key installation successful"),
            }
        }
            
    def add_dict_to_dropdown(self, version_dict):
        self.firmware_key_dict = version_dict
        firmware_versions = list(version_dict.get('firmware', {}).keys())
        key_versions = list(version_dict.get('keys', {}).keys())

        if not len(key_versions) == 0:
            self.key_option_menu_variable.set(key_versions[0])
            self.key_option_menu.configure(state="normal")
            CTkScrollableDropdown(self.key_option_menu, values=key_versions, width=215, height=210, resize=False, button_height=30)
        else:
            self.key_option_menu_variable.set("None Found")
        if not len(firmware_versions) == 0:
            self.firmware_option_menu_variable.set(firmware_versions[0])
            self.firmware_option_menu.configure(state="normal")
            CTkScrollableDropdown(self.firmware_option_menu, values=firmware_versions, width=215, height=210, resize=False, button_height=30)
        else:
            self.firmware_option_menu_variable.set("None Found")
        self.fetched = True

    def request_fetch(self, *args):
        if self.fetching_versions or self.fetched:
            return
        
        self.event_manager.add_event(
            event_id="fetch_firmware_keys",
            func=self.fetch_firmware_keys_dict,
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Firmware Keys", "An unexpected error occured while attempting to fetch the firmware and keys details.\nCheck the logs for more details and report this issue.")],
            completion_funcs_with_result=[self.add_dict_to_dropdown]
        )

    def fetch_firmware_keys_dict(self):
        # first check cache
        cache_lookup_result = self.cache.get_json_data_from_cache("firmware_keys")
        if cache_lookup_result and time.time() - cache_lookup_result["time"] < 604800:
            return {
                "result": (cache_lookup_result["data"],),
            }
            
        # if not in cache, create new one
        firmware_keys_fetch_result = self.emulator_obj.get_firmware_keys_dict()
        if not firmware_keys_fetch_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Firmware and Keys", firmware_keys_fetch_result["message"]),
                }
            }
            
        # save to cache
        self.cache.add_json_data_to_cache("firmware_keys", firmware_keys_fetch_result["firmware_keys"])
        
        # return result
        return {
            "result": (firmware_keys_fetch_result["firmware_keys"], ),
        }
        
    def update_installed_versions(self):
        self.installed_firmware_version_label.configure(text=self.emulator_obj.get_installed_firmware_version() or "Not Installed")
        self.installed_key_version_label.configure(text=self.emulator_obj.get_installed_key_version() or "Not Installed")