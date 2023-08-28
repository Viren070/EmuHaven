import os
import json
from gui.emulator_manager import EmulatorManager
import customtkinter
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
        


def main():
    load_customtkinter_themes()
    EmulatorManager(os.path.dirname(os.path.realpath(__file__)))
if __name__ == "__main__":
    main()