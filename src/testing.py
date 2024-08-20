from core.utils.myrient import get_list_of_games

from core.paths import Paths
from core.settings import Settings
from core.versions import EmulatorVersions
from core.cache import Cache

from core.emulators.dolphin.runner import Dolphin

class TempProgressHandler:
    def __init__(self):
        self.value = 0

    def report_progress(self, value):
        print(value)
        
    def report_success(self):
        print("Success")
        
    def report_error(self, error):
        print(error)
        
    def should_cancel(self):
        return False
    
    def cancel(self):
        pass
    

a = Paths()
print(a.app_dir)
print(a.cache_dir)
print(a.versions_file)
print(a.settings_file)
print(a.asset_path)
print(a.get_image_path("yuzu_logo"))

settings = Settings()
versions = EmulatorVersions()

d = Dolphin(settings, versions)
release = d.get_dolphin_release()
print(d.download_release(release["release"], progress_handler=TempProgressHandler()))

"""
FOR FRONTEND 

import customtkinter
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip
def show_messagebox(title, message, icon, option_1, option_2=None, option_3=None):
    response = CTkMessagebox(
        title=title,
        message=message,
        icon=icon,
        option_1=option_1,
        option_2=option_2,
        option_3=option_3,
        fade_in_duration=150,
        justify="center",
        sound=True,
    )





a = customtkinter.CTk()
b = customtkinter.CTkButton(a, text="Test", command=lambda: show_messagebox("Test", "Test", "info", "OK"))
CTkToolTip(b, message="Test")
b.pack()
a.mainloop()
"""


"""  
plan:

for both cli and gui, we need to have a progress handler class. 
it has a report progress method that takes a decimal value between 0 and 1.
It then uses the update_display method to update the display with the new value.
The display can be a progress bar (customtkinter class) or a text display.

Only the core logic should be defined in core. 
No decision making should be done in core.
The core should be able to be used by any frontend.


SETTINGS: 
Have the config for each emulator to be configured within the emulator section in the frontend. 

Each Emulator has its config class that inherits from the base config class.
The base config class has the save method. 
The load method is present in all subclasses and will only load the config for that specific emulator.

Some settings need to be synced with the emulator settings. 
e.g. portable mode will have to be detected by the logic in core. 
Frontend will have option to enable portable mode. 
If portable mode is enabled, then runner needs to consider that when installing/updating the emulator. 
We need to avoid deleting the user data folder as it will be stored within the folder that the emulator is installed in.
We can create a backup of the user folder and restore it when the emulator is updated.
or we can change the way we install the emulator by extracting the files one by one.

All emulator settings should be synced settings as they are settings for that emulator so changing these settings should affect the emulator



Do we use the emulator settings class within the runner to decide on operations 
or do we rely on the interfaces to pass in the parameters to the runner?



"""
