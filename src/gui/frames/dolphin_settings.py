import customtkinter 
from tkinter import ttk 
class DolphinSettings(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings 
        self.build_frame()
    def build_frame(self):
        
        self.grid_columnconfigure(0, weight=1)
        
        self.dolphin_settings_user_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_install_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_global_save_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_export_directory_variable = customtkinter.StringVar()
        self.dolphin_settings_dolphin_zip_directory_variable = customtkinter.StringVar()
       
        
        
        
        customtkinter.CTkLabel(self, text="User Directory: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_user_directory_entry = customtkinter.CTkEntry(self,  width=300)
        self.dolphin_settings_user_directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_user_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=0, column=3, padx=5, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
    
        customtkinter.CTkLabel(self, text="Dolphin Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_install_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.dolphin_settings_install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_install_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=2,column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Global Save Directory: ").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_global_save_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.dolphin_settings_global_save_directory_entry.grid(row=4, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_global_save_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=4, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Export Directory: ").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_export_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.dolphin_settings_export_directory_entry.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_export_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=6, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=7, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Dolphin ZIP: ").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_settings_dolphin_zip_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.dolphin_settings_dolphin_zip_directory_entry.grid(row=8, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.dolphin_settings_dolphin_zip_directory_entry: self.update_dolphin_setting_with_explorer(entry_widget)).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=9, columnspan=4, sticky="ew")
     
        self.dolphin_settings_actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.dolphin_settings_actions_frame.grid_columnconfigure(0, weight=1)
        self.dolphin_settings_actions_frame.grid(row=10,sticky="ew", columnspan=5, padx=10, pady=10)
        customtkinter.CTkButton(self.dolphin_settings_actions_frame, text="Apply").grid(row=10,column=3,padx=10,pady=10, sticky="e")
        customtkinter.CTkButton(self.dolphin_settings_actions_frame, text="Restore Defaults").grid(row=10, column=0, padx=10,pady=10, sticky="w")
 