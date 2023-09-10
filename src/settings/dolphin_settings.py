import os

from utils.paths import is_path_exists_or_creatable


class DolphinSettings:
    def __init__(self, master):
        self.emulator_file_path = os.path.join(master.root_dir,"Emulator Files")
        self.default_settings = {
            'user_directory': (os.path.join(os.getenv("APPDATA"), "Dolphin Emulator")),
            'install_directory': (os.path.join(os.getenv("LOCALAPPDATA"), "Dolphin Emulator")),
            'export_directory': (os.path.join(os.getcwd(), "User Data","Dolphin")),
            'rom_directory': ""
        }
        self._settings = self.default_settings.copy()

    def restore_default(self):
        for name, value in self.default_settings.items():
            try:
                setattr(self, name, value)
            except(ValueError, FileNotFoundError):
                if name == "zip_path":
                    setattr(self, name, "")
                else:
                    os.makedirs(value)
                    setattr(self, name, value)
    def _set_directory_property(self, property_name, value):
        if is_path_exists_or_creatable(value):
            self._settings[property_name] = value
        else:
            raise ValueError(f"{property_name.replace('__','/').replace('_',' ').title()} - Invalid Path: {(value)}")
   
    def _get_property(self, property_name):
        return self._settings[property_name]
    
    user_directory = property(lambda self: self._get_property('user_directory'), 
                              lambda self, value: self._set_directory_property('user_directory', value))
    
    install_directory = property(lambda self: self._get_property('install_directory'), 
                                 lambda self, value: self._set_directory_property('install_directory', value))
    
    export_directory = property(lambda self: self._get_property('export_directory'), 
                                lambda self, value: self._set_directory_property('export_directory', value))
    rom_directory = property(lambda self: self._get_property('rom_directory'), 
                                lambda self, value: self._set_directory_property('rom_directory', value))
    
   