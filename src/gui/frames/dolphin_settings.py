import os
from tkinter import filedialog, messagebox, ttk

import customtkinter


class DolphinSettings(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings 
        self.build_frame()
        self.update_entry_widgets()
    def build_frame(self):
        
        self.grid_columnconfigure(0, weight=1)
 
        customtkinter.CTkLabel(self, text="User Directory: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.user_directory_entry = customtkinter.CTkEntry(self,  width=300)
        self.user_directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.user_directory_entry: self.update_with_explorer(entry_widget)).grid(row=0, column=3, padx=5, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
    
        customtkinter.CTkLabel(self, text="Dolphin Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.install_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.install_directory_entry: self.update_with_explorer(entry_widget)).grid(row=2,column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Global Save Directory: ").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.global_save_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.global_save_directory_entry.grid(row=4, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.global_save_directory_entry: self.update_with_explorer(entry_widget)).grid(row=4, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=5, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Export Directory: ").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.export_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.export_directory_entry.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.export_directory_entry: self.update_with_explorer(entry_widget)).grid(row=6, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=7, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Dolphin ZIP: ").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.dolphin_zip_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.dolphin_zip_directory_entry.grid(row=8, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.dolphin_zip_directory_entry: self.update_with_explorer(entry_widget, "zip")).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=9, columnspan=4, sticky="ew")
     
        self.actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid(row=10,sticky="ew", columnspan=5, padx=10, pady=10)
        customtkinter.CTkButton(self.actions_frame, text="Apply", command=self.apply).grid(row=10,column=3,padx=10,pady=10, sticky="e")
        customtkinter.CTkButton(self.actions_frame, text="Restore Defaults").grid(row=10, column=0, padx=10,pady=10, sticky="w")
    
        self.matching_dict = {
            "user_directory": {
                "entry_widget": self.user_directory_entry,
                "variable": self.settings.dolphin.user_directory
            },
            "install_directory": {
                "entry_widget": self.install_directory_entry,
                "variable": self.settings.dolphin.install_directory
            },
            "global_save_directory": {
                "entry_widget": self.global_save_directory_entry,
                "variable": self.settings.dolphin.global_save_directory
            },
            "export_directory": {
                "entry_widget": self.export_directory_entry,
                "variable": self.settings.dolphin.export_directory
            },
            "zip_path": {
                "entry_widget": self.dolphin_zip_directory_entry,
                "variable": self.settings.dolphin.zip_path
            }
        }
    def update_entry_widgets(self):
        for setting_name, match in self.matching_dict.items():
            match["entry_widget"].delete(0, 'end')
            match["entry_widget"].insert(0, match["variable"])

    
    def update_with_explorer(self, entry_widget, dialogtype=None):
        if dialogtype is None:
            new_directory = filedialog.askdirectory(initialdir=entry_widget.get())
            if new_directory is None or new_directory == "":
                return
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, new_directory)
            return 
        initialdir=os.path.dirname(entry_widget.get())
        if dialogtype=="zip":
            new_path = filedialog.askopenfilename(initialdir=initialdir, title="Select Dolphin archive", filetypes=[("Dolphin 5.0-xxxxx", "*zip")])
      
        if new_path is None or new_path == "":
            return 
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, new_path)
        
    def apply(self):
        errors = ""
        for setting_name, match in self.matching_dict.items():
            try:
                setattr(self.settings.dolphin, setting_name, match["entry_widget"].get())
            except (ValueError, FileNotFoundError) as error:
                errors += f"{error}\n\n"
        if errors:
            self.update_entry_widgets()
            messagebox.showerror("Settings Error", errors)
        self.settings.update_file()
        
