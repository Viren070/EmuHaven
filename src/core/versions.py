import json 

from core.paths import Paths


class EmulatorVersions:
    def __init__(self):
        self.paths = Paths()
        self.versions_dict = {}
        self.versions_file = self.paths.versions_file
        self.load_versions_from_file()

    def create_versions_file(self):
        self.versions_file.touch()
        with open(self.versions_file, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4)

    def load_versions_from_file(self):
        if not self.versions_file.exists():
            return
        with open(self.versions_file, "r", encoding="utf-8") as file:
            self.versions_dict = json.load(file)
            
    def save_versions_to_file(self):
        if not self.versions_file.exists():
            self.versions_file.parent.mkdir(parents=True, exist_ok=True)
            
        with open(self.versions_file, "w", encoding="utf-8") as file:
            json.dump(self.versions_dict, file, indent=4)
            
    def set_version(self, key, value):
        self.versions_dict[key] = value
        self.save_versions_to_file()
    
    def get_version(self, key):
        self.load_versions_from_file()
        return self.versions_dict.get(key)
    