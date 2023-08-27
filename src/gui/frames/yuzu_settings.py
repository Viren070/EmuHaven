import customtkinter 
from tkinter import ttk 

class YuzuSettings(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame)
        self.settings = settings
        self.build_frame()
    def build_frame(self):
        self.grid_columnconfigure(0, weight=1)
            
        self.yuzu_settings_install_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_user_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_global_save_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_export_directory_variable = customtkinter.StringVar()
        self.yuzu_settings_installer_path_variable = customtkinter.StringVar()
        self.yuzu_settings_firmware_path_variable = customtkinter.StringVar()
        self.yuzu_settings_key_path_variable = customtkinter.StringVar()
        
        #1
        customtkinter.CTkLabel(self, text="User Directory: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_user_directory_entry = customtkinter.CTkEntry(self,  width=300)
        self.yuzu_settings_user_directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_user_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=0, column=3, padx=5, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
        #2
        customtkinter.CTkLabel(self, text="yuzu Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_install_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_settings_install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_install_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=2,column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")
        #3
        customtkinter.CTkLabel(self, text="Global Save Directory: ").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_global_save_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_settings_global_save_directory_entry.grid(row=4, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_global_save_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=4, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")
        #4
        customtkinter.CTkLabel(self, text="Export Directory: ").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_export_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_settings_export_directory_entry.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_export_directory_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=6, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=7, columnspan=4, sticky="ew")      
        #5
        customtkinter.CTkLabel(self, text="Yuzu Installer: ").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_yuzu_installer_path_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_settings_yuzu_installer_path_entry.grid(row=8, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_yuzu_installer_path_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=9, columnspan=4, sticky="ew")
        #6
        customtkinter.CTkLabel(self, text="Switch Firmware: ").grid(row=10, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_firmware_path_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_settings_firmware_path_entry.grid(row=10, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_firmware_path_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=10, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=11, columnspan=4, sticky="ew")
        #7
        customtkinter.CTkLabel(self, text="Switch Keys: ").grid(row=12, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_settings_key_path_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_settings_key_path_entry.grid(row=12, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_settings_key_path_entry: self.update_yuzu_setting_with_explorer(entry_widget)).grid(row=12, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=13, columnspan=4, sticky="ew")
        
        self.yuzu_settings_actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.yuzu_settings_actions_frame.grid_columnconfigure(0, weight=1)
        self.yuzu_settings_actions_frame.grid(row=14,sticky="ew", columnspan=4, padx=10, pady=10)
        customtkinter.CTkButton(self.yuzu_settings_actions_frame, text="Apply").grid(row=10,column=3,padx=10,pady=10, sticky="e")
        customtkinter.CTkButton(self.yuzu_settings_actions_frame, text="Restore Defaults").grid(row=10, column=0, padx=10,pady=10, sticky="w")
