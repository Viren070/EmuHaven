from MainScreen import MainScreen, load_appearance_settings
from colorama import just_fix_windows_console


if __name__ == "__main__":
    just_fix_windows_console()
    load_appearance_settings()
    app = MainScreen()