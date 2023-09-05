import json
import os

from settings.app_settings import AppSettings
from settings.dolphin_settings import DolphinSettings
from settings.yuzu_settings import YuzuSettings

class Settings:
    def __init__(self, master, root_dir):
        self.root_dir = root_dir
        self.version = "2"
        self.settings_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "config", "settings.json")
            
        self.yuzu = YuzuSettings(self)
        self.dolphin = DolphinSettings(self)
        self.app = AppSettings(self)
        if not os.path.exists(self.settings_file) or not self.settings_file_valid():
            self.create_settings_file() 
        else:
            self.load()
                    
        self.define_image_paths(os.path.join(root_dir, "images"))
        self.update_file()
    def create_settings_file(self):
        settings_template = { 
            "version": self.version,
            
            "dolphin_settings": {
                "user_directory": "",
                "install_directory": "",
                "auto_import__export_directory": "",
                "export_directory": "",
                "zip_path" : ""
                
            },
            "yuzu_settings": {
                "user_directory": "",
                "install_directory": "",
                "auto_import__export_directory" : "",
                "export_directory" : "",
                "installer_path" : "",
                "firmware_path" : "",
                "key_path" : ""
                
            },
            "app_settings": {
                "image_paths": {
                    "dolphin_logo": '',
                    "dolphin_banner_dark": '',
                    "dolphin_banner_light": "",
                    "yuzu_logo": "", 
                    "yuzu_mainline": "",
                    "yuzu_early_access": "",
                    "padlock_dark": "",
                    "padlock_light": "",
                    "play_dark": "",
                    "play_light": "",
                    "settings_dark": "",
                    "settings_light": "",
                    },
                "appearance_mode" : "",
                "colour_theme" : "",
                "auto_import__export_default_value":  "",
                "default_yuzu_channel": "",
                "ask_firmware": ""
            }
        }
        if not os.path.exists(os.path.dirname(os.path.abspath(self.settings_file))):
            os.makedirs(os.path.dirname(os.path.abspath(self.settings_file)))
        with open(self.settings_file, "w") as f:
            json.dump(settings_template, f)
    
    def define_image_paths(self, image_path):
        self.image_path = image_path
        with open(self.settings_file, "r") as f:
            settings = json.load(f)
        image_paths = settings["app_settings"]["image_paths"]
        if len(image_paths) != 12:
            settings["app_settings"]["image_paths"] = {
                    "dolphin_logo": '',
                    "dolphin_banner_dark": '',
                    "dolphin_banner_light": "",
                    "yuzu_logo": "", 
                    "yuzu_mainline": "",
                    "yuzu_early_access": "",
                    "padlock_dark": "",
                    "padlock_light": "",
                    "play_dark": "",
                    "play_light": "",
                    "settings_dark": "",
                    "settings_light": "",
                    }
        for name, path in settings["app_settings"]["image_paths"].items():
            path = os.path.join(image_path, f"{name}.png")
            settings["app_settings"]["image_paths"][name] = path
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)
    
    def get_image_path(self, image_name):
        with open(self.settings_file, "r") as f:
            settings=json.load(f)
        if image_name=="all":
            return settings["app_settings"]["image_paths"]
        image_path = settings["app_settings"]["image_paths"][image_name]
        return image_path


    def load(self):
        with open(self.settings_file, "r") as file:
            settings = json.load(file)
            
        sections = {
            "dolphin_settings": self.dolphin,
            "yuzu_settings": self.yuzu,
            "app_settings": self.app
        }
        
        for section_name, section_obj in sections.items():
            section_settings = settings[section_name]
            for setting_name, value in section_settings.items():
                if (setting_name == "export_directory" or setting_name == "auto_import__export_directory") and value!="" and not os.path.exists(os.path.abspath(value)):
                    os.makedirs(os.path.abspath(value))
                elif setting_name != "image_paths" and os.path.join("Temp", "_MEI") in os.path.normpath(value):
                    continue # skip as settings file contains old MEI path.
                elif setting_name == "image_paths":
                    for image_name, path in value.items():
                        if os.path.join("Temp", "_MEI") in os.path.normpath(path):
                            continue
                if value == "":
                    if os.path.exists(section_obj.default_settings[setting_name]): 
                        setattr(section_obj, setting_name, section_obj.default_settings[setting_name])
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
                "auto_import__export_directory": self.dolphin.auto_import__export_directory,
                "export_directory": self.dolphin.export_directory,
                "zip_path" : self.dolphin.zip_path
                
            },
            "yuzu_settings": {
                "user_directory": self.yuzu.user_directory,
                "install_directory": self.yuzu.install_directory,
                "auto_import__export_directory" : self.yuzu.auto_import__export_directory,
                "export_directory" : self.yuzu.export_directory,
                "installer_path" : self.yuzu.installer_path,
                "firmware_path" : self.yuzu.firmware_path,
                "key_path" : self.yuzu.key_path
                
            },
            "app_settings": {
                "image_paths": self.get_image_path("all"),
                "appearance_mode" : self.app.appearance_mode,
                "colour_theme" : self.app.colour_theme,
                "auto_import__export_default_value":  self.app.auto_import__export_default_value,
                "default_yuzu_channel": self.app.default_yuzu_channel,
                "ask_firmware": self.app.ask_firmware
            }
        }
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)
    
    def settings_file_valid(self):
        with open(self.settings_file, "r") as file:
            settings = json.load(file)
        try:
            if not settings["version"] == self.version:
                return False 
            yuzu_image_path = settings["app_settings"]["image_paths"]["yuzu_logo"]
            return True
            
        except (KeyError, json.JSONDecodeError):
            return False