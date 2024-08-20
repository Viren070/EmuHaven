import json 

from core.emulators.dolphin.settings import DolphinSettings
from core.emulators.ryujinx.settings import RyujinxSettings
from core.emulators.yuzu.settings import YuzuSettings
from core.emulators.xenia.settings import XeniaSettings
from core.paths import Paths
from core.constants import App

class Settings:
    def __init__(self):
        self.default_settings = {
            "appearance_mode": "auto",
            "colour_theme": "light",
            "delete_files_after_installing": True,
            "auto_app_updates": True,
            "auto_emulator_updates": True,
            "announcements_read": [],
            "firmware_denied": False

        }
        self.paths = Paths()
        self.settings_file = self.paths.settings_file

        self._settings = self.default_settings.copy()
        self.dolphin = DolphinSettings()
        self.ryujinx = RyujinxSettings()
        self.yuzu = YuzuSettings()
        self.xenia = XeniaSettings()
        self.version = "5"

    def create_settings_file(self):
        settings_template = {
            "version": self.version,

            "dolphin_settings": {
                "install_directory": "",
                "portable_mode": False,
                "rom_directory": "",
                "current_channel": ""

            },
            "yuzu_settings": {
                "user_directory": "",
                "install_directory": "",
                "installer_path": "",
                "use_yuzu_installer": "",
                "current_yuzu_channel": ""

            },
            "ryujinx_settings": {
                "user_directory": "",
                "install_directory": ""
            },
            "xenia_settings": {
                "user_directory": "",
                "install_directory": "",
                "rom_directory": "",
                "current_xenia_channel": "",
            },
            "app_settings": {
                "appearance_mode": "",
                "colour_theme": "",
                "delete_files": "",
                "check_for_app_updates": "",
                "disable_automatic_updates": "",
                "ask_firmware": ""
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
                    if section_obj.default_settings[setting_name].exists():
                        # Reset to default if the path is blank
                        setattr(section_obj, setting_name,
                                section_obj.default_settings[setting_name])
                        continue
                try:
                    # Set the value from the settings file
                    setattr(section_obj, setting_name, value)
                except Exception:
                    # If the value is invalid, simply ignore it as
                    # we are in the initialisation stage and cannot
                    # display error messages
                    pass

    def save(self):
        settings = {

            "version": self.version,

            "dolphin_settings": {
                "install_directory": self.dolphin.install_directory,
                "portable": self.dolphin.portable_mode,
                "game_directory": self.dolphin.game_directory,
                "current_channel": self.dolphin.release_channel

            },
            "yuzu_settings": {
                "install_directory": self.yuzu.install_directory,
                "release_channel": self.yuzu.release_channel,
                "portable_mode": self.yuzu.portable_mode

            },
            "ryujinx_settings": {
                "install_directory": self.ryujinx.install_directory,
                "portable_mode": self.ryujinx.portable_mode
            },
            "xenia_settings": {
                "install_directory": self.xenia.install_directory,
                "release_channel": self.xenia.release_channel,
                "game_directory": self.xenia.game_directory
            },
            "app_settings": {
                "appearance_mode": self.appearance_mode,
                "colour_theme": self.colour_theme,
                "delete_files_after_installing": self.delete_files_after_installing,
                "auto_app_updates": self.auto_app_updates,
                "auto_emulator_updates": self.auto_emulator_updates,
                "firmware_denied": self.firmware_denied,
            }
        }
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    def settings_file_valid(self):
        try:
            with open(self.settings_file, "r", encoding="utf-8") as file:
                settings = json.load(file)
                if settings["version"] != self.version and not self.upgrade_if_possible(settings["version"]):
                    return False
                settings["app_settings"]["image_paths"]["yuzu_logo"]  # Check for specific setting existence
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False
        return True

    def _set_property(self, property_name, value):
        if property_name == "colour_theme":
            if value.exists() and value.suffix == ".json" and self.paths.is_theme_valid(value):
                pass
            elif not value.lower().replace(" ", "-") in self.paths.get_list_of_themes() + App.VALID_COLOUR_THEMES:
                value = "dark-blue"
        elif property_name == "appearance_mode" and not value.lower().replace(" ", "-") in App.VALID_APPEARANCE_MODES:
            value = "dark"
        self._settings[property_name] = value

    def _get_property(self, property_name):
        return self._settings[property_name]

    colour_theme = property(
        lambda self: self._get_property("colour_theme"),
        lambda self, value: self._set_property("colour_theme", value),
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
