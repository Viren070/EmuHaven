from pathlib import Path
import platform

class YuzuSettings:
    def __init__(self):
        self.config = {
            "install_directory": self.get_default_install_directory(),
            "portable_mode": False,
            "release_channel": "mainline",
        }
    
    def get_default_install_directory(self):
        system = platform.system().lower()

        if system == "windows":
            return Path.home() / "AppData" / "Local" / "yuzu"

        return Path()

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
