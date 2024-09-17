import customtkinter

from gui.frames.settings.setting_modal import SettingModal


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

        sync_user_data_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings.yuzu,
                "id": "sync_user_data",
                "type": "switch",
                "title": "Sync User Data",
                "description": "Sync your user data across mainline and early access versions and between portable and non-portable modes.",
            },
        )
        sync_user_data_setting.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
