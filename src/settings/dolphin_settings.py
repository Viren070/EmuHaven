import os

from utils.paths import is_path_exists_or_creatable


class DolphinSettings:
    def __init__(self, master):
        self.emulator_file_path = os.path.join(master.root_dir,"Emulator Files")
        self.default_settings = {
            'user_directory': os.path.abspath(os.path.join(os.getenv("APPDATA"), "Dolphin Emulator")),
            'install_directory': os.path.abspath(os.path.join(os.getenv("LOCALAPPDATA"), "Dolphin Emulator")),
            'export_directory': os.path.abspath(os.path.join(os.getcwd(), "User Data","Dolphin")),
            'zip_path': os.path.abspath(os.path.join(self.emulator_file_path, "Dolphin 5.0-19870.zip"))
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
        value=os.path.abspath(value)
        if is_path_exists_or_creatable(value):
            self._settings[property_name] = value
        else:
            raise ValueError(f"{property_name.replace('__','/').replace('_',' ').title()} - Invalid Path: {os.path.abspath(value)}")
    def _set_path_property(self, property_name, value):
        if value == "":
            self._settings[property_name] = value
            return
        value = os.path.abspath(value)
        if not os.path.exists(value):
            if not os.path.exists(self.default_settings[property_name]):
                self._settings[property_name] = ""
            raise FileNotFoundError(f"{property_name.replace('__','/').replace('_',' ').title()} - File Not Found: {value}")
        if not value.endswith(".zip"):
            raise ValueError(f"{property_name.replace('__','/').replace('_',' ').title()} - Invalid Filetype: Expected file extension of .zip but got {os.path.splitext(value)[-1]}")
        
        self._settings[property_name] = value
    def _get_property(self, property_name):
        return self._settings[property_name]
    
    user_directory = property(lambda self: self._get_property('user_directory'), 
                              lambda self, value: self._set_directory_property('user_directory', value))
    
    install_directory = property(lambda self: self._get_property('install_directory'), 
                                 lambda self, value: self._set_directory_property('install_directory', value))
    
    export_directory = property(lambda self: self._get_property('export_directory'), 
                                lambda self, value: self._set_directory_property('export_directory', value))
    
    zip_path = property(lambda self: self._get_property('zip_path'), 
                              lambda self, value: self._set_path_property('zip_path', value))
    
   