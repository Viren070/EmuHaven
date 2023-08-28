
class AppSettings:
    def __init__(self, master):
        
        self._app_settings = {
            'colour_theme': "green",
            'appearance_mode': "dark",
            'global_saves_default_value': "False"
            
        }    
        
    def _set_property(self, property_name, value):
        print(f"Setting {property_name} to {value}")
        self._app_settings[property_name] = value
    def _get_property(self, property_name):
        return self._app_settings[property_name]
    
    colour_theme = property(lambda self: self._get_property('colour_theme'), 
                              lambda self, value: self._set_property('colour_theme', value))
    
    appearance_mode = property(lambda self: self._get_property('appearance_mode'), 
                                 lambda self, value: self._set_property('appearance_mode', value))
    
    global_saves_default_value = property(lambda self: self._get_property('global_saves_default_value'), 
                                     lambda self, value: self._set_property('global_saves_default_value', value))
    def update_settings(self):
        pass
