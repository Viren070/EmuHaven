import os

from gui.windows.emulator_manager import EmulatorManager
from settings.app_settings import load_customtkinter_themes

def main():
    load_customtkinter_themes(os.path.join(os.path.dirname(os.path.realpath(__file__)),"themes"))
    EmulatorManager(os.path.dirname(os.path.realpath(__file__)))
    
if __name__ == "__main__":
    main()