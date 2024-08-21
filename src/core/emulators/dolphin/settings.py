from pathlib import Path
import platform

from core.utils.logger import Logger


class DolphinSettings:
    def __init__(self):
        self.logger = Logger(__name__).get_logger()
        self.config = {
            "release_channel": "release",
            "portable": False,
            "install_directory": self.get_default_install_directory(),
            "game_directory": Path().resolve(),
        }

    def get_default_install_directory(self):
        
        system = platform.system().lower()
        if system == "windows":
            # ~/AppData/Roaming/Dolphin Emulator
            self.logger.debug("Setting default install directory for Windows")
            return Path.home() / "AppData" / "Local" / "Dolphin Emulator"

        return Path()

    def _set_property(self, property_name, value):
        self.config[property_name] = value

    def _get_property(self, property_name):
        return self.config.get(property_name)

    portable_mode = property(
        fget=lambda self: self._get_property("portable_mode"),
        fset=lambda self, value: self._set_property("portable_mode", value),
    )

    install_directory = property(
        fget=lambda self: self._get_property("install_directory"),
        fset=lambda self, value: self._set_property("install_directory", value),
    )

    release_channel = property(
        fget=lambda self: self._get_property("release_channel"),
        fset=lambda self, value: self._set_property("release_channel", value),
    )
    game_directory = property(
        fget=lambda self: self._get_property("game_directory"),
        fset=lambda self, value: self._set_property("game_directory", value),
    )
