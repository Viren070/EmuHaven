from pathlib import Path

import platformdirs

from core.config import constants
from core.logging.logger import Logger


class Paths:
    def __init__(self):
        portable_mode = Path("PORTABLE.txt").exists()
        self.logger = Logger(__name__).get_logger()
        self.app_dir = (
            platformdirs.user_data_path(
                appauthor=constants.App.AUTHOR.value, appname=constants.App.NAME.value, roaming=True
            )
            if not portable_mode
            else Path.cwd() / "portable"
        )
        self.logger.info("Portable mode: %s", portable_mode)
        self.logger.info("App directory: %s", self.app_dir)
        self.cache_dir = self.app_dir / "cache"
        self.asset_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        self.versions_file = self.app_dir / "versions.json"
        self.settings_file = self.app_dir / "settings.json"
