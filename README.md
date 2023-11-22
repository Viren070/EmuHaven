# Emulator Manager



A program that will help manage your emulators, currently supports: 

 - Dolphin
 - Yuzu
 - Ryujinx

Only tested on Windows 10 and 11, not sure if it will work on anything else

## Download 

Download the latest release from [here](https://github.com/Viren070/Emulator-Manager/releases/latest) by scrolling to the bottom and downloading the exe from the assets. 

Note: Windows Defender will detect the file as a virus since the file is unsigned. This is a false positive and can be ignored. If you don't want to run the exe, you can [run the source code](https://github.com/Viren070/Emulator-Manager/tree/main#building-yourself)

## Features

You can shift-click any install button to use a custom archive. You can also shift click the launch button to skip updating the emulator and launch immediately. 

### Dolphin 

- Download any game you want for the GameCube or Wii directly from the manager. It is easy to use and you can browse or search for whatever game you want. 
- Download the latest beta or development build of dolphin and keep it updated through the manager.
- Manage your user data and export it to any directory


### Yuzu 

An all in one launcher for yuzu. Allows you to switch between mainline and early accesd and keeps both versions updated. It can download multiple versions of firmware and keys from the internet. 

- Allows you to install, delete and launch yuzu
- Can install yuzu in any directory, can be changed in the settings.
- Can switch channels between mainline and early access through a dropdown menu in the corner
- Will automatically update yuzu when you launch it
- Will detect any missing firmware or keys and then automaticaly install them for you.
- Can switch between different versions for firmware and keys.
- Manage your user data, you can choose to specifically delete/import/export certain folders.
- Can choose to still use the Yuzu installer (liftinstall) when launching or installing yuzu.

### Ryujinx 

Same features as Yuzu, where applicable.

### App

- Through the settings page, you can customise the app to your liking with the several themes to choose from. These were taken from:
  - [avalaon60/ctk_theme_builder](https://github.com/avalon60/ctk_theme_builder/tree/develop/user_themes)
  - [a13xe/CTkThemesPack](https://github.com/a13xe/CTkThemesPack)

## How to use

Should be straight forward, you just click the buttons. You can shift-click the launch buttons to immediately launch the emulator instead of checking for updates first. 

You can also shift click the Install buttons.  This will allow you to use a local source for the install.

The GitHub login feature is optional and should only be used if you ran out of API requests and need more immediately. It will grant you 5000 requests per hour. The user access token is not stored and this means that you will have to login again when you next launch the app if you want 5000 requests again.

The settings for dolphin and yuzu are used to change where yuzu/dolphin is installed and where your user data is stored (if you are using the portable version). You can only change the install location if you are not using the yuzu installer, otherwise it will always install in the default location. 

## Building yourself 

### Requirements:
 - Latest version of python

1. Clone the repository or click the download ZIP button. 
2. Run
   ```
   pip install -r requirements.txt
   ```
3. You should be able to run main.py
4. To build the executable run:
   ```
   pyinstaller --noconfirm --onefile --windowed --name "Emulator Manager" --clean --add-data "%localappdata%/Programs/Python/Python312/Lib/site-packages/customtkinter;customtkinter/" --add-data src/assets;assets/  src/main.py
   ```
   - If you don't have pyinstaller, you can install it with `pip install pyinstaller`
   - You can replace `--onefile` with `--onedir`.
   - Replace the path to customtkinter as necessary
   
### Images
![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/b48d7b97-a4dd-45ae-b9a6-17cf8e65adfb)


![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/a0637a78-7307-4476-aa11-d2dd83882e94)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/ee2c7d8b-08b1-4407-96bf-cd8143f05d06)


![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/2b86392c-7694-42f8-b6e7-4a9610f74256)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/da785edf-9cb9-40c1-89f0-6af895f7ad53)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/81e77b74-2032-4cea-9aaf-e8554456b671)


## [Early Access Source](https://github.com/pineappleEA/pineapple-src) | [Firmware](https://archive.org/download/nintendo-switch-global-firmwares) | [Keys](https://github.com/Viren070/SwitchFirmwareKeysInstaller/tree/main/Keys)  | [Dolphin](https://github.com/Viren070/dolphin-beta-downloads) | [Dolphin ROMs](https://myrient.erista.me/)
