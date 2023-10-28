import os

from utils.paths import is_path_exists_or_creatable


class YuzuSettings:
    def __init__(self, master):
        self.emulator_file_path = os.path.join(master.root_dir,"Emulator Files")
        self.default_settings = {
            'user_directory': os.path.join(os.getenv("APPDATA"), "Yuzu"),
            'install_directory': os.path.join(os.getenv("LOCALAPPDATA"), "Yuzu"),
            'installer_path': "",
            'use_yuzu_installer': 'False',
            'current_yuzu_channel': "Mainline",
            'rom_directory': os.path.join(os.getcwd(), "ROMS",)
            
        }
        self._settings = self.default_settings.copy()
        self.refresh_app_settings = sum
    def restore_default(self):
        for name, value in self.default_settings.items():
            try:
                setattr(self, name, value)
            except (ValueError, FileNotFoundError):
                if "path" in name:
                    setattr(self, name, "")
                else:
                    os.makedirs(value)
                    setattr(self, name, value)
                    
    def _set_property(self, property_name, value):
        self._settings[property_name] = value
        
    def _set_directory_property(self, property_name, value):
        if is_path_exists_or_creatable(value):
            self._settings[property_name] = value
        else:
            raise ValueError(f"{property_name.replace('__','/').replace('_', ' ').title()} - Invalid Path: {value}")
    def _set_path_property(self, property_name, value):
        if value == "" or value==".":
            self._settings[property_name] = value
            self.use_yuzu_installer = "False"
            self.refresh_app_settings()
            return
        if not os.path.exists(value):
            if not os.path.exists(self.default_settings[property_name]):
                self._settings[property_name] = ""
            self.use_yuzu_installer = "False"
            self.refresh_app_settings()
            raise FileNotFoundError(f"{property_name.replace('__','/').replace('_',' ').title()} - Path does not exist: {value}")
        
        if property_name == "installer_path" and not value.endswith(".exe"):
            self.use_yuzu_installer = "False"
            self.refresh_app_settings()
            raise ValueError(f"{property_name.replace('__','/').replace('_',' ').title()} - Invalid Filetype: Expected file extension of .exe but got {os.path.splitext(value)[-1]}")
                          
        self._settings[property_name] = value
    def _get_property(self, property_name):
        return self._settings[property_name]
    
    
    user_directory = property(lambda self: self._get_property('user_directory'), 
                              lambda self, value: self._set_directory_property('user_directory', value))
    
    install_directory = property(lambda self: self._get_property('install_directory'), 
                                 lambda self, value: self._set_directory_property('install_directory', value))
    
    rom_directory = property(lambda self: self._get_property('rom_directory'), 
                                lambda self, value: self._set_directory_property('rom_directory', value))
    
    installer_path = property(lambda self: self._get_property('installer_path'), 
                              lambda self, value: self._set_path_property('installer_path', value))
    
    use_yuzu_installer = property(lambda self: self._get_property('use_yuzu_installer'), 
                                     lambda self, value: self._set_property('use_yuzu_installer', value))
    
    current_yuzu_channel = property(lambda self: self._get_property('current_yuzu_channel'), 
                                     lambda self, value: self._set_property('current_yuzu_channel', value))
    