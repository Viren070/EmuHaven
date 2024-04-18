import os
import sys

from gui.windows.emulator_manager import EmulatorManager
from settings.app_settings import load_customtkinter_themes


if __name__ == "__main__":
    if len(sys.argv) > 1:
        from cli import handle_cli_args
        handle_cli_args(sys.argv[1:])
    else:
        load_customtkinter_themes(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "themes"))
        App = EmulatorManager(os.path.dirname(os.path.realpath(__file__)))
        App.mainloop()
