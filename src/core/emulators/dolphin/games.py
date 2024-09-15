from core.network.myrient import get_list_of_games
from core.config.constants import Dolphin

class DolphinGames:
    def __init__(self, settings):
        self.settings = settings
        
    def get_current_games_list(self):
        game_list = []
        for game in self.settings.dolphin.game_directory.iter_dir():
            if any(game.suffix == ext for ext in Dolphin.GAME_FILE_EXTENSIONS.value):
                game_list.append(game)
        return game_list
    
    def get_all_games_download_links(self):
        return get_list_of_games(Dolphin.MYRIENT_PATH.value)
    
    def get_paginated_games_list(self, page_number):
        all_games = self.get_all_games_download_links()
        start = (page_number - 1) * 10
        end = start + 10
        return {
            "games": all_games[start:end],
            "ids": list(range(start, end))
        }
        