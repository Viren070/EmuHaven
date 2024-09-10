import json
from pathlib import Path

import customtkinter

from core.utils.web import download_file
from gui.frames.game_list_frame import GameListFrame
from gui.libs import messagebox
from gui.progress_handler import ProgressHandler
from gui.windows.saves_browser import SavesBrowser

class MySwitchGamesFrame(GameListFrame):
    def __init__(self, master, cache, assets, event_manager, emulator_name, emulator_object):
        self.cache = cache
        self.assets = assets
        self.emulator_name = emulator_name
        self.event_manager = event_manager
        self.fetching_titledb = False
        self.titledb = {}
        self.game_id_name_map = {}
        self.emulator_object = emulator_object
        super().__init__(master, event_manager)
        self.progress_handler = ProgressHandler(self.winfo_toplevel(), widget="window")
        

    def get_game_list(self):
        user_directory = self.emulator_object.get_user_directory()
        title_ids = []
        match self.emulator_name:
            case "yuzu":
                title_id_dir = user_directory / "cache" / "game_list"
                if title_id_dir.is_dir() and any(title_id_dir.iterdir()):
                    for item in title_id_dir.iterdir():
                        if item.is_file() and [".pv", ".txt"] == item.suffixes:
                            title_ids.append(item.name.split(".")[0])
            case "ryujinx":
                title_id_dir = user_directory / "games"
                if title_id_dir.is_dir() and any(title_id_dir.iterdir()):
                    
                    for item in title_id_dir.iterdir():
                        if item.is_dir():
                            title_ids.append(item.name)
            case _:
                raise ValueError(f"Emulator name {self.emulator_name} not recognized.")
        if not title_ids:
            return {
                "result": (title_ids,),
                "message": {
                    "function": messagebox.showinfo,
                    "arguments": (self.winfo_toplevel(), "Empty", "No games were found in your user directory. Make sure you have launched the game at least once.")
                }
            }
        return {
            "result": (title_ids, ),
        }
    
    def add_game_to_frame(self, game, row_counter):
        # game can either be a title ID or a game name
        title_id = None
        name = None
        
        if game.isnumeric():
            title_id = game
        else:
            name = game
        
        
        if title_id:
            # if game is title ID, get name from title ID
            meta = self.get_title_meta_from_id(title_id)
            if meta is None:
                return
        elif name:
            # if game is the name, get title ID from mapping and then get meta
            title_id = self.game_id_name_map.get(name, None)
            if not title_id:
                return
            meta = self.get_title_meta_from_id(title_id)
    
        name = meta["name"]
        description = meta["description"]
        icon_url = meta["iconUrl"]
        # add the title id and name to the mapping 
        self.game_id_name_map[name] = title_id
        self.game_id_name_map[title_id] = name
        game_frame = customtkinter.CTkFrame(self.result_frame)
        game_frame.grid(row=row_counter, column=0, padx=10, pady=5, sticky="nsew")
        game_frame.grid_columnconfigure(1, weight=1)  # Allow the second column to expand

        # Game cover button
        game_cover = customtkinter.CTkButton(game_frame, hover_color=None, border_width=0, text="", image=self.assets.placeholder_icon)
        game_cover.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="nsew")  # Span 3 rows
        self.event_manager.add_event(
            event_id=f"download_icon_{title_id}",
            func=self.download_icon,
            kwargs={"title_id": title_id, "icon_url": icon_url, "button": game_cover},
            completion_funcs_with_result=[self.update_game_cover],
        )

        # Game name label
        game_name_label = customtkinter.CTkLabel(game_frame, text=name, font=customtkinter.CTkFont("Arial", 16))
        game_name_label.grid(row=0, column=1, padx=10, columnspan=2, pady=5, sticky="nsew")

        # Game description text box
        game_desc_text = customtkinter.CTkTextbox(game_frame, height=130, border_width=0, fg_color="transparent")
        game_desc_text.insert(customtkinter.END, description)
        game_desc_text.configure(state="disabled")  # Make the text box read-only
        game_desc_text.grid(row=1, column=1, padx=10, columnspan=2, pady=5, sticky="nsew")

        # Download mods button
        download_mods_button = customtkinter.CTkButton(game_frame, text="Download Mods", height=50, font=("Arial", 14))
        download_mods_button.configure(command=lambda game=game, button=download_mods_button: self.download_mods_button_event(game, button))
        download_mods_button.grid(row=2, column=1, padx=10, pady=10, sticky="sw")

        # Download saves button
        download_saves_button = customtkinter.CTkButton(game_frame, text="Download Saves", height=50, font=("Arial", 14))
        download_saves_button.configure(command=lambda game=game, button=download_saves_button: self.download_saves_button_event(game, button))
        download_saves_button.grid(row=2, column=2, padx=10, pady=10, sticky="se")
        
        # remove title ID from list and add name instead
        self.game_list.remove(game)
        self.game_list.append(name)

    def download_icon(self, title_id, icon_url, button):
        cache_query_result = self.cache.get_data_from_cache(f"{title_id}_icon")
        if cache_query_result:
            icon_path = cache_query_result["data"]
            return {
                "result": (button, icon_path, )
            }
        download_result = download_file(icon_url, Path(f"{title_id}.png").resolve())
        if not download_result["status"]:
            return {}
        
        icon_path = download_result["download_path"]
        add_to_cache_result = self.cache.add_custom_file_to_cache(f"{title_id}_icon", icon_path)
        if not add_to_cache_result["status"]:
            return {}
        
        cache_query_result = self.cache.get_data_from_cache(f"{title_id}_icon")
        if not cache_query_result:
            return {}
        icon_path = cache_query_result["data"]
        
        return {
            "result": (button, icon_path, )
        }
    
    def update_game_cover(self, button, image):
        button.configure(image=self.assets.create_image(image, (224, 224)))
        
    def get_title_meta_from_id(self, title_id):
        self.assert_titledb()
        return self.titledb.get(str(title_id))

    def assert_titledb(self):
        cache_query = self.cache.get_data_from_cache("TitleDB")
        if not cache_query:
            self.start_titledb_download_event()
        elif not self.titledb:
            titledb_path = cache_query["data"]
            with open(titledb_path, "r", encoding="utf-8") as f:
                try:
                    self.titledb = json.load(f)
                except json.JSONDecodeError:
                    self.start_titledb_download_event()

    def start_titledb_download_event(self):
        if self.fetching_titledb:
            return
        self.fetching_titledb = True
        self.event_manager.add_event(
            event_id="fetch_titledb",
            func=self.download_titledb,
            kwargs={},
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An unknown error occured while attempting to download the titleDB.")],
            completion_functions=[lambda: setattr(self, "fetching_titledb", False)]
        )
        
    def download_titledb(self):
        self.progress_handler.start_operation("Downloading TitleDB", total_units=0, units="MiB", status="Downloading...")
        download_result = self.emulator_object.download_titledb(progress_handler=self.progress_handler)
        
        if not download_result["status"]:
            self.fetching_titledb = False
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"An error occured while attempting to download the TitleDB:\n\n{download_result['message']}"),
                }
            }
        download_path = download_result["download_path"]

        move_to_cache_result = self.cache.add_custom_file_to_cache("TitleDB", download_path)
        if not move_to_cache_result["status"]:
            self.fetching_titledb = False
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"An error occured while attempting to move the TitleDB to the cache:\n\n{move_to_cache_result['message']}"),
                }
            }

        cache_lookup_result = self.cache.get_data_from_cache("TitleDB")
        if not cache_lookup_result:
            self.fetching_titledb = False
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", "An error occured while attempting to lookup the TitleDB in the cache."),
                }
            }

        titledb_path = cache_lookup_result["data"]
        with open(titledb_path, "r", encoding="utf-8") as f:
            self.titledb = json.load(f)

        self.fetching_titledb = False
        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self.winfo_toplevel(), "Success", "TitleDB downloaded successfully.")
            }
        }
        
    def download_mods_button_event(self, game, button):
        button.configure(state="disabled")
        self.open_mod_downloader(game)
        button.configure(state="normal")
        
    def open_mod_downloader(self, game):
        pass 
    
    def download_saves_button_event(self, game, button):
        button.configure(state="disabled")
        all_saves_cache_query = self.cache.get_json_data_from_cache("switch_saves")
        if not all_saves_cache_query:
            self.event_manager.add_event(
                event_id="fetch_switch_saves",
                func=self.get_saves_list,
                kwargs={},
                completion_functions=[lambda: self.open_save_browser(game, button), lambda: button.configure(state="normal")],
                error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "An error occurred while attempting to fetch the saves list.")],
            )
        else:
            self.open_save_browser(game, button)

    def open_save_browser(self, game, button):
        game_name = self.game_id_name_map.get(game, game)
        save_browser = SavesBrowser(master=self.winfo_toplevel(), title=game_name, saves_list=self.get_saves_for_game(game), event_manager=self.event_manager)
        save_browser.wait_window()
        button.configure(state="normal")
        
    def get_saves_for_game(self, game):
        all_saves_cache_query = self.cache.get_json_data_from_cache("switch_saves")
        if not all_saves_cache_query:
            return []

      
        title_id = game
        all_saves = all_saves_cache_query["data"]
        game_saves = [save for save in all_saves if title_id in save]
        return game_saves
        
    def get_saves_list(self):
        saves_result = self.emulator_object.get_saves_list()
        if not saves_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self.winfo_toplevel(), "Error", f"An error occurred while attempting to fetch the saves list:\n\n{saves_result['message']}"),
                }
            }
        saves = saves_result["saves"]
        
        self.cache.add_json_data_to_cache("switch_saves", saves)
        
        

                            
