from settings.dolphin_settings import DolphinSettings
from settings.yuzu_settings import YuzuSettings
import os
import json
class Settings:
    def __init__(self):
        self.yuzu_settings = YuzuSettings()
        self.dolphin_settings = DolphinSettings()
        self.settings_file = os.path.join(os.getenv("APPDATA"), "config", "settings.json")

    def save_settings(self):
        pass