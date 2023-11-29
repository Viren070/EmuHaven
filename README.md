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
![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/0ea2e7d0-43f5-4ad0-a523-5959ca8a841a)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/1a86bc03-555e-414e-a063-f3ec9e02af14)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/f31767b9-689d-4de6-a468-266525b6eb5a)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/8e098494-a1a1-481c-a73c-46d2b5a1f040)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/1ed421bd-cd16-4820-90e1-9fdefbb2847e)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/01491588-c2ab-41d7-b9e7-d7b2ffd983d4)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/b9626aaa-e959-41d5-a203-7eee1d1c02eb)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/dc8cbc5b-2cab-434e-bf05-5ab131b11d7f)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/a57140aa-9262-489e-9fde-e2c363a1521e)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/771e601e-a0f7-4828-95cd-ad5fb3d0b85a)






## [Early Access Source](https://github.com/pineappleEA/pineapple-src) | [Firmware](https://archive.org/download/nintendo-switch-global-firmwares) | [Keys](https://github.com/Viren070/SwitchFirmwareKeysInstaller/tree/main/Keys)  | [Dolphin](https://github.com/Viren070/dolphin-beta-downloads) | [Dolphin ROMs](https://myrient.erista.me/)
