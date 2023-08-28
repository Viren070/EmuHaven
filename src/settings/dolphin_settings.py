import os

from utils.paths import is_path_exists_or_creatable


class DolphinSettings:
    def __init__(self, master):
        self.emulator_file_path = os.path.join(master.root_dir,"Emulator Files")
        print(self.emulator_file_path)
        self._default_settings = {
            'user_directory': os.path.join(os.getenv("APPDATA"), "Dolphin Emulator"),
            'install_directory': os.path.join(os.getenv("LOCALAPPDATA"), "Dolphin Emulator"),
            'global_save_directory': os.path.join(os.getcwd(), "User Data","Dolphin"),
            'export_directory': os.path.join(os.getcwd(), "User Data","Dolphin"),
            'zip_path': os.path.join(self.emulator_file_path, "Dolphin 5.0-19870.zip")
        }
        self._settings = self._default_settings

    def _set_directory_property(self, property_name, value):
        if is_path_exists_or_creatable(value):
            self._settings[property_name] = value
        else:
            raise ValueError(f"{property_name} - Invalid Path: {value}")
    def _set_path_property(self, property_name, value):
        if not os.path.exists(value):
            raise FileNotFoundError(f"{property_name} - File Not Found: {value}")
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
    
    zip_path = property(lambda self: self._get_property('zip_path'), 
                              lambda self, value: self._set_path_property('zip_path', value))
    
   