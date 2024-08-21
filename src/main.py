import cli
import sys
from core.utils.logger import Logger
from core.settings import Settings
import customtkinter 
logger = Logger(__name__).get_logger()


def load_customtkinter_settings():
    logger.info("Loading themes and appearance mode")
    settings = Settings()
    theme = settings.colour_theme_path
    appearance = settings.appearance_mode
    customtkinter.set_appearance_mode(appearance)
    customtkinter.set_default_color_theme(str(theme))

if __name__ == "__main__":
    logger.info("Starting the application with arguments: %s", sys.argv[1:])
    if len(sys.argv) > 1:
        logger.info("Starting the application in CLI mode")
    else:
        logger.info("Starting the application in GUI mode")
        load_customtkinter_settings()
        logger.info("Building the GUI")
        from gui.emulator_manager import EmulatorManager
        app = EmulatorManager()
        logger.info("Running the GUI")
        app.mainloop()
