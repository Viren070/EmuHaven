import customtkinter

from gui.frames.game_list_frame import GameListFrame
from gui.libs.CTkMessagebox import messagebox


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
            "result": (games,),
        }

    def add_game_to_frame(self, game, row_counter):
        def convert_bytes_to_suitable_unit(bytes):
            if bytes < 1024:
                return f"{bytes} B"
            elif bytes < 1024 * 1024:
                return f"{bytes / 1024:.2f} KB"
            elif bytes < 1024 * 1024 * 1024:
                return f"{bytes / 1024 / 1024:.2f} MB"
            elif bytes < 1024 * 1024 * 1024 * 1024:
                return f"{bytes / 1024 / 1024 / 1024:.2f} GB"
            else:
                return f"{bytes / 1024 / 1024 / 1024 / 1024:.2f} TB"

        game_frame = customtkinter.CTkFrame(self.result_frame, corner_radius=7, border_width=1, fg_color="transparent", height=200)
        game_frame.grid(row=row_counter, column=0, sticky="ew", pady=10, padx=10)
        game_frame.grid_columnconfigure(0, weight=1)

        game_label = customtkinter.CTkLabel(game_frame, text=game, font=("Arial", 15), anchor="w")
        game_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)

        game_size = (self.emulator_settings.game_directory / game).stat().st_size
        game_size_label = customtkinter.CTkLabel(game_frame, text=convert_bytes_to_suitable_unit(game_size), font=("Arial", 12), anchor="w")
        game_size_label.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)

        delete_button = customtkinter.CTkButton(game_frame, text="Delete", width=100, command=lambda: self.delete_game(game))
        delete_button.grid(row=0, column=2, padx=5, pady=2)

    def get_current_roms_from_subdirectories(self):
        games = []

        for _, _, files in self.emulator_settings.game_directory.walk():
            for file in files:
                if file.suffix in self.game_extensions and file.is_file():
                    games.append(file.name)
        return {
            "result": games,
        }

    def delete_game(self, game):
        game_path = self.emulator_settings.game_directory / game
        if not game_path.exists():
            self.get_game_list_button_event()
        if messagebox.askyesno(self.winfo_toplevel(), "Delete ROM", f"This will delete the game located at: \n\n{game_path}\nThis action cannot be undone. Are you sure you wish to continue?", icon="warning") != "yes":
            return
        try:
            game_path.unlink()
        except Exception as error:
            messagebox.showerror(self.winfo_toplevel(), "Delete Game", f"An error prevented the game from being deleted:\n\n{error}")
        self.get_game_list_button_event()
