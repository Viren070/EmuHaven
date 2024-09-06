import sys
import time

import customtkinter

from core.assets import Assets
from core.cache import Cache
from core.paths import Paths
from core.settings import Settings
from core.utils.logger import Logger
from core.versions import Versions


logger = Logger(__name__).get_logger()

    


def load_customtkinter_settings(settings_object: Settings):
    theme = settings_object.colour_theme_path
    dark_mode = settings_object.dark_mode
    logger.info("Dark: %s", dark_mode)
    logger.info("Theme: %s", theme)
    customtkinter.set_appearance_mode("dark" if dark_mode else "light")
    customtkinter.set_default_color_theme(str(theme))

if __name__ == "__main__":
    logger.info("Starting the application with arguments: %s", sys.argv[1:])
    
    paths = Paths()
    settings = Settings(paths)
    versions = Versions(paths)
    cache = Cache(paths)
    
    args = sys.argv[1:]
    
    if args: 

        logger.info("Starting the application in CLI mode")
        
    else:
    
        try:
            assets = Assets(paths)
        except FileNotFoundError as e:
            logger.error("Failed to load assets: %s", e)
            sys.exit(1)
        
        logger.info("Starting the application in GUI mode")
    
        load_customtkinter_settings(settings)
        time_start = time.time()
        
        from gui.emulator_manager import EmulatorManager
        app = EmulatorManager(
            paths=paths,
            settings=settings,
            versions=versions,
            cache=cache,
            assets=assets
        )
        
        logger.info("GUI built in %s seconds", round(time.time() - time_start, 2))
        logger.info("Running the GUI")
        
        app.mainloop()
