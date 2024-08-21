import json 

from core.emulators.dolphin.settings import DolphinSettings
from core.emulators.ryujinx.settings import RyujinxSettings
from core.emulators.yuzu.settings import YuzuSettings
from core.emulators.xenia.settings import XeniaSettings
from core.paths import Paths
from core.constants import App
from core.utils.logger import Logger
from pathlib import Path

class Settings:
    def __init__(self):
        self.logger = Logger(__name__).get_logger()
        self.default_settings = {
            "appearance_mode": "dark",
            "colour_theme_path": Path("blue"),
            "delete_files_after_installing": True,
            "auto_app_updates": True,
            "auto_emulator_updates": True,
            "announcements_read": [],
            "firmware_denied": False,
            "token": ""

        }
        self.paths = Paths()
        self.settings_file = self.paths.settings_file

        self._settings = self.default_settings.copy()
        self.dolphin = DolphinSettings()
        self.ryujinx = RyujinxSettings()
        self.yuzu = YuzuSettings()
        self.xenia = XeniaSettings()
        self.version = "5"
        if self.settings_file_valid():
            self.load()
        else:
            self.create_settings_file()
            self.load()
            
    def settings_file_valid(self):
        if not self.settings_file.exists():
            return False
        try:
            with open(self.settings_file, "r", encoding="utf-8") as file:
                settings = json.load(file)
                if settings["version"] != self.version:  # and not self.upgrade_if_possible(settings["version"]):
                    return False
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False
                
        return True
        

    def create_settings_file(self):
        settings_template = {
            "version": self.version,

            "dolphin_settings": {
                "install_directory": "",
                "portable_mode": "",
                "game_directory": "",
                "release_channel": ""

            },
            "yuzu_settings": {
                "portable_mode": "",
                "install_directory": "",
                "release_channel": ""

            },
            "ryujinx_settings": {
                "portable_mode": "",
                "install_directory": ""
            },
            "xenia_settings": {
                "portable_mode": "",
                "install_directory": "",
                "game_directory": "",
                "release_channel": "",
            },
            "app_settings": {
                "appearance_mode": "",
                "colour_theme_path": "",
                "delete_files_after_installing": "",
                "auto_app_updates": "",
                "auto_emulator_updates": "",
                "firmware_denied": ""
            }
        }

        self.settings_file.resolve().parent.mkdir(parents=True, exist_ok=True)

        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings_template, f, indent=4)

    def load(self):
        with open(self.settings_file, "r", encoding="utf-8") as file:
            settings = json.load(file)

        sections = {
            "dolphin_settings": self.dolphin,
            "yuzu_settings": self.yuzu,
            "ryujinx_settings": self.ryujinx,
            "xenia_settings": self.xenia,
            "app_settings": self
        }

        for section_name, section_obj in sections.items():
            if section_name not in settings:
                continue
            section_settings = settings[section_name]
            for setting_name, value in section_settings.items():
                if value == "":
                    continue
                if "path" in setting_name or "directory" in setting_name and value:
                    value = Path(value)
                try:
                    # Set the value from the settings file
                    setattr(section_obj, setting_name, value)
                except Exception as error:
                    # If the value is invalid, simply ignore it as
                    # we are in the initialisation stage and cannot
                    # display error messages
                    pass

    def save(self):
        # when saving the settings, we need to convert Path objects to strings
        settings = {

            "version": self.version,

            "dolphin_settings": {
                "install_directory": str(self.dolphin.install_directory.resolve()),
                "portable_mode": self.dolphin.portable_mode,
                "game_directory": str(self.dolphin.game_directory.resolve()),
                "current_channel": self.dolphin.release_channel

            },
            "yuzu_settings": {
                "install_directory": str(self.yuzu.install_directory.resolve()),
                "release_channel": self.yuzu.release_channel,
                "portable_mode": self.yuzu.portable_mode

            },
            "ryujinx_settings": {
                "install_directory": str(self.ryujinx.install_directory.resolve()),
                "portable_mode": self.ryujinx.portable_mode
            },
            "xenia_settings": {
                "install_directory": str(self.xenia.install_directory.resolve()),
                "release_channel": self.xenia.release_channel,
                "game_directory": str(self.xenia.game_directory.resolve())
            },
            "app_settings": {
                "appearance_mode": self.appearance_mode,
                "colour_theme_path": str(self.colour_theme_path.resolve()),
                "delete_files_after_installing": self.delete_files_after_installing,
                "auto_app_updates": self.auto_app_updates,
                "auto_emulator_updates": self.auto_emulator_updates,
                "firmware_denied": self.firmware_denied,
            }
        }
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    def _set_property(self, property_name, value):
        if property_name == "colour_theme_path":
            if self.paths.is_theme_valid(value):
                pass
            else:
                value = self.default_settings[property_name]
        elif property_name == "appearance_mode" and not value.lower().replace(" ", "-") in App.VALID_APPEARANCE_MODES.value:
            value = "dark"
        self._settings[property_name] = value

    def _get_property(self, property_name):
        return self._settings[property_name]

    colour_theme_path = property(
        lambda self: self._get_property("colour_theme_path"),
        lambda self, value: self._set_property("colour_theme_path", value),
    )

    appearance_mode = property(
        lambda self: self._get_property("appearance_mode"),
        lambda self, value: self._set_property("appearance_mode", value),
    )
    delete_files_after_installing = property(
        lambda self: self._get_property("delete_files_after_installing"),
        lambda self, value: self._set_property("delete_files_after_installing", value),
    )
    auto_app_updates = property(
        lambda self: self._get_property("auto_app_updates"),
        lambda self, value: self._set_property("auto_app_updates", value),
    )
    auto_emulator_updates = property(
        lambda self: self._get_property("auto_emulator_updates"),
        lambda self, value: self._set_property("auto_emulator_updates", value),
    )
    firmware_denied = property(
        lambda self: self._get_property("firmware_denied"),
        lambda self, value: self._set_property("firmware_denied", value),
    )
    announcements_read = property(
        lambda self: self._get_property("announcements_read"),
        lambda self, value: self._set_property("announcements_read", value),
    )
    token = property(
        lambda self: self._get_property("token"),
        lambda self, value: self._set_property("token", value),
    )
