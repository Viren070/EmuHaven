import json
import os

from settings.app_settings import AppSettings
from settings.dolphin_settings import DolphinSettings
from settings.yuzu_settings import YuzuSettings
from settings.ryujinx_settings import RyujinxSettings


class Settings:
    def __init__(self, master, root_dir):
        self.root_dir = root_dir
        self.version = "3"
        if os.path.exists(os.path.join("config", "settings.json")):
            self.settings_file = os.path.join("config", "settings.json")
        else:
            self.settings_file = os.path.join(
                os.getenv("APPDATA"), "Emulator Manager", "config", "settings.json")
        self.master = master

        self.app = AppSettings(self)
        self.yuzu = YuzuSettings(self)
        self.dolphin = DolphinSettings(self)
        self.ryujinx = RyujinxSettings(self)

        if not os.path.exists(self.settings_file) or not self.settings_file_valid():
            self.create_settings_file()
        else:
            self.load()

        self.define_image_paths(os.path.join(root_dir, "assets", "images"))
        self.update_file()

    def create_settings_file(self):
        settings_template = {
            "version": self.version,

            "dolphin_settings": {
                "user_directory": "",
                "install_directory": "",
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
            "app_settings": {
                "image_paths": {
                    "dolphin_logo": '',
                    "dolphin_banner_dark": '',
                    "dolphin_banner_light": "",
                    "yuzu_logo": "",
                    "yuzu_mainline": "",
                    "yuzu_early_access": "",
                    "ryujinx_logo": "",
                    "ryujinx_banner": "",
                    "padlock_dark": "",
                    "padlock_light": "",
                    "play_dark": "",
                    "play_light": "",
                    "settings_dark": "",
                    "settings_light": "",
                    "placeholder_icon": ""
                },
                "appearance_mode": "",
                "colour_theme": "",
                "delete_files": "",
                "check_for_updates": "",
                "ask_firmware": ""
            }
        }
        if not os.path.exists(os.path.dirname(os.path.abspath(self.settings_file))):
            os.makedirs(os.path.dirname(os.path.abspath(self.settings_file)))
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings_template, f)

    def define_image_paths(self, image_path):
        self.image_path = image_path
        with open(self.settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
        image_paths = settings["app_settings"]["image_paths"]
        if len(image_paths) != 15:
            settings["app_settings"]["image_paths"] = {
                "dolphin_logo": '',
                "dolphin_banner_dark": '',
                "dolphin_banner_light": "",
                "yuzu_logo": "",
                "yuzu_mainline": "",
                "yuzu_early_access": "",
                "ryujinx_logo": "",
                "ryujinx_banner": "",
                "padlock_dark": "",
                "padlock_light": "",
                "play_dark": "",
                "play_light": "",
                "settings_dark": "",
                "settings_light": "",
                "placeholder_icon": ""
            }
        for name, path in settings["app_settings"]["image_paths"].items():
            path = os.path.join(image_path, f"{name}.png")
            settings["app_settings"]["image_paths"][name] = path
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f)

    def get_image_path(self, image_name):
        with open(self.settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
        if image_name == "all":
            return settings["app_settings"]["image_paths"]
        image_path = settings["app_settings"]["image_paths"][image_name]
        return image_path

    def load(self):
        with open(self.settings_file, "r", encoding="utf-8") as file:
            settings = json.load(file)

        sections = {
            "dolphin_settings": self.dolphin,
            "yuzu_settings": self.yuzu,
            "ryujinx_settings": self.ryujinx,
            "app_settings": self.app
        }

        for section_name, section_obj in sections.items():
            if section_name not in settings:
                continue
            section_settings = settings[section_name]
            for setting_name, value in section_settings.items():
                if setting_name != "image_paths" and os.path.join("Temp", "_MEI") in os.path.normpath(value):
                    continue  # skip as settings file contains old MEI path.
                elif setting_name == "image_paths":
                    for _, path in value.items():
                        if os.path.join("Temp", "_MEI") in os.path.normpath(path):
                            continue
                if value == "":
                    if os.path.exists(section_obj.default_settings[setting_name]):
                        setattr(section_obj, setting_name,
                                section_obj.default_settings[setting_name])
                        continue
                try:
                    setattr(section_obj, setting_name, value)
                except:
                    pass

    def update_file(self):
        settings = {

            "version": self.version,

            "dolphin_settings": {
                "user_directory": self.dolphin.user_directory,
                "install_directory": self.dolphin.install_directory,
                "rom_directory": self.dolphin.rom_directory,
                "current_channel": self.dolphin.current_channel

            },
            "yuzu_settings": {
                "user_directory": self.yuzu.user_directory,
                "install_directory": self.yuzu.install_directory,
                "installer_path": self.yuzu.installer_path,
                "use_yuzu_installer":  self.yuzu.use_yuzu_installer,
                "current_yuzu_channel": self.yuzu.current_yuzu_channel

            },
            "ryujinx_settings": {
                "user_directory": self.ryujinx.user_directory,
                "install_directory": self.ryujinx.install_directory
            },
            "app_settings": {
                "image_paths": self.get_image_path("all"),
                "appearance_mode": self.app.appearance_mode,
                "colour_theme": self.app.colour_theme,
                "delete_files": self.app.delete_files,
                "check_for_updates": self.app.check_for_updates,
                "ask_firmware": self.app.ask_firmware
            }
        }
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f)

    def settings_file_valid(self):
        if not os.path.exists(self.settings_file):
            return False
        with open(self.settings_file, "r", encoding="utf-8") as file:
            try:
                settings = json.load(file)
            except json.decoder.JSONDecodeError:
                return False
        try:
            if not settings["version"] == self.version:
                return False
            settings["app_settings"]["image_paths"]["yuzu_logo"]
            return True

        except KeyError:
            return False
