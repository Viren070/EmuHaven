# Emulator-Manager

A program that will help manage your emulators, currently supports: 

 - Dolphin
 - Yuzu 

## Features

- Allows you to keep automatic backups of your data 
- Import / Export Data
- Delete all data or just saved data. 
- For yuzu (and Ryujinx) specifically :
  - it will automatically prompt you to install the latest firmware and keys to your device when launched*
  - Built-in [downloader](https://github.com/Viren070/SwitchFirmwareKeysInstaller) that allows you to switch firmware and key versions all the way back to 1.0.0

*Requires paths to firmware and keys to be set in settings. This is done by default if you download the -resources-included.exe and requires no further setup.

## How to download 
Download the latest release from [here](https://github.com/Viren070/Emulator-Manager/releases/latest)

You can choose either the:
- Emulator Manager v0.x.x-resources
  - Has the required resource files (Installers, firmware, keys)
  - Much larger file size 
- Emulator Manager v0.x.x
  - Does not have the required resource files.
  - These must be installed separately and paths must be set in the settings. 
  - Has a much smaller file size

 The .exe will take longer to launch but has no clutter. The .zip includes a smaller sized .exe and will launch faster but has a lot of files. 

 If you download the .exe file, you will be unable to change the [resource files within the exe itself](https://github.com/Viren070/Emulator-Manager#resource-files). You can still set the paths in the settings to other files but that will mean that the resource files within the exe are unused and are wasting space. 
 ## Resource Files
  (as of v0.6.5)
- Firmware 16.0.3 (Rebootless Update 2).zip
- Keys 16.0.3.zip
- yuzu_install.exe v0.9
- Dolphin 5.0-19870.zip 
