import customtkinter 
from tkinter import ttk 
import os 

class AppSettings(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings 
        self.build_frame()
    def build_frame(self):
        self.settings_path = os.path.join(os.getenv("APPDATA"),"Emulator Manager", "config")
        self.settings_file = os.path.join(self.settings_path, 'settings.json')
        
        # create appearance and themes widgets for settings menu 'Appearance'
        self.grid_columnconfigure(0, weight=1)
        
        self.appearance_mode_variable = customtkinter.StringVar()
        self.colour_theme_variable = customtkinter.StringVar()
        self.global_saves_default_value_variable = customtkinter.StringVar()
        
        self.appearance_mode_variable.set(self._get_appearance_mode().title())
        self.colour_theme_variable.set(customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title())
        customtkinter.CTkLabel(self, text="Appearance Mode: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.appearance_mode_variable, values=["Dark", "Light"], command=self.change_appearance_mode).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Colour Theme: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.colour_theme_variable, values=["Blue", "Dark Blue", "Green"], command=self.change_colour_theme).grid(row=2, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Global Saves Default Value").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.global_saves_default_value_variable, values=["True", "False"]).grid(row=4, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")
    def change_colour_theme(self, theme, startup=False):
        if customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title() == theme: # if current theme is the same as the proposed theme, return
            return
        customtkinter.set_default_color_theme(theme.replace(" ","-").lower())  #set the theme to the proposed theme after converting to proper theme name
        if not startup: # if the colour theme is being changed in the settings page and not when loading from settings.json
            self.update_settings()   # update settings to reflect latest change in appearance settings
        for after_id in self.tk.eval('after info').split():
            self.after_cancel(after_id)
        self.destroy()   # destroy current window (because changing colour theme directly does not work)
        #EmulatorManager(['settings','appearance'])  # create new window and open on the Appearance page 
        
    def change_appearance_mode(self, mode, startup=False):
        customtkinter.set_appearance_mode(mode.lower()) # change appearance mode using customtkinters function 
        if not startup:
            self.update_settings()   # update settings.json if change was through settings menu
            