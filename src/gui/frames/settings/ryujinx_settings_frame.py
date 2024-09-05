from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from gui.frames.settings.setting_modal import SettingModal
import customtkinter


class RyujinxSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings
        self.build_frame()

    def build_frame(self):
        self.grid_columnconfigure(0, weight=1)

        install_directory_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings.ryujinx,
                "id": "install_directory",
                "type": "path",
                "title": "Install Directory",
                "description": "The directory where Ryujinx is installed.",
            },
            path_options={
                "type": "directory",
                "title": "Select Ryujinx Install Directory",
            }
        )
        install_directory_setting.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        portable_mode_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings.ryujinx,
                "id": "portable_mode",
                "type": "switch",
                "title": "Portable Mode",
                "description": "Enable portable mode for Ryujinx.",
            },
        )
        portable_mode_setting.grid(row=1, column=0, padx=10, pady=5, sticky="ew")