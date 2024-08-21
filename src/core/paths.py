import json
import os
from pathlib import Path

import customtkinter
import platformdirs

from core import constants


class Paths:
    def __init__(self):
        portable_mode = Path("PORTABLE.txt").exists()

        self.app_dir = (
            platformdirs.user_data_path(
                appauthor=constants.App.AUTHOR.value, appname=constants.App.NAME.value, roaming=True
            )
            if not portable_mode
            else Path.cwd() / "portable"
        )
        self.cache_dir = self.app_dir / "cache"
        self.asset_dir = Path(__file__).resolve().parent.parent / "assets"
        self.versions_file = self.app_dir / "versions.json"
        self.settings_file = self.app_dir / "settings.json"

    def get_image_path(self, image_name):
        path = self.asset_dir / "images" / f"{image_name}.png"
        if path.exists():
            return path
        raise FileNotFoundError(f"Image {image_name} not found")

    def get_theme_path(self, theme_name):
        if theme_name in constants.App.VALID_COLOUR_THEMES.value:
            path = Path(customtkinter.__file__).parent / "assets" / "themes" / f"{theme_name}.json"
        else:
            path = self.asset_dir / "themes" / f"{theme_name}.json"
            
        if path.exists():
            return path

        raise FileNotFoundError(f"Theme {theme_name} not found")

    def get_list_of_themes(self):
        """
        Get a full list of all customtkinter themes from the built-in themes and the
        apps themes directory.

        Returns:
            list: A list of pathlib.Path objects for each theme file.
        """
        return [
            Path(theme)
            for theme in (
                Path(customtkinter.__file__).parent / "assets" / "themes"
            ).iterdir()
            if theme.suffix == ".json"
        ] + [
            Path(theme)
            for theme in (self.asset_dir / "themes").iterdir()
            if theme.suffix == ".json"
        ]

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
