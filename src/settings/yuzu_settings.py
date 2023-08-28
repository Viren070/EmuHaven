from utils.paths import is_path_exists_or_creatable
import os
class YuzuSettings:
    def __init__(self, master):
        self.emulator_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(master.get_image_path("dolphin_logo")))),"Emulator Files")
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

    def _set_directory_property(self, property_name, value):
        if is_path_exists_or_creatable(value):
            print(f"Setting {property_name} to {value}")
            self._settings[property_name] = value
        else:
            raise ValueError
    def _set_path_property(self, property_name, value):
        print(f"Setting {property_name} to {value}")
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