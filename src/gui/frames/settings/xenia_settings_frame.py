from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter


class XeniaSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings
        self.build_frame()
        self.update_entry_widgets()

    def build_frame(self):
        self.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self, text="Xenia Install Directory: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.install_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.install_directory_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.install_directory_entry: self.update_with_explorer(entry_widget)).grid(row=2, column=3, padx=5, pady=5, sticky="E")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Game Directory").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.rom_directory_entry = customtkinter.CTkEntry(self, width=300)
        self.rom_directory_entry.grid(row=8, column=2, padx=10, pady=10, sticky="E")
        customtkinter.CTkButton(self, text="Browse", width=50, command=lambda entry_widget=self.rom_directory_entry: self.update_with_explorer(entry_widget)).grid(row=8, column=3, padx=5, sticky="E")
        ttk.Separator(self, orient="horizontal").grid(row=9, columnspan=4, sticky="ew")

        self.actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid(row=10, sticky="ew", columnspan=5, padx=10, pady=10)
        customtkinter.CTkButton(self.actions_frame, text="Apply", command=self.apply).grid(row=10, column=3, padx=10, pady=10, sticky="e")
        customtkinter.CTkButton(self.actions_frame, text="Restore Defaults", command=self.restore_defaults).grid(row=10, column=0, padx=10, pady=10, sticky="w")

        self.matching_dict = {
            "install_directory":  self.install_directory_entry,
            "game_directory": self.rom_directory_entry
        }

    def settings_changed(self):
        for setting_name, entry_widget in self.matching_dict.items():
            if Path(entry_widget.get()).resolve() != getattr(self.settings.xenia, setting_name).resolve():
                return True
        return False

    def update_entry_widgets(self):
        for setting_name, entry_widget in self.matching_dict.items():
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, getattr(self.settings.xenia, setting_name))

    def update_with_explorer(self, entry_widget,):

        new_directory = filedialog.askdirectory(initialdir=entry_widget.get())
        if new_directory is None or new_directory == "":
            return
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, new_directory)
        return

    def apply(self):
        errors = ""
        for setting_name, entry_widget in self.matching_dict.items():
            try:

                setattr(self.settings.xenia, setting_name, entry_widget.get())
            except (ValueError, FileNotFoundError) as error:
                errors += f"{error}\n\n"
        if errors:
            self.update_entry_widgets()
            messagebox.showerror("Settings Error", errors)
        self.settings.update_file()

    def restore_defaults(self):
        self.settings.xenia.restore_default()
        self.update_entry_widgets()
