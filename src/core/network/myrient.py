from core.config.constants import Myrient
from core.network.web import get_all_files_from_page
from urllib.parse import quote, unquote

def get_list_of_games(myrient_path):
    scrape_result = get_all_files_from_page(url=Myrient.BASE_URL.value + myrient_path, file_ext=".zip")
    if not scrape_result["status"]:
        return scrape_result
    scrape_result["games"] = []
    for file in scrape_result["files"]:
        # Remove the base URL and the myrient path from the filename
        # this will return a list of filenames that are relative to the myrient path
        scrape_result["games"].append(unquote(file.replace(Myrient.BASE_URL.value + myrient_path, "").replace(".zip", "")))
    
    return scrape_result


def get_game_download_url(game_name, myrient_path):
    return Myrient.BASE_URL.value + myrient_path + f"{quote(game_name)}.zip"