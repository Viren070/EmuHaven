import os
from tkinter import messagebox, ttk

import customtkinter


class AppSettings(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings 
        self.parent_frame = parent_frame
        self.build_frame()
    def build_frame(self):
        self.settings_path = os.path.join(os.getenv("APPDATA"),"Emulator Manager", "config")
        self.settings_file = os.path.join(self.settings_path, 'settings.json')
        
        # create appearance and themes widgets for settings menu 'Appearance'
        self.grid_columnconfigure(0, weight=1)
        
        self.appearance_mode_variable = customtkinter.StringVar()
        self.colour_theme_variable = customtkinter.StringVar()
        self.auto_import__export_default_value_variable = customtkinter.StringVar()
        self.auto_import__export_default_value_variable.set(self.settings.app.auto_import__export_default_value)
        self.appearance_mode_variable.set(self._get_appearance_mode().title())
        self.colour_theme_variable.set(customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title())
        customtkinter.CTkLabel(self, text="Appearance Mode: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.appearance_mode_variable, values=["Dark", "Light"], command=self.change_appearance_mode).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Colour Theme: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.colour_theme_variable, values=["Blue", "Dark Blue", "Green"], command=self.change_colour_theme).grid(row=2, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Auto Import/Export Default Value").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.auto_import__export_default_value_variable, values=["True", "False"], command=self.change_default_auto_import__export_value).grid(row=4, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")
    def change_colour_theme(self, theme):
        if customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title() == theme: # if current theme is the same as the proposed theme, return
            return
        self.settings.app.colour_theme = theme.lower().replace(" ", "-")
        self.update_settings()
        if messagebox.askyesno("Change Theme","The application must be restarted for these changes to take effect, restart now?"):    
            self.parent_frame.parent_frame.restart()
        # destroy current window (because changing colour theme directly does not work)
        # self.parent_frame.parent_frame.destroy()

        
        
    def change_appearance_mode(self, mode):
        customtkinter.set_appearance_mode(mode.lower()) # change appearance mode using customtkinters function 
        self.settings.app.appearance_mode = mode.lower()
        self.update_settings()   # update settings.json if change was through settings menu
    def change_default_auto_import__export_value(self, value):
        self.settings.app.auto_import__export_default_value = value
        self.update_settings()
    def update_settings(self):
        self.settings.update_file()