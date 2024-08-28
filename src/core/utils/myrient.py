from core.constants import Myrient
from core.utils.web import get_all_files_from_page


def get_list_of_games(myrient_path):
    scrape_result = get_all_files_from_page(url=Myrient.BASE_URL.value + myrient_path, file_ext=".zip")
    if not scrape_result["status"]:
        return scrape_result
    scrape_result["games"] = []
    for file in scrape_result["files"]:
        # Remove the base URL and the myrient path from the filename
        # this will return a list of filenames that are relative to the myrient path
        scrape_result["games"].append(file.replace(Myrient.BASE_URL.value + myrient_path, ""))
    
    return scrape_result
