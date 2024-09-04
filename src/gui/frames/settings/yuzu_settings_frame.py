from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter


class YuzuSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings
        self.build_frame()
        self.update_entry_widgets()

    def build_frame(self):
        # give 1st column a weight of 1 so it fills all available space
        self.grid_columnconfigure(0, weight=1)
        # create fonts
        title_font = customtkinter.CTkFont(family="Arial", size=15, weight="bold")
        description_font = customtkinter.CTkFont(family="Arial", size=13)


        install_directory_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=1)
        install_directory_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        install_directory_frame.grid_columnconfigure(0, weight=1)
    
        install_directory_title = customtkinter.CTkLabel(install_directory_frame, text="Install Directory", font=title_font)
        install_directory_title.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        
        install_directory_description = customtkinter.CTkLabel(install_directory_frame, justify="left", text="The directory where yuzu will be installed to.\nWithin the directory you select, a 'yuzu-windows-msvc' and 'yuzu-windows-msvc-early-access' folder will be used\nto store the respective versions of yuzu", font=description_font)
        install_directory_description.grid(row=1, column=0, padx=10, pady=2, sticky="w")
       
        install_directory_setting_frame = customtkinter.CTkFrame(install_directory_frame, fg_color="transparent", border_width=0)
        install_directory_setting_frame.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
        install_directory_setting_frame.grid_columnconfigure(0, weight=1)
        
        self.install_directory_entry = customtkinter.CTkEntry(install_directory_setting_frame)
        self.install_directory_entry.grid(row=0, column=0, pady=5, sticky="ew")
        customtkinter.CTkButton(install_directory_setting_frame, text="Browse", width=100, command=lambda entry_widget=self.install_directory_entry: self.update_with_explorer(entry_widget)).grid(row=0, column=1, padx=10, pady=5, sticky="e")
    

        portable_mode_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=1)
        portable_mode_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        portable_mode_title = customtkinter.CTkLabel(portable_mode_frame, text="Portable Mode", font=title_font)
        portable_mode_title.grid(row=0, column=0, padx=10, pady=1, sticky="w")
        
        portable_mode_description = customtkinter.CTkLabel(portable_mode_frame, text="With portable mode enabled, your user files (saves, config etc.) are stored in the same directory as the install directory", font=description_font)
        portable_mode_description.grid(row=1, column=0, padx=10, pady=0, sticky="w")
        
        self.portable_mode_var = customtkinter.BooleanVar()
        portable_mode_switch = customtkinter.CTkSwitch(portable_mode_frame, text="", variable=self.portable_mode_var, onvalue=True, offvalue=False, command=self.toggle_portable_mode, switch_height=24, switch_width=54)
        portable_mode_switch.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.matching_dict = {
            "install_directory": self.install_directory_entry,
        }

    def update_entry_widgets(self):
        for setting_name, entry_widget in self.matching_dict.items():
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, getattr(self.settings.yuzu, setting_name))

    def settings_changed(self):
        for setting_name, entry_widget in self.matching_dict.items():
            if Path(entry_widget.get()).resolve() != getattr(self.settings.yuzu, setting_name).resolve():
                return True
        return False

    def toggle_portable_mode(self):
        self.settings.yuzu.portable_mode = self.portable_mode_var.get()
        self.settings.save()

    def update_with_explorer(self, entry_widget, dialogtype=None):
        if dialogtype is None:
            new_directory = filedialog.askdirectory(initialdir=entry_widget.get())
            if new_directory is None or new_directory == "":
                return
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, new_directory)
            return
        initialdir = Path(entry_widget.get()).parent
        if dialogtype == "installer":
            new_path = filedialog.askopenfilename(initialdir=initialdir, title="Select Yuzu Installer", filetypes=[("yuzu_install.exe", "*exe")])
        else:
            new_path = filedialog.askopenfilename(initialdir=initialdir, title="Select {} ZIP".format("Firmware" if dialogtype == "firmware" else "Key"), filetypes=[("Firmware" if dialogtype == "firmware" else "Keys", "*zip" if dialogtype == "firmware" else ("*zip", "prod.keys"))])
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
