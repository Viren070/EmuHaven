"""
A module to manage the assets used in the application.
Author: Viren070
"""
import json
from pathlib import Path

import customtkinter
from PIL import Image

from core.config import constants
from core.config.paths import Paths
from core.logging.logger import Logger


class Assets:
    """
    A class to manage the assets used in the application.
    """
    def __init__(self, paths: Paths):
        self.logger = Logger(__name__).get_logger()
        self.paths = paths
        # assign the asset directory from Paths object as an attribute for easy access

    def define_assets(self):
        """
        Define all the images used in the application as customtkinter.CTkImage objects.
        """
        self.asset_dir = self.paths.asset_dir
        # assign all the images as CTkImage objects to attributes
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
        self.placeholder_icon = customtkinter.CTkImage(Image.open(self.get_image_path("placeholder_icon")), size=(224, 224))
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("play_light")),
                                                 dark_image=Image.open(self.get_image_path("play_dark")), size=(20, 20))
        self.settings_image = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("settings_light")),
                                                     dark_image=Image.open(self.get_image_path("settings_dark")), size=(20, 20))
        self.discord_icon = customtkinter.CTkImage(Image.open(self.get_image_path("discord_icon")), size=(40, 40))

        self.github_icon = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("github-mark")),
                                                  dark_image=Image.open(self.get_image_path("github-mark-white")), size=(40, 40))

        self.kofi_button = customtkinter.CTkImage(light_image=Image.open(self.get_image_path("kofi_button_red")), size=(1081*0.185, 170*0.195))

    def create_image(self, image_path, size):
        """
        Create a customtkinter image object from an image file path and a size

        Args:
            image_path (str or pathlib.Path): the path to the image file
            size (tuple): the size in (x, y) to resize the image to

        Returns:
            customtkinter.CTkImage: a customtkinter image object with the image loaded and resized
        """
        self.logger.debug(f"Creating CTkImage from {image_path}")
        return customtkinter.CTkImage(Image.open(image_path), size=size)

    def get_image_path(self, image_name):
        """
        Get the path to an image file in the assets/images directory given the image name

        Args:
            image_name (str): the name of the image file without the file extension

        Raises:
            FileNotFoundError: if the image file is not found

        Returns:
            pathlib.Path: the path to the image file
        """
        path = self.asset_dir / "images" / f"{image_name}.png"
        self.logger.debug("Resolved image path for %s as %s", image_name, path)
        if path.exists():
            return path
        self.logger.error("Image %s not found", image_name)
        raise FileNotFoundError(f"Image {image_name} not found")

    def get_theme_path(self, theme_name):
        """
        Get the path to a theme file in the themes directory given the theme name

        Args:
            theme_name (str): the name of the theme file without the file extension

        Raises:
            FileNotFoundError: if the theme file is not found

        Returns:
            pathlib.Path: the path to the theme file
        """
        if theme_name in constants.App.DEFAULT_COLOUR_THEMES.value:
            # if the theme is a built-in theme, get the path from the customtkinter asset directory
            path = Path(customtkinter.__file__).resolve().parent / "assets" / "themes" / f"{theme_name}.json"
        else:
            # otherwise, get the path from the app's asset directory
            path = self.asset_dir / "themes" / f"{theme_name}.json"
        self.logger.debug("Resolved theme path for %s as %s", theme_name, path)
        if path.exists():
            # ensure the theme file exists and return the path
            return path
        # if the theme file does not exist, return an error
        self.logger.error("Theme %s not found. Reinstall the app.", theme_name)
        raise FileNotFoundError(f"Theme {theme_name} not found. Ensure that you have not deleted a theme by mistake. You can re-download the assets folder if needed.")

    def get_list_of_themes(self):
        """
        Get a full list of all customtkinter themes from the built-in themes and the
        apps themes directory.

        Returns:
            list: A list of pathlib.Path objects for each theme file.
        """
        # get all the themes from the built-in themes directory
        # and the apps themes directory and return them as a list
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
        """
        Check if a theme file is valid by checking if all the required keys are present
        and that the theme file exists.

        Args:
            theme (pathlib.Path): The path to the theme file.

        Returns:
            bool: True if the theme file is valid, False otherwise.
        """
        if not theme.exists():
            # if the theme file does not exist return False
            self.logger.error("Theme file %s does not exist", theme)
            return False
        with open(theme, "r", encoding="utf-8") as file:
            try:
                # try to load the theme file as a json file
                theme = json.load(file)
            except json.JSONDecodeError as error:
                # if the theme file is not a valid json file return False
                self.logger.error("Theme file %s is not a valid JSON file, full error: %s", theme, error)
                return False
            try:
                # attempt to access all the required keys in the theme file
                # and use a list comprehension to check if all the keys are present
                return all([
                    theme["CTk"]["fg_color"], theme["CTkToplevel"]["fg_color"],
                    theme["CTkFrame"]["fg_color"], theme["CTkButton"]["fg_color"],
                    theme["CTkLabel"]["fg_color"], theme["CTkEntry"]["fg_color"],
                    theme["CTkProgressBar"]["fg_color"], theme["CTkOptionMenu"]["fg_color"],
                    theme["CTkScrollbar"]["fg_color"], theme["CTkScrollableFrame"]["label_fg_color"],
                    theme["CTkSwitch"]["fg_color"]
                ])
            except KeyError as error:
                # if any of the required keys are missing return False
                self.logger.error("Theme file %s is missing required key %s", theme, error)
                return False
