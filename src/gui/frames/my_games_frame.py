import os
from pathlib import Path

import customtkinter

from gui.frames.game_list_frame import GameListFrame
from gui.libs import messagebox




class MyGamesFrame(GameListFrame):
    def __init__(self, master, event_manager, emulator_settings_object, game_extensions, scan_subdirectories=False):
        self.scan_subdirectories = scan_subdirectories
        self.total_pages = None
        self.emulator_settings = emulator_settings_object
        self.game_extensions = game_extensions
        self.update_in_progress = False
        super().__init__(master=master, event_manager=event_manager)


    def get_game_list(self):
        games = []
        if not (self.emulator_settings.game_directory.exists() and self.emulator_settings.game_directory.is_dir()):
            return []
        if self.scan_subdirectories:
            return self.get_current_roms_from_subdirectories()
        for file in self.emulator_settings.game_directory .iterdir():
            if file.is_file() and file.suffix in self.game_extensions:
                # Create a ROMFile object and append it to the roms list
                games.append(file.name)
        
        return {
            "result": games,
        }
    
    def get_current_roms_from_subdirectories(self):
        games = []

        for _, _, files in self.emulator_settings.game_directory.walk():
            for file in files:
                if file.suffix in self.game_extensions and file.is_file():
                    games.append(file.name)
        return {
            "result": games,
        }

    def delete_rom(self, path_to_rom):
        if not os.path.exists(path_to_rom):
            self.update_results()
            return
        if not messagebox.askyesno(self.winfo_toplevel(), "Delete ROM", f"This will delete the ROM located at: \n\n{path_to_rom}\nThis action cannot be undone. Are you sure you wish to continue?"):
            return
        try:
            os.remove(path_to_rom)
        except Exception as error:
            messagebox.showerror("Error", f"An error prevented the ROM from being deleted:\n\n{error}")
        self.searched_roms = self.get_current_roms()
        self.refresh_results()
