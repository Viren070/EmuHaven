import json
import os

import customtkinter

VALID_APPEARANCE_MODES = ["dark", "light"]
VALID_COLOUR_THEMES = ["blue", "dark-blue", "green"]
    
class AppSettings:
    def __init__(self, master):
        global VALID_COLOUR_THEMES
        VALID_COLOUR_THEMES = get_colour_themes(os.path.join(master.root_dir, "assets", "themes"))
        self.default_settings = {
            'colour_theme': "dark-blue",
            'appearance_mode': "dark",
            'use_yuzu_installer': "False",
            'current_yuzu_channel': 'Mainline',
            'delete_files': 'True', 
            'ask_firmware': 'True',
            'token': ''
        }
        self._app_settings = self.default_settings.copy()
        self.master=master
    def _set_property(self, property_name, value):
        if property_name == "colour_theme":
            if os.path.exists(value) and value.endswith(".json"):
                pass
            elif not value.lower().replace(" ","-")  in VALID_COLOUR_THEMES:
                value="dark-blue"
        elif property_name == "appearance_mode" and not value.lower().replace(" ","-") in VALID_APPEARANCE_MODES:
            value="dark"
        self._app_settings[property_name] = value
    def _get_property(self, property_name):
        return self._app_settings[property_name]
    
    colour_theme = property(lambda self: self._get_property('colour_theme'), 
                              lambda self, value: self._set_property('colour_theme', value))
    
    appearance_mode = property(lambda self: self._get_property('appearance_mode'), 
                                 lambda self, value: self._set_property('appearance_mode', value))
    
    use_yuzu_installer = property(lambda self: self._get_property('use_yuzu_installer'), 
                                     lambda self, value: self._set_property('use_yuzu_installer', value))
   
    current_yuzu_channel = property(lambda self: self._get_property('current_yuzu_channel'), 
                                     lambda self, value: self._set_property('current_yuzu_channel', value))
    delete_files = property(lambda self: self._get_property('delete_files'), 
                                     lambda self, value: self._set_property('delete_files', value))
    ask_firmware = property(lambda self: self._get_property('ask_firmware'), 
                                     lambda self, value: self._set_property('ask_firmware', value))
    token = property(lambda self: self._get_property('token'), 
                                     lambda self, value: self._set_property('token', value))
    
  

def get_colour_themes(theme_folder):
    themes = ["blue", "dark-blue", "green"]
    theme_path = theme_folder
    for file in os.listdir(theme_path):
        if file.endswith(".json"):
            themes.append(os.path.splitext(file)[0])
    return themes
    
    
def custom_theme_is_valid(theme):
    with open(theme, "r") as file:
        theme = json.load(file)
        try:
            theme["CTk"]["fg_color"]
            theme["CTkToplevel"]["fg_color"]
            theme["CTkFrame"]["fg_color"]
            theme["CTkButton"]["fg_color"]
            theme["CTkLabel"]["fg_color"]
            theme["CTkEntry"]["fg_color"]
            theme["CTkProgressBar"]["fg_color"]
            theme["CTkOptionMenu"]["fg_color"]
            theme["CTkScrollbar"]["fg_color"]
            theme["CTkScrollableFrame"]["label_fg_color"]
            return True
        except KeyError as error:
            print(f"[ERROR] app_settings.custom_theme_is_valid: Returning False:  {error}")
            return False
def load_customtkinter_themes(theme_folder):
    global VALID_COLOUR_THEMES
    VALID_COLOUR_THEMES = get_colour_themes(theme_folder)
    default_themes = ["blue", "dark-blue", "green"]
    path_to_settings = os.path.join(os.getenv("APPDATA"),"Emulator Manager", "config", "settings.json")
    appearance_mode = 'dark'
    colour_theme = 'dark-blue'
    
    if os.path.exists(path_to_settings):
        
        with open(path_to_settings, "r", encoding="utf-8") as file:
            try:
                settings = json.load(file)
  
                app_settings = settings["app_settings"]
                appearance_mode = app_settings["appearance_mode"] if app_settings["appearance_mode"] in VALID_APPEARANCE_MODES else "dark"
                colour_theme = app_settings["colour_theme"] 
                if os.path.exists(colour_theme) and colour_theme.endswith(".json"):
                    colour_theme = colour_theme if custom_theme_is_valid(colour_theme) else "dark-blue"
                elif colour_theme not in VALID_COLOUR_THEMES:
                    colour_theme = "dark-blue"
                elif colour_theme not in default_themes and colour_theme in VALID_COLOUR_THEMES:
                    colour_theme = os.path.join(theme_folder, colour_theme+".json")
                    if not os.path.exists(colour_theme):
                        colour_theme = 'dark-blue'
                elif colour_theme in default_themes:
                    pass
                else:
                    colour_theme = "dark-blue"
            except (KeyError,json.decoder.JSONDecodeError):
                pass
    
    customtkinter.set_appearance_mode(appearance_mode)
    customtkinter.set_default_color_theme(colour_theme)