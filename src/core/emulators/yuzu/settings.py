import platform
from pathlib import Path
from core.logging.logger import Logger

class YuzuSettings:
    def __init__(self):
        self.logger = Logger(__name__).get_logger()
        self.config = {
            "install_directory": self.get_default_install_directory(),
            "portable_mode": False,
            "release_channel": "mainline",
            "last_used_data_path": None,
            "sync_user_data": True,
        }
    
    def get_default_install_directory(self):
        system = platform.system().lower()

        if system == "windows":
            return Path.home() / "AppData" / "Local" / "yuzu"

        return Path()

    def _set_property(self, property_name, value):
        self.logger.debug(f"Setting {property_name} to {value}")
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
    sync_user_data = property(
        fget=lambda self: self._get_property("sync_user_data"),
        fset=lambda self, value: self._set_property("sync_user_data", value),
    )
    release_channel = property(
        fget=lambda self: self._get_property("release_channel"),
        fset=lambda self, value: self._set_property("release_channel", value),
    )
    last_used_data_path = property(
        fget=lambda self: self._get_property("last_used_data_path"),
        fset=lambda self, value: self._set_property("last_used_data_path", value),
    )
