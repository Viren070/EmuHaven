import os 
import json 
import customtkinter 
class AppSettings:
    def __init__(self, master):
        self.default_settings = {
            'colour_theme': "dark-blue",
            'appearance_mode': "dark",
            'auto_import__export_default_value': "False"
            
        }
        self._app_settings = self.default_settings.copy()
        
    def _set_property(self, property_name, value):
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
    if not os.path.exists(path_to_settings):
        return
    with open(path_to_settings, "r") as file:
        settings = json.load(file)
    try:
        app_settings = settings["app_settings"]
        appearance_mode = app_settings["appearance_mode"]
        colour_theme = app_settings["colour_theme"]
    except KeyError:
        appearance_mode = 'dark'
        colour_theme = 'green'
    customtkinter.set_appearance_mode(appearance_mode)
    customtkinter.set_default_color_theme(colour_theme)