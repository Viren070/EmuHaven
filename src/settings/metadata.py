import json
import os


class Metadata:
    def __init__(self, master, settings):
        self.master = master 
        self.settings = settings 
        self.template= {
            "dolphin": {
                "installed_version": ""
                },
            "yuzu": {
                "mainline" : {
                    "installed_version": ""
                },
                "early_access": {
                    "installed_version": ""
                },
                "firmware_version": "",
                "key_version": ""
            },
            "ryujinx": {
                "installed_version": "",
                "installed_firmware_version": "",
                "installed_key_version": ""
            }
        }
        self.metadata_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "metadata.json")
        if not os.path.exists(self.metadata_file) or not self.is_metadata_valid():
            self.create_metadata_file()
    def create_metadata_file(self):

        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        with open(self.metadata_file, "w", encoding="utf-8") as file:
            json.dump(self.template, file)
    
    def update_metadata(self, contents):
        if not os.path.exists(self.metadata_file):
            self.create_metadata_file()
        with open(self.metadata_file, "w", encoding="utf-8") as file:
            json.dump(contents, file)
            
    def get_metadata_contents(self):
        if not os.path.exists(self.metadata_file):
            self.create_metadata_file()
            return self.template
        with open(self.metadata_file, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                self.create_metadata_file()
                return self.template
    def update_installed_version(self, mode, version):
        current_contents = self.get_metadata_contents()
        match(mode):
            case "mainline":
                current_contents["yuzu"]["mainline"]["installed_version"] = version
            case "early_access":
                current_contents["yuzu"]["early_access"]["installed_version"] = version 
            case "dolphin":
                current_contents["dolphin"]["installed_version"] = version 
            case "yuzu_firmware":
                current_contents["yuzu"]["firmware_version"] = version 
            case "yuzu_keys":
                current_contents["yuzu"]["key_version"] = version
            case "ryujinx":
                current_contents["ryujinx"]["installed_version"] = version
            case "ryujinx_firmware":
                current_contents["ryujinx"]["installed_firmware_version"] = version 
            case "ryujinx_keys":
                current_contents["ryujinx"]["installed_key_version"] = version
            case _:
                raise ValueError(f"Expected str argument of mainline or early access, but got {mode}")
                
        self.update_metadata(current_contents)
        return version
    def get_installed_version(self, mode):
        current_contents = self.get_metadata_contents()
        match(mode):
            case "mainline":
                version = current_contents["yuzu"]["mainline"]["installed_version"] if os.path.exists(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc", "yuzu.exe")) else self.update_installed_version("mainline", "")
            case "early_access":
                version = current_contents["yuzu"]["early_access"]["installed_version"] if os.path.exists(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access", "yuzu.exe")) else self.update_installed_version("early_access", "")
            case "dolphin":
                version = current_contents["dolphin"]["installed_version"] if os.path.exists(os.path.join(self.settings.dolphin.install_directory, "Dolphin.exe")) else self.update_installed_version("dolphin", "")
            case "yuzu_firmware":
                version = current_contents["yuzu"]["firmware_version"] if ( os.path.exists(os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")) and os.listdir(os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")) ) else self.update_installed_version("yuzu_firmware", "")
            case "yuzu_keys":
                version = current_contents["yuzu"]["key_version"] if os.path.exists(os.path.join(self.settings.yuzu.user_directory, "keys", "prod.keys")) else self.update_installed_version("yuzu_keys", "")
            case "ryujinx":
                version = current_contents["ryujinx"]["installed_version"] if os.path.exists(os.path.join(self.settings.ryujinx.install_directory, "publish", "Ryujinx.exe")) else self.update_installed_version("ryujinx", "")
            case "ryujinx_firmware":
                version = current_contents["ryujinx"]["installed_firmware_version"] if ( os.path.exists(os.path.join(self.settings.ryujinx.user_directory, "bis", "system", "Contents", "registered")) and os.listdir(os.path.join(self.settings.ryujinx.user_directory, "bis", "system", "Contents", "registered")) ) else self.update_installed_version("ryujinx_firmware", "")
            case "ryujinx_keys":
                version = current_contents["ryujinx"]["installed_key_version"] if os.path.exists(os.path.join(self.settings.ryujinx.user_directory, "system", "prod.keys")) else self.update_installed_version("ryujinx_keys", "")
            
            case _:
                raise ValueError(f"Expected str argument of mainline or early access, but got {mode}")
        return version
    def is_metadata_valid(self):
        try:
            for mode in ["mainline", "early_access", "dolphin", "yuzu_firmware", "yuzu_keys", "ryujinx", "ryujinx_firmware", "ryujinx_keys"]:
                self.get_installed_version(mode)
            return True
        except (KeyError, TypeError):
            return False 
                