import platform
from pathlib import Path

from core.utils.logger import Logger


class RyujinxSettings:
    def __init__(self):
        self.logger = Logger(__name__).get_logger()
        self.config = {
            "install_directory": self.get_default_install_directory(),
            "portable": False,
            "release_channel": "master",
            "game_directory": Path(),
        }

    def get_default_install_directory(self):
        
        system = platform.system().lower()
        if system == "windows":
            # ~/AppData/Roaming/Ryujinx
            self.logger.debug("Setting default install directory for Windows")
            return Path.home() / "AppData" / "Local" / "Ryujinx"

        return None

    def _set_property(self, property_name, value):
        self.config[property_name] = value

    def _get_property(self, property_name):
        return self.config.get(property_name)

    install_directory = property(
        fget=lambda self: self._get_property("install_directory"),
        fset=lambda self, value: self._set_property("install_directory", value),
    )

    portable_mode = property(
        fget=lambda self: self._get_property("portable_mode"),
        fset=lambda self, value: self._set_property("portable_mode", value),
    )

    release_channel = property(
        fget=lambda self: self._get_property("release_channel"),
        fset=lambda self, value: self._set_property("release_channel", value),
    )
    game_directory = property(
        fget=lambda self: self._get_property("game_directory"),
        fset=lambda self, value: self._set_property("game_directory", value),
    )
