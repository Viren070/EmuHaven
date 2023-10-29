from threading import Thread
from tkinter import messagebox

import customtkinter

from gui.CTkScrollableDropdown import CTkScrollableDropdown
from gui.windows.path_dialog import PathDialog
from utils.requests_utils import get_all_releases, get_headers


class FirmwareKeysFrame(customtkinter.CTkFrame):
    def __init__(self, master, gui):
        super().__init__(master)
        self.gui = gui
        self.fetching_versions = False
        self.build_frame()
    def build_frame(self):
      
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        self.firmware_option_menu_variable = customtkinter.StringVar()
        self.firmware_option_menu_variable.set("Fetching...")
        self.key_option_menu_variable = customtkinter.StringVar()
        self.key_option_menu_variable.set("Fetching...")
        # Firmware Row
        firmware_label = customtkinter.CTkLabel(self, text="Installed Firmware:")
        firmware_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.installed_firmware_version_label = customtkinter.CTkLabel(self, text="Unknown")
        self.installed_firmware_version_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.firmware_option_menu = customtkinter.CTkOptionMenu(self, state="disabled", variable=self.firmware_option_menu_variable, dynamic_resizing=False, width=200)
        self.firmware_option_menu.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.firmware_option_menu.bind("<Button-1>", command=self.attempt_fetch)

        self.install_firmware_button = customtkinter.CTkButton(self, text="Install", width=100, command=self.gui.install_firmware_button_event)
        self.install_firmware_button.bind("<Button-1>", command=self.gui.install_firmware_button_event)
        self.install_firmware_button.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Keys Row
        keys_label = customtkinter.CTkLabel(self, text="Installed Keys:")
        keys_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.installed_key_version_label = customtkinter.CTkLabel(self, text="Unknown")
        self.installed_key_version_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.key_option_menu = customtkinter.CTkOptionMenu(self, width=200, state="disabled", dynamic_resizing=False, variable=self.key_option_menu_variable)
        self.key_option_menu.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.key_option_menu.bind("<Button-1>", command=self.attempt_fetch)
       

        self.install_keys_button = customtkinter.CTkButton(self, text="Install", width=100, command=self.gui.install_keys_button_event)
        self.install_keys_button.bind("<Button-1>", command=self.gui.install_keys_button_event)
        self.install_keys_button.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        
        
    def attempt_fetch(self, *args):
        if self.fetching_versions:
            messagebox.showwarning("Version Fetch", "A Fetch is already in progress, please try again later")
            return 
        if not (self.firmware_option_menu_variable.get() == "Click to fetch versions" or self.key_option_menu_variable.get() == "Click to fetch versions"):
            return 
        self.fetching_versions = True 
        Thread(target=self.fetch_firmware_and_key_versions, args=(True,)).start()
    def configure_firmware_key_buttons(self, state):
        self.install_firmware_button.configure(state=state)
        self.install_keys_button.configure(state=state)
        
    def fetch_firmware_and_key_versions(self, manual_fetch=False, return_dict=False):
        class Release:
            def __init__(self):
                self.name = None
                self.download_url = None
                self.size = None 
                self.version = None
        self.fetching_versions = True
        self.firmware_key_version_dict = {
            "firmware": {},
            "keys": {}
        }
        self.firmware_option_menu_variable.set("Fetching...")
        self.key_option_menu_variable.set("Fetching...")
        releases = get_all_releases("https://api.github.com/repos/Viren070/Emulator-Manager-Resources/releases?per_page=100", get_headers(self.gui.settings.app.token))
        if not all(releases):
            self.firmware_option_menu_variable.set("Click to fetch versions")
            self.key_option_menu_variable.set("Click to fetch versions")
            self.fetching_versions = False
            if manual_fetch:
                messagebox.showerror("Fetch Error", f"There was an error while attempting to fetch the available versions for firmware and keys:\n\n {releases[1]}")
            return 
        releases = releases[1]
        for release in releases:
            if "-ns" not in release["tag_name"]:
                continue 
            if not release["assets"]:
                continue 
            version = release["name"]
            assets = release["assets"]
            
            
            key_release = None
            firmware_release = None
            
            for asset in assets:
                if "Alpha" in asset["name"]:
                    firmware_release = Release()
                    firmware_release.name = asset["name"].replace("Alpha","Firmware")
                    firmware_release.download_url = asset["browser_download_url"]
                    firmware_release.size = asset["size"]
                    firmware_release.version = version 
                elif "Rebootless" not in version and "Beta" in asset["name"]:
                    key_release = Release()
                    key_release.name = asset["name"].replace("Beta", "Keys")
                    key_release.download_url = asset["browser_download_url"]
                    key_release.size = asset["size"]
                    key_release.version = version
            
            if firmware_release is not None:
                self.firmware_key_version_dict["firmware"][version] = firmware_release
            if key_release is not None and "Rebootless" not in version:
                self.firmware_key_version_dict["keys"][version] = key_release
                
        if return_dict:
            return self.firmware_key_version_dict
            
        # Extract firmware versions from the self.firmware_key_version_dict
        firmware_versions = [release.version for release in self.firmware_key_version_dict.get("firmware", {}).values()]

        # Extract key versions from the self.firmware_key_version_dict
        key_versions = [release.version for release in self.firmware_key_version_dict.get("keys", {}).values()]

        if not len(key_versions) == 0:
            self.key_option_menu_variable.set(key_versions[0])
            self.key_option_menu.configure(state="normal")
        else:
            self.key_option_menu_variable.set("None Found")
        if not len(firmware_versions) == 0:
            self.firmware_option_menu_variable.set(firmware_versions[0])
            self.firmware_option_menu.configure(state="normal")
        else:
            self.firmware_option_menu_variable.set("None Found")
        
        self.install_firmware_button.configure(state="normal")
        self.install_keys_button.configure(state="normal")
        self.firmware_option_menu.configure(values=firmware_versions)
        self.key_option_menu.configure(values=key_versions)
        CTkScrollableDropdown(self.firmware_option_menu, width=300, height=200, values=firmware_versions, resize=False, button_height=30)
        CTkScrollableDropdown(self.key_option_menu, width=300, height=200, values=key_versions, resize=False, button_height=30)
        self.fetching_versions = False