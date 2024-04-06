import sys
import os
import threading


VERSION = "0.1"

def display_help():
    print("Available commands:")
    print("help - Display available commands and their functions")
    print("version - Display the Emulator Manager CLI version")
    print("launch - Launch an emulator")
    print(f"    Usage: {os.path.realpath(__file__)} --launch <emulator_name> [-update]")
    print("    emulator_name: yuzu, ryujinx, dolphin")
    print("    -update (optional): Update the emulator before launching")

def handle_launch(arguments):
    print(arguments)
    def launch_yuzu():
        from emulators.yuzu import Yuzu
        progress_window.yuzu = Yuzu(progress_window, progress_window.settings, progress_window.metadata)
        progress_window.yuzu.main_progress_frame = progress_window.progress_frame
        def launch():
            progress_window.yuzu.launch_yuzu_handler(progress_window.settings.yuzu.current_yuzu_channel.lower().replace(" ", "_"), skip_update, wait_for_exit=False)
            progress_window.after(1000, progress_window.destroy)
            sys.exit(0)
        threading.Thread(target=launch).start()

    def launch_ryujinx():
        from emulators.ryujinx import Ryujinx
        progress_window.ryujinx = Ryujinx(progress_window, progress_window.settings, progress_window.metadata)
        progress_window.ryujinx.main_progress_frame = progress_window.progress_frame
        def launch():
            progress_window.ryujinx.launch_ryujinx_handler(skip_update, wait_for_exit=False)
            progress_window.after(1000, progress_window.destroy)
            sys.exit(0)
        threading.Thread(target=launch).start()

    def launch_dolphin():
        from emulators.dolphin import Dolphin   
        progress_window.dolphin = Dolphin(progress_window, progress_window.settings, progress_window.metadata)
        progress_window.dolphin.main_progress_frame = progress_window.progress_frame
        def launch():
            progress_window.dolphin.launch_dolphin_handler(progress_window.settings.dolphin.current_channel, skip_update, wait_for_exit=False)
            progress_window.after(1000, progress_window.destroy)
            sys.exit(0)
        threading.Thread(target=launch).start()
        
    from settings.settings import Settings
    from settings.metadata import Metadata
    from gui.windows.progress_window import ProgressWindow
    progress_window = ProgressWindow(title="Updating")
    progress_window.settings = Settings(progress_window, os.path.dirname(os.path.realpath(__file__)))
    progress_window.metadata = Metadata(progress_window, progress_window.settings)
    if arguments:
        skip_update = True
        if len(arguments) > 1 and arguments[1] == "-update":
            skip_update = False
        match arguments[0]:
            case "yuzu":
                progress_window.after(1000, launch_yuzu)
            case "ryujinx":
                progress_window.after(1000, launch_ryujinx)
            case "dolphin":
                progress_window.after(1000, launch_dolphin)
            case _:
                print(f"Unknown emulator: {arguments[0]}")
                display_help()
   
        progress_window.mainloop()
    else:
        print("No emulator name passed")
        display_help()
    
def handle_cli_args(arguments):
    match arguments[0]:
        case "--help":
            display_help()
        case "--version": 
            print(f"Emulator Manager Version: {VERSION}")
        case "--launch":
            handle_launch(arguments[1:])
        case _:
            print("Unknown command")
            display_help()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        handle_cli_args(arguments)
    else:
        print("No arguements passed")
