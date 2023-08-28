from settings.dolphin_settings import DolphinSettings
from settings.yuzu_settings import YuzuSettings
import os
import json
class Settings:
    def __init__(self):
        
        self.settings_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "config", "settings.json")
        if not os.path.exists(self.settings_file):
            self.create_settings_file() 
        self._app_settings = {
            'colour_theme': "green",
            'appearance_mode': "dark",
            'global_saves_value': 0
            
        }    
            
        self.yuzu = YuzuSettings(self)
        self.dolphin = DolphinSettings(self)
    def _set_property(self, property_name, value):
        print(f"Setting {property_name} to {value}")
        self._app_settings[property_name] = value
    def _get_property(self, property_name):
        return self._app_settings[property_name]
    
    user = property(lambda self: self._get_property('user'), 
                              lambda self, value: self._set_property('user', value))
    
    install = property(lambda self: self._get_property('install'), 
                                 lambda self, value: self._set_property('install', value))
    
    global_save = property(lambda self: self._get_property('global_save'), 
                                     lambda self, value: self._set_property('global_save', value))
    
    export = property(lambda self: self._get_property('export'), 
                                lambda self, value: self._set_property('export', value))
    
    zip_path = property(lambda self: self._get_property('zip'), 
                              lambda self, value: self._set_property('zip', value))
    
   
    def create_settings_file(self):
        settings_template = { 
            "dolphin_settings": {
                "Dolphin User Directory": "",
                "Dolphin Installation Directory": "",
                "Dolphin Global Save Directory": "",
                "Dolphin Export Directory": "",
                "Dolphin ZIP Path" : ""
                
            },
            "yuzu_settings": {
                "Yuzu User Directory": "",
                "Yuzu Installation Directory": "",
                "Yuzu Global Save Directory" : "",
                "Yuzu Export Directory" : "",
                "Yuzu Installer Path" : "",
                "Yuzu Firmware ZIP Path" : "",
                "Yuzu Key ZIP Path" : ""
                
            },
            "app_settings": {
                "Image Paths": {
                    "dolphin_logo": '',
                    "yuzu_logo": "", 
                    "padlock_dark": "",
                    "padlock_light": "",
                    "play_dark": "",
                    "play_light": "",
                    "settings_dark": "",
                    "settings_light": ""
                    },
                "Appearance Mode" : "",
                "Colour Theme" : "",
                "Global Saves Default Value":  ""
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
        for name, path in settings["app_settings"]["Image Paths"].items():
            path = os.path.join(image_path, f"{name}.png")
            settings["app_settings"]["Image Paths"][name] = path
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)
    
    def get_image_path(self, image_name):
        with open(self.settings_file, "r") as f:
            settings=json.load(f)

        image_path = settings["app_settings"]["Image Paths"][image_name]
        return image_path

            
 