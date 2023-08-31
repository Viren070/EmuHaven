import os 
import json 
import customtkinter 

VALID_APPEARANCE_MODES = ["dark", "light"]
VALID_COLOUR_THEMES = ["blue", "dark-blue", "green"]
    
class AppSettings:
    def __init__(self, master):
        self.default_settings = {
            'colour_theme': "dark-blue",
            'appearance_mode': "dark",
            'auto_import__export_default_value': "False"
            
        }
        self._app_settings = self.default_settings.copy()
        
    def _set_property(self, property_name, value):
        if property_name == "colour_theme" and not value in VALID_COLOUR_THEMES:
            value="dark-blue"
        elif property_name == "appearance_mode" and not value in VALID_APPEARANCE_MODES:
            value="dark"
        self._app_settings[property_name] = value
    def _get_property(self, property_name):
        return self._app_settings[property_name]
    
    colour_theme = property(lambda self: self._get_property('colour_theme'), 
                              lambda self, value: self._set_property('colour_theme', value))
    
    appearance_mode = property(lambda self: self._get_property('appearance_mode'), 
                                 lambda self, value: self._set_property('appearance_mode', value))
    
    auto_import__export_default_value = property(lambda self: self._get_property('auto_import__export_default_value'), 
                                     lambda self, value: self._set_property('auto_import__export_default_value', value))
   
        
def load_customtkinter_themes():
    path_to_settings = os.path.join(os.getenv("APPDATA"),"Emulator Manager", "config", "settings.json")
    appearance_mode = 'dark'
    colour_theme = 'dark-blue'
    
    if os.path.exists(path_to_settings):
        
        with open(path_to_settings, "r") as file:
            settings = json.load(file)
        try:
            app_settings = settings["app_settings"]
            appearance_mode = app_settings["appearance_mode"] if app_settings["appearance_mode"] in VALID_APPEARANCE_MODES else "dark"
            colour_theme = app_settings["colour_theme"] if app_settings["colour_theme"] in VALID_COLOUR_THEMES else "dark-blue"
        except KeyError:
            pass
    
    customtkinter.set_appearance_mode(appearance_mode)
    customtkinter.set_default_color_theme(colour_theme)