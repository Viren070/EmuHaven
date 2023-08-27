import os

from gui.emulator_manager import EmulatorManager
from settings.settings import Settings


def main():
    a=Settings()
    a.define_image_paths(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images"))  #  modify code such that settings file is checked for image paths in settings.py 
    EmulatorManager()
    
if __name__ == "__main__":
    main()