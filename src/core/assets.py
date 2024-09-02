import json
from pathlib import Path

import customtkinter
from PIL import Image

from core import constants
from core.paths import Paths


class Assets:
    def __init__(self, paths: Paths):
        self.paths = paths
        self.asset_dir = self.paths.asset_dir

        self.dolphin_logo = customtkinter.CTkImage(Image.open(self.get_image_path("dolphin_logo")), size=(24, 13.5))
        self.dolphin_banner = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("dolphin_banner_light")),
                                                     dark_image=Image.open(self.get_image_path("dolphin_banner_dark")), size=(276, 129))
        self.yuzu_logo = customtkinter.CTkImage(Image.open(self.get_image_path("yuzu_logo")), size=(26, 26))
        self.yuzu_mainline = customtkinter.CTkImage(Image.open(self.get_image_path("yuzu_mainline")), size=(276, 129))
        self.yuzu_early_access = customtkinter.CTkImage(Image.open(self.get_image_path("yuzu_early_access")), size=(276, 129))
        self.ryujinx_logo = customtkinter.CTkImage(Image.open(self.get_image_path("ryujinx_logo")), size=(26, 26))
        self.ryujinx_banner = customtkinter.CTkImage(Image.open(self.get_image_path("ryujinx_banner")), size=(276, 129))
        self.xenia_logo = customtkinter.CTkImage(Image.open(self.get_image_path("xenia_logo")), size=(26, 26))
        self.xenia_banner = customtkinter.CTkImage(Image.open(self.get_image_path("xenia_banner")), size=(276, 129))
        self.xenia_canary_banner = customtkinter.CTkImage(Image.open(self.get_image_path("xenia_canary_banner")), size=(276, 129))
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("play_light")),
                                                 dark_image=Image.open(self.get_image_path("play_dark")), size=(20, 20))
        self.settings_image = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("settings_light")),
                                                     dark_image=Image.open(self.get_image_path("settings_dark")), size=(20, 20))
        self.lock_image = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("padlock_light")),
                                                 dark_image=Image.open(self.get_image_path("padlock_dark")), size=(20, 20))
        self.discord_icon = customtkinter.CTkImage(Image.open(self.get_image_path("discord_icon")), size=(40, 40))
        self.kofi_icon = customtkinter.CTkImage(Image.open(self.get_image_path("kofi_icon")), size=(40, 40))
        self.github_icon = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("github-mark")),
                                                  dark_image=Image.open(self.get_image_path("github-mark-white")), size=(40, 40))

    def get_image_path(self, image_name):
        path = self.asset_dir / "images" / f"{image_name}.png"
        if path.exists():
            return path
        raise FileNotFoundError(f"Image {image_name} not found")

    def get_theme_path(self, theme_name):
        if theme_name in constants.App.DEFAULT_COLOUR_THEMES.value:
            path = Path(customtkinter.__file__).resolve().parent / "assets" / "themes" / f"{theme_name}.json"
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

    @staticmethod
    def is_theme_valid(theme):
        if not theme.exists():
            return False
        with open(theme, "r", encoding="utf-8") as file:
            theme = json.load(file)
            try:
                return all([
                    theme["CTk"]["fg_color"], theme["CTkToplevel"]["fg_color"],
                    theme["CTkFrame"]["fg_color"], theme["CTkButton"]["fg_color"],
                    theme["CTkLabel"]["fg_color"], theme["CTkEntry"]["fg_color"],
                    theme["CTkProgressBar"]["fg_color"], theme["CTkOptionMenu"]["fg_color"],
                    theme["CTkScrollbar"]["fg_color"], theme["CTkScrollableFrame"]["label_fg_color"]
                ])
            except KeyError as error:
                print(error)
                return False
