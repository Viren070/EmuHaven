import os

from utils.paths import is_path_exists_or_creatable


class YuzuSettings:
    def __init__(self, master):
        self.emulator_file_path = os.path.join(master.root_dir,"Emulator Files")
        self._default_settings = {
            'user_directory': os.path.join(os.getenv("APPDATA"), "Yuzu"),
            'install_directory': os.path.join(os.getenv("LOCALAPPDATA"), "Yuzu"),
            'global_save_directory': os.path.join(os.getcwd(), "User Data","Yuzu"),
            'export_directory': os.path.join(os.getcwd(), "User Data","Yuzu"),
            'installer_path': os.path.join(self.emulator_file_path, "yuzu_install.exe"),
            'firmware_path': os.path.join(self.emulator_file_path, "Yuzu Files", "Firmware 16.0.3 (Rebootless Update 2).zip"),
            'key_path': os.path.join(self.emulator_file_path, "Yuzu Files", "Keys 16.0.3.zip")
        }
        self._settings = self._default_settings

    def restore_default(self):
        for name, value in self._default_settings.items():
            setattr(self, name, value)
    def _set_directory_property(self, property_name, value):
        if is_path_exists_or_creatable(value):
            self._settings[property_name] = value
        else:
            raise ValueError(f"{property_name} - Invalid Path: {value}")
    def _set_path_property(self, property_name, value):
        if not os.path.exists(value):
            raise FileNotFoundError(f"{property_name} - Path does not exist: {value}")
        if (property_name == "firmware_path" or property_name == "key_path") and not value.endswith(".zip"):
            raise ValueError("Expected file type of .zip")
        elif property_name == "installer_path" and not value.endswith(".exe"):
            raise ValueError("Expected file type of .exe")
        self._settings[property_name] = value
    def _get_property(self, property_name):
        return self._settings[property_name]
    
    
    user_directory = property(lambda self: self._get_property('user_directory'), 
                              lambda self, value: self._set_directory_property('user_directory', value))
    
    install_directory = property(lambda self: self._get_property('install_directory'), 
                                 lambda self, value: self._set_directory_property('install_directory', value))
    
    global_save_directory = property(lambda self: self._get_property('global_save_directory'), 
                                     lambda self, value: self._set_directory_property('global_save_directory', value))
    
    export_directory = property(lambda self: self._get_property('export_directory'), 
                                lambda self, value: self._set_directory_property('export_directory', value))
    
    installer_path = property(lambda self: self._get_property('installer_path'), 
                              lambda self, value: self._set_path_property('installer_path', value))
    
    firmware_path = property(lambda self: self._get_property('firmware_path'), 
                             lambda self, value: self._set_path_property('firmware_path', value))
    
    key_path = property(lambda self: self._get_property('key_path'), 
                        lambda self, value: self._set_path_property('key_path', value))