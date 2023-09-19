from gui.frames.rom_search_frame import ROMSearchFrame
import customtkinter 
from tkinter import messagebox
import os
class CurrentROMSFrame(ROMSearchFrame):
    def __init__(self, master, root, emulator_settings, allowed_extensions):
        super().__init__(master, root, "")
        self.emulator_settings = emulator_settings
        self.rom_directory = getattr(emulator_settings, "rom_directory")
        self.allowed_extensions = allowed_extensions
        self.refresh_button.configure(text="Refresh", command=self.update_results)
        self.roms = self.get_current_roms()
        self.update_results()
    def update_results(self):
        self.roms = self.get_current_roms()
        if self.update_in_progress:
            self.next_button.configure(state="normal")
            self.prev_button.configure(state="normal")
            return
        self.update_in_progress = True
        start_index = (self.current_page - 1) * self.results_per_page
        end_index = start_index + self.results_per_page
        for widget in self.result_frame.winfo_children():
            widget.grid_forget()
            
        if len(self.roms) == 0:
            customtkinter.CTkLabel(self.result_frame, text=f"Nothing to see here. Download some more ROMs and they will show up here.\n\nROM Directory: '{self.rom_directory}'").grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        for i, rom in enumerate(self.roms):
            if i > end_index or i < start_index:
                continue
            entry = customtkinter.CTkEntry(self.result_frame, width=400)
            entry.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            size_suffixes = ['B', 'KB', 'MB', 'GB']
            size_in_bytes = rom.size
            for suffix in size_suffixes:
                if size_in_bytes < 1024 or suffix == 'GB':
                    break
                size_in_bytes /= 1024

            entry.insert(0, f"{size_in_bytes:.1f} {suffix} - {rom.name}")
            button = customtkinter.CTkButton(self.result_frame, text="Delete", command=lambda path=rom.path: self.delete_rom(path))
            button.grid(row=i, column=1, padx=10, pady=5, sticky="e")
            
        for widget in (self.refresh_button, self.search_button, self.search_entry, self.prev_button, self.next_button, self.current_page_entry):
            widget.configure(state="normal")
            
        self.current_page_entry.delete(0, customtkinter.END)
        self.current_page_entry.insert(0, str(self.current_page))
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.update_in_progress = False
    def get_current_roms(self):
        class ROMFile:
            def __init__(self, name, path, size):
                self.name = name 
                self.path = path
                self.size = size 
        roms = [] 
        allowed_extensions = self.allowed_extensions
        self.rom_directory = getattr(self.emulator_settings, "rom_directory")
        if self.rom_directory == "" or not os.path.exists(self.rom_directory):
            return []
        for file in os.listdir(self.rom_directory):
            if file.endswith(allowed_extensions) and os.path.isfile(os.path.join(self.rom_directory, file)):
                # Create a ROMFile object and append it to the roms list
                full_path = os.path.join(self.rom_directory, file)
                rom = ROMFile(name=file, path=full_path, size=os.path.getsize(full_path))
                roms.append(rom)
        self.total_pages = (len(roms) + self.results_per_page - 1) // self.results_per_page   
        self.total_pages_label.configure(text=f"/ {self.total_pages}")
        return roms 
    def delete_rom(self, path_to_rom):
        if not os.path.exists(path_to_rom):
            self.update_results()
            return 
        try:
            os.remove(path_to_rom)
        except Exception as error:
            messagebox.showerror("Error", f"An error prevented the ROM from being deleted:\n\n{error}")
        self.update_results()