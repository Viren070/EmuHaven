import os 
import json 
import customtkinter 

VALID_APPEARANCE_MODES = ["dark", "light"]
VALID_COLOUR_THEMES = ["blue", "dark-blue", "green"]
    
class AppSettings:
    def __init__(self, master):
        global VALID_COLOUR_THEMES
        VALID_COLOUR_THEMES = get_colour_themes(os.path.join(master.root_dir, "themes"))
        self.default_settings = {
            'colour_theme': "dark-blue",
            'appearance_mode': "dark",
            'auto_import__export_default_value': "False",
            'default_yuzu_channel': 'Mainline'
        }
        self._app_settings = self.default_settings.copy()
        self.master=master
    def _set_property(self, property_name, value):
        value = value.lower().replace(" ","-") if property_name == "colour_theme" else value
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
   
    default_yuzu_channel = property(lambda self: self._get_property('default_yuzu_channel'), 
                                     lambda self, value: self._set_property('default_yuzu_channel', value))
    
    
  

def get_colour_themes(theme_folder):
    themes = ["blue", "dark-blue", "green"]
    theme_path = theme_folder
    for file in os.listdir(theme_path):
        if file.endswith(".json"):
            themes.append(os.path.splitext(file)[0])
    return themes
    
def load_customtkinter_themes(theme_folder):
    global VALID_COLOUR_THEMES
    VALID_COLOUR_THEMES = get_colour_themes(theme_folder)
    default_themes = ["blue", "dark-blue", "green"]
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
            if colour_theme not in default_themes and colour_theme in VALID_COLOUR_THEMES:
                colour_theme = os.path.join(theme_folder, colour_theme+".json")
                if not os.path.exists(colour_theme):
                    colour_theme = 'dark-blue'
        except KeyError:
            pass
    
    customtkinter.set_appearance_mode(appearance_mode)
    customtkinter.set_default_color_theme(colour_theme)