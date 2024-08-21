import cli
import sys
from core.utils.logger import Logger

logger = Logger(__name__).get_logger()

if __name__ == "__main__":
    logger.info("Starting the application with arguments: %s", sys.argv[1:])
    if len(sys.argv) > 1:
        logger.info("Starting the application in CLI mode")
    else:
        logger.info("Starting the application in GUI mode")
        from gui.emulator_manager import EmulatorManager
        app = EmulatorManager()
        app.mainloop()
