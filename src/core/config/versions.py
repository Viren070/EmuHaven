import json

from core.config.paths import Paths
from core.logging.logger import Logger


class Versions:
    def __init__(self, paths: Paths):
        self.logger = Logger(__name__).get_logger()
        self.paths = paths
        self.versions_dict = {}
        self.versions_file = self.paths.versions_file
        self.load_versions_from_file()

    def create_versions_file(self):
        self.logger.debug("Creating versions file at %s", self.versions_file)
        self.versions_file.touch()
        with open(self.versions_file, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4)

    def load_versions_from_file(self):
        if not self.versions_file.exists():
            return
        with open(self.versions_file, "r", encoding="utf-8") as file:
            try:
                self.versions_dict = json.load(file)
            except json.JSONDecodeError:
                self.logger.error("Versions file is not a valid JSON file. Recreating the file.")
                self.create_versions_file()
                self.versions_dict = {}

    def save_versions_to_file(self):
        if not self.versions_file.exists():
            self.versions_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger.debug("Saving versions to file")
        with open(self.versions_file, "w", encoding="utf-8") as file:
            json.dump(self.versions_dict, file, indent=4)

    def set_version(self, key, value):
        self.logger.info("Setting version for %s to %s", key, value)
        self.versions_dict[key] = value
        self.save_versions_to_file()

    def get_version(self, key):
        self.load_versions_from_file()
        self.logger.debug("Getting version for %s", key)
        return self.versions_dict.get(key, "")
