from pathlib import Path

import customtkinter

from core import constants
from core.utils.files import extract_zip_archive_with_progress
from core.utils.myrient import get_game_download_url
from core.utils.web import download_file_with_progress
from gui.frames.my_games_frame import MyGamesFrame
from gui.frames.myrient_game_list_frame import MyrientGameListFrame
from gui.libs import messagebox
from gui.progress_handler import ProgressHandler


class DolphinROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, settings, cache, event_manager):
        super().__init__(master, corner_radius=7, anchor="nw")
        self.master = master
        self.event_manager = event_manager
        self.roms = None
        self.cache = cache
        self.settings = settings
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()

    def build_frame(self):
        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.add("Wii ROMs")
        self.add("GameCube ROMs")
        self.add("Downloads")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Wii ROMs").grid_columnconfigure(0, weight=1)
        self.tab("Wii ROMs").grid_rowconfigure(0, weight=1)
        self.tab("GameCube ROMs").grid_columnconfigure(0, weight=1)
        self.tab("GameCube ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Downloads").grid_columnconfigure(0, weight=1)
        self.tab("Downloads").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = MyGamesFrame(master=self.tab("My ROMs"), emulator_settings_object=self.settings.dolphin, game_extensions=[".wbfs", ".iso", ".rvz", ".gcm", ".gcz", ".ciso"], event_manager=self.event_manager)
        self.current_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.wii_roms_frame = MyrientGameListFrame(master=self.tab("Wii ROMs"), event_manager=self.event_manager, cache=self.cache, myrient_path=constants.Dolphin.MYRIENT_WII_PATH.value, console_name="nintendo_wii", download_button_event=self.download_game_button_event)
        self.wii_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.gamecube_roms_frame = MyrientGameListFrame(master=self.tab("GameCube ROMs"), event_manager=self.event_manager, cache=self.cache, myrient_path=constants.Dolphin.MYRIENT_GAMECUBE_PATH.value, console_name="nintendo_gamecube", download_button_event=self.download_game_button_event)
        self.gamecube_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.downloads_frame = customtkinter.CTkScrollableFrame(self.tab("Downloads"))
        self.downloads_frame.grid_columnconfigure(0, weight=1)
        self.downloads_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    def download_game_button_event(self, game, myrient_path):
        self.set("Downloads")
        self.downloads_in_progress += 1
        download_frame = customtkinter.CTkFrame(self.downloads_frame, corner_radius=7, border_width=1, fg_color="transparent", height=50)
        download_frame.grid(row=self.downloads_in_progress - 1, column=0, sticky="ew", pady=5, padx=5)
        download_frame.grid_columnconfigure(0, weight=1)

        progress_handler = ProgressHandler(download_frame)
        
        self.event_manager.add_event(
            event_id="download_game",
            func=self.download_game,
            kwargs={"game": game, "progress_handler": progress_handler, "myrient_path": myrient_path},
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Game Download", "An unexpected error occurred while attempting to download this game.")],
            completion_functions=[lambda frame=download_frame: frame.destroy()],
        )
        
    def download_game(self, game, progress_handler, myrient_path):
        progress_handler.start_operation(title=game, total_units=0, units="MiB", status="Downloading...")
        download_result = download_file_with_progress(
            download_url=get_game_download_url(game, myrient_path=myrient_path),
            download_path=Path(self.settings.dolphin.game_directory) / f"{game}.zip",
            progress_handler=progress_handler
        )
        if not download_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Game Download", f"An error occurred while attempting to download this game\n\n{download_result['message']}"),
                }
            }
        
        progress_handler.start_operation(title=game, total_units=0, units="MiB", status="Extracting...")
        extract_result = extract_zip_archive_with_progress(
            zip_path=download_result["download_path"],
            extract_directory=Path(self.settings.dolphin.game_directory),
            progress_handler=progress_handler
        )
        download_result["download_path"].unlink(missing_ok=True)
        if not extract_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Game Download", f"An error occurred while attempting to extract this game\n\n{extract_result['message']}"),
                }
            }
        
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Game Download", "The game was successfully downloaded"),
            }
        }
