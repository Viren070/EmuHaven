from pathlib import Path
from tkinter import filedialog, messagebox

from gui.frames.settings.setting_modal import SettingModal


import customtkinter


class YuzuSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings
        self.build_frame()


    def build_frame(self):
        # give 1st column a weight of 1 so it fills all available space
        self.grid_columnconfigure(0, weight=1)

        install_directory_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings.yuzu,
                "id": "install_directory",
                "type": "path",
                "title": "Install Directory",
                "description": "The directory where Yuzu is installed.",
            },
            path_options={
                "type": "directory",
                "title": "Select Yuzu Install Directory",
            }
        )
        install_directory_setting.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        portable_mode_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings.yuzu,
                "id": "portable_mode",
                "type": "switch",
                "title": "Portable Mode",
                "description": "Enable portable mode for Yuzu.",
            },
        )
        portable_mode_setting.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.matching_dict = {}

