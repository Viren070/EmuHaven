from threading import Thread
from tkinter import messagebox

import customtkinter

from gui.CTkScrollableDropdown import CTkScrollableDropdown
from utils.requests_utils import fetch_firmware_keys_dict, get_headers


class FirmwareKeysFrame(customtkinter.CTkFrame):
    def __init__(self, master, gui):
        super().__init__(master)
        self.gui = gui
        self.fetching_versions = False
        self.firmware_key_version_dict = {
            "firmware": {},
            "keys": {}
        }
        self.build_frame()

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
        self.scrollable_firmware_option_menu = CTkScrollableDropdown(self.firmware_option_menu, width=300, height=200, resize=False, button_height=30)
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
        self.scrollable_key_option_menu = CTkScrollableDropdown(self.key_option_menu, width=300, height=200, resize=False, button_height=30)
        self.key_option_menu.bind("<Button-1>", command=self.attempt_fetch)

        self.install_keys_button = customtkinter.CTkButton(self, text="Install", width=100, command=self.gui.install_keys_button_event)
        self.install_keys_button.bind("<Button-1>", command=self.gui.install_keys_button_event)
        self.install_keys_button.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    def attempt_fetch(self, *args):
        if self.fetching_versions:
            messagebox.showwarning("Version Fetch", "A fetch is already in progress or the menu is currently being initialised, please try again later.")
            return
        if not (self.firmware_option_menu_variable.get() == "Click to fetch versions" or self.key_option_menu_variable.get() == "Click to fetch versions"):
            return
        self.fetching_versions = True
        Thread(target=self.fetch_firmware_and_key_versions, args=(True,)).start()

    def configure_firmware_key_buttons(self, state):
        self.install_firmware_button.configure(state=state)
        self.install_keys_button.configure(state=state)
        self.gui.fetch_versions()

    def create_scrollable_dropdown_with_dict(self, version_dict):
        firmware_versions = [release.version for release in version_dict.get("firmware", {}).values()]

        # Extract key versions from the self.firmware_key_version_dict
        key_versions = [release.version for release in version_dict.get("keys", {}).values()]
        if not len(key_versions) == 0:
            self.scrollable_firmware_option_menu.configure(values=key_versions)
            # CTkScrollableDropdown(self.key_option_menu, width=300, height=200, values=key_versions, resize=False, button_height=30)
            self.key_option_menu_variable.set(key_versions[0])
            self.key_option_menu.configure(state="normal")
        else:
            self.key_option_menu_variable.set("None Found")
        if not len(firmware_versions) == 0:
            self.scrollable_key_option_menu.configure(values=firmware_versions)
            # CTkScrollableDropdown(self.firmware_option_menu, width=300, height=200, values=firmware_versions, resize=False, button_height=30)
            self.firmware_option_menu_variable.set(firmware_versions[0])
            self.firmware_option_menu.configure(state="normal")
        else:
            self.firmware_option_menu_variable.set("None Found")

        self.firmware_option_menu.configure(values=firmware_versions)
        self.key_option_menu.configure(values=key_versions)

    def fetch_firmware_and_key_versions(self, manual_fetch=False):
        self.fetching_versions = True
        self.firmware_option_menu_variable.set("Fetching...")
        self.key_option_menu_variable.set("Fetching...")
        firmware_key_dict_result = fetch_firmware_keys_dict(headers=get_headers(self.gui.settings.app.token))
        if not all(firmware_key_dict_result):
            self.firmware_option_menu_variable.set("Click to fetch versions")
            self.key_option_menu_variable.set("Click to fetch versions")
            self.fetching_versions = False
            if manual_fetch:
                messagebox.showerror("Fetch Error", f"There was an error while attempting to fetch the available versions for firmware and keys:\n\n {firmware_key_dict_result[1]}")
            return
        firmware_key_version_dict = firmware_key_dict_result[1]
        # Extract firmware versions from the self.firmware_key_version_dict
        self.create_scrollable_dropdown_with_dict(firmware_key_version_dict)
        self.fetching_versions = False
        self.firmware_key_version_dict = firmware_key_version_dict
