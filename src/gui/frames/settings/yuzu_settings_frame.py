import os
from tkinter import filedialog, messagebox, ttk

import customtkinter


class YuzuSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings
        self.build_frame()
        self.update_entry_widgets()
    def build_frame(self):
        self.grid_columnconfigure(0, weight=1)
        
        self.use_yuzu_installer_variable = customtkinter.StringVar()
        self.use_yuzu_installer_variable.set(self.settings.yuzu.use_yuzu_installer)
        customtkinter.CTkLabel(self, text="User Directory: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.user_directory_entry = customtkinter.CTkEntry(self,  width=300)
        self.user_directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.user_directory_entry: self.update_with_explorer(entry_widget)).grid(row=0, column=3, padx=5, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
    
        customtkinter.CTkLabel(self, text="yuzu Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.install_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.install_directory_entry: self.update_with_explorer(entry_widget)).grid(row=2,column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="ROM Directory: ").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.rom_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.rom_directory_entry.grid(row=8, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.rom_directory_entry: self.update_with_explorer(entry_widget)).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=9, columnspan=4, sticky="ew")    
    
        customtkinter.CTkLabel(self, text="Yuzu Installer: ").grid(row=10, column=0, padx=10, pady=10, sticky="w")
        self.yuzu_installer_path_entry = customtkinter.CTkEntry(self, width=300)
        self.yuzu_installer_path_entry.grid(row=10, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.yuzu_installer_path_entry: self.update_with_explorer(entry_widget, "installer")).grid(row=10, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=11, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Use Yuzu Installer").grid(row=12, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkCheckBox(self, text="", variable=self.use_yuzu_installer_variable, width=45, onvalue="True", offvalue="False", command=self.change_yuzu_installer_option).grid(row=12, column=3, pady=10, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=13, columnspan=4, sticky="ew")
        
        self.actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid(row=14,sticky="ew", columnspan=4, padx=10, pady=10)
        customtkinter.CTkButton(self.actions_frame, text="Apply", command=self.apply).grid(row=10,column=3,padx=10,pady=10, sticky="e")
        customtkinter.CTkButton(self.actions_frame, text="Restore Defaults", command=self.restore_defaults).grid(row=10, column=0, padx=10,pady=10, sticky="w")

        self.matching_dict = {
            "user_directory": self.user_directory_entry,
            "install_directory": self.install_directory_entry,
            "rom_directory": self.rom_directory_entry,
            "installer_path":  self.yuzu_installer_path_entry
        }
        
    def change_yuzu_installer_option(self):
        value = self.use_yuzu_installer_variable.get()
        if value == "True" and not os.path.exists(self.settings.yuzu.installer_path):
            self.use_yuzu_installer_variable.set("False")
            messagebox.showerror("Yuzu Installer", "Please ensure you have set the path to the yuzu installer in the settings before attempting to enable this option")
            return
        self.settings.yuzu.use_yuzu_installer = self.use_yuzu_installer_variable.get()
        self.settings.update_file()
    def update_entry_widgets(self):
        for setting_name, entry_widget in self.matching_dict.items():
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, getattr(self.settings.yuzu, setting_name))

    def settings_changed(self):
        for setting_name, entry_widget in self.matching_dict.items():
            if entry_widget.get() != getattr(self.settings.yuzu, setting_name):
                return True
      
        return False
    def update_with_explorer(self, entry_widget, dialogtype=None):
        if dialogtype is None:
            new_directory = filedialog.askdirectory(initialdir=entry_widget.get())
            if new_directory is None or new_directory == "":
                return
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, new_directory)
            return 
        initialdir=os.path.dirname(entry_widget.get())
        if dialogtype=="installer":
            new_path = filedialog.askopenfilename(initialdir=initialdir, title="Select Yuzu Installer", filetypes=[("yuzu_install.exe", "*exe")])
        else:
            new_path = filedialog.askopenfilename(initialdir=initialdir, title="Select {} ZIP".format("Firmware" if dialogtype=="firmware" else "Key"), filetypes=[("Firmware" if dialogtype=="firmware" else "Keys", "*zip" if dialogtype=="firmware" else ("*zip", "prod.keys"))]) 
        if new_path is None or new_path == "":
            return 
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, new_path)
        
    def apply(self):
        errors = ""
        for setting_name, entry_widget in self.matching_dict.items():
            try:
                setattr(self.settings.yuzu, setting_name, entry_widget.get())
            except (ValueError, FileNotFoundError) as error:
                errors += f"{error}\n\n"
        if errors:
            self.update_entry_widgets()
            messagebox.showerror("Settings Error", errors)
        self.settings.update_file()
    def restore_defaults(self):
        self.settings.yuzu.restore_default()
        self.update_entry_widgets()
        
