import os
from pathlib import Path
import json 

import platformdirs
from core.constants import App


class Paths:
    def __init__(self):
        portable_mode = Path("PORTABLE.txt").exists()
            
        self.app_dir = (
            platformdirs.user_data_path(
                appauthor=App.AUTHOR.value, appname=App.NAME.value, roaming=True
            )
            if not portable_mode
            else Path(os.getcwd()) / "portable"
        )
        self.cache_dir = self.app_dir / "cache"
        self.asset_dir = Path(__file__).resolve().parent.parent / "assets"
        self.versions_file = self.app_dir / "versions.json"
        self.settings_file = self.app_dir / "settings.json"
  
    def get_image_path(self, image_name):
        return self.asset_dir / "images" / f"{image_name}.png"

    def get_list_of_themes(self):
        return [Path(theme) for theme in (self.asset_dir / "themes").iterdir() if theme.suffix == ".json"]

    def is_theme_valid(self, theme):
        if not theme.exists():
            return False
        with open(theme, "r", encoding="utf-8") as file:
            theme = json.load(file)
            try:
                test = [theme["CTk"]["fg_color"], theme["CTkToplevel"]["fg_color"],
                        theme["CTkFrame"]["fg_color"], theme["CTkButton"]["fg_color"],
                        theme["CTkLabel"]["fg_color"], theme["CTkEntry"]["fg_color"],
                        theme["CTkProgressBar"]["fg_color"], theme["CTkOptionMenu"]["fg_color"],
                        theme["CTkScrollbar"]["fg_color"], theme["CTkScrollableFrame"]["label_fg_color"]
                        ]
                return all(test)
            except KeyError as error:
                print(error)
                return False
