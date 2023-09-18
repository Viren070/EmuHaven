# Emulator Manager



A program that will help manage your emulators, currently supports: 

 - Dolphin
 - Yuzu

Only tested on Windows 10 and 11, not sure if it will work on anything else

## Download 

Download the latest release from [here](https://github.com/Viren070/Emulator-Manager/releases/latest) by scrolling to the bottom and downloading the exe from the assets (Use [0.9.3](https://github.com/Viren070/Emulator-Manager/releases/tag/v0.9.3) for playing in places with limited internet access for now. I'll add back ways to use files from other sources to install stuff in a future update)

## Features

### Dolphin 

- Download any game you want for the GameCube or Wii directly from the manager. It is easy to use and you can browse or search for whatever game you want. (Will come in 0.11.0, you can download the alpha release [here](https://github.com/Viren070/Emulator-Manager/releases/tag/v0.9.3).)
- Download the latest beta release of dolphin through the manager and keep Dolphin updated. 
- Manage your user data and export it to any directory


### Yuzu 

An all in one launcher for yuzu. Allows you to switch between mainline and early accesd and keeps both versions updated. It can download the latest firmware and keys from the internet. 

- Allows you to install, delete and launch yuzu
- Can switch channels between mainline and early access through a dropdown menu in the corner
- Will automatically update yuzu when you launch it
- Will detect any missing firmware or keys and then automaticaly install them for you. 
- Manage your user data, you can choose to specifically delete/import/export certain folders.


### App

- Through the settings page, you can customise the app to your liking with the several themes to choose from. These were taken from:
  - [avalaon60/ctk_theme_builder](https://github.com/avalon60/ctk_theme_builder/tree/develop/user_themes)
  - [a13xe/CTkThemesPack](https://github.com/a13xe/CTkThemesPack)

## How to use

Should be straight forward, you just click the buttons. You can shift-click the launch buttons to immediately launch the emulator instead of checking for updates first. 

For the downloader on yuzu. You need to click Options, then Attempt version fetch. This will probably be changed if I get around to re-doing the options menu but for now, you'll have to manually fetch the versions.

The GitHub login feature is optional and should only be used if you ran out of API requests and need more immediately. It will grant you 5000 requests per hour. The user access token is not stored and this means that you will have to login again when you next launch the app if you want 5000 requests again.

The settings for dolphin and yuzu are used to change where yuzu/dolphin is installed and where your user data is stored (if you are using the portable version). You can only change the install location if you are not using the yuzu installer, otherwise it will always install in the default location. 

### Images
![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/9b421e17-65a0-4a89-8178-b5c25754ae74)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/1ea40ed6-9e42-4ef0-8804-4f84090b0109)
![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/2148d447-80ce-49fa-8707-7f43234c3620)
![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/2b86392c-7694-42f8-b6e7-4a9610f74256)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/0a6361b2-5b54-4801-a87c-69d32c999ed4)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/0093c941-fd3e-4ed6-9d26-b4265aa22bcf)



## [Early Access Source](https://github.com/pineappleEA/pineapple-src) | [Firmware](https://archive.org/download/nintendo-switch-global-firmwares) | [Keys](https://github.com/Viren070/SwitchFirmwareKeysInstaller/tree/main/Keys)  | [Dolphin](https://github.com/Viren070/dolphin-beta-downloads)
3,669 loc 





