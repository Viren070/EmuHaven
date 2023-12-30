# Emulator Manager



A program that will help manage your emulators, currently supports: 

 - Dolphin
 - Yuzu
 - Ryujinx
 - Xenia (as of 0.13.0)

Only tested on Windows 10 and 11, not sure if it will work on anything else

## Download 

Download the latest release from [here](https://github.com/Viren070/Emulator-Manager/releases/latest) by scrolling to the bottom and downloading the exe from the assets. 

Note: Windows Defender will detect the file as a virus since the file is unsigned. This is a false positive and can be ignored. If you don't want to run the exe, you can [run the source code](https://github.com/Viren070/Emulator-Manager/tree/main#building-yourself)

## Features

### Dolphin 

- Download the latest beta or development build of dolphin and keep it updated through the manager.
- Download any game you want for the GameCube or Wii directly from the manager. It is easy to use and you can browse or search for whatever game you want. 
- Manage your user data and export it to any directory

### Yuzu 

An all in one launcher for yuzu. Allows you to switch between mainline and early access and keeps both versions updated. It can download multiple versions of firmware and keys from the internet. 

- Allows you to install, delete and launch yuzu
- Can install yuzu in any directory, can be changed in the settings.
- Can switch channels between mainline and early access through a dropdown menu in the corner
- Will automatically update yuzu when you launch it
- Will detect any missing firmware or keys and then automaticaly install them for you.
- Can switch between different versions for firmware and keys.
- Manage your user data, you can choose to specifically delete/import/export certain folders.
- Can choose to still use the Yuzu installer (liftinstall) when launching or installing yuzu.
- Manage your games and install mods and saves for specific games.*
  
### Ryujinx 

- You can install, delete, or launch Ryujinx.
- You can change the installation location in the settings.
- When you launch Ryujinx, it will automatically attempt to update Ryujinx. This can be skipped by holding shift while clicking launch.
- Will detect firmware and keys and prompt you to install them for you if they are missing.
- You can switch between different versions of firmware and keys.
- Manage your user data, you can choose to specifically delete/import/export certain folders.
- Manage your games and install mods and saves for specific games.*

### App

- Through the settings page, you can customise the app to your liking with the several themes to choose from. These were taken from:
  - [avalaon60/ctk_theme_builder](https://github.com/avalon60/ctk_theme_builder/tree/develop/user_themes)
  - [a13xe/CTkThemesPack](https://github.com/a13xe/CTkThemesPack)

*Only downloading saves are currently supported. Downloading mods will be added soon. 

## Details 

This section contains the technical details and full coverage of all features of the app. It is still unfinished.

### `Play` Menu 

There will be an install, launch & delete button. Clicking the button will perform its respective and appropriate function. 
Holding shift while clicking the install button will allow you to use a custom archive to install the emulator. The archive needs to be in the appropriate format but any archive that was downloaded from the emulators official website will work. 
Holding shift while clicking the launch button wil skip updating the emulator and launch the emulator immediately.

The latest versions of most emulators are fetched using the GitHub API. The amount of requests you have left and the time left till it resets is shown in the app settings.

#### Dolphin

The dolphin menu has a dropdown menu in the top right corner which allows you to switch between development and beta release channels. Only one version of dolphin is installed at a time, so switching channels and then installing dolphin (either through the install button or updating) will overwrite the previous version.

#### Yuzu 

The yuzu menu has a dropdown menu in the top right corner which allows you to switch between early access and mainline builds. Two versions can be installed at a time so switching channels will not overwrite the other channels installation when you install again.

Within the folder that is selected as the installation directory, two folders are used for mainline and early access: `yuzu-windows-msvc` and `yuzu-windows-early-access-msvc` respectively.
If you want to be able to choose the asset that you want downloaded, create a feature request through an issue. 


Below the 3 main buttons, there is another section that contains two dropdown menus and one install button to the left of each dropdown menu. One row is for firmware and the other for keys. You can select a version to download from the dropdown menu and then click install to download and extract the file(s) to the correct directory.

If the shift key is held while clicking install, then you can use a custom firmware/key archive to install to the emulators directory instead. a .keys file will also work for keys.

If it is your first time launching the app, the dropdown menus will say `Click to fetch versions`. Upon clicking the dropdown menu, a request will be sent to the website hosting the firmware and keys and a dictionary collating the information about each version will be collected. Once it has been created, it will be stored in the cache file and the next time you launch the app the dropdown menu will have the available versions displayed. 
However, if the age of the cached data becomes more than 7 days old, it will not be used and you will have to click the dropdown menu to fetch the versions again.

#### Ryujinx 

The ryujinx menu has no dropdown menu (I could add one for the LDN builds, make a feature request through an issue if you want this to be added). 

Within the folder that is selected as the installation directory, a `publish` folder is used to store the builds of ryujinx.


Below the 3 main buttons, there is another section that contains two dropdown menus and one install button to the left of each dropdown menu. One row is for firmware and the other for keys. You can select a version to download from the dropdown menu and then click install to download and extract the file(s) to the correct directory.

If the shift key is held while clicking install, then you can use a custom firmware/key archive to install to the emulators directory instead. a .keys file will also work for keys.

If it is your first time launching the app, the dropdown menus will say `Click to fetch versions`. Upon clicking the dropdown menu, a request will be sent to the website hosting the firmware and keys and a dictionary collating the information about each version will be collected. Once it has been created, it will be stored in the cache file and the next time you launch the app the dropdown menu will have the available versions displayed. 
However, if the age of the cached data becomes more than 7 days old, it will not be used and you will have to click the dropdown menu to fetch the versions again.


### `Manage Data` Menu 

...

### `Manage ROMs` Menu

This menu contains a Tabview frame which as it suggests, allows you to display separate tabs.

#### Dolphin

Dokphin's Manage ROMs menu has 4 tabs. One called `My ROMs` which will show you the roms you currently have downloaded (provided that the correct path is provided in the settings). And it will display the size that it takes and a delete button next to it. 
The next 2 tabs allow you to download ROMs from Myrient. One tab for Wii ROMs and one for GameCube ROMS. 
If it is your first time launching the app, there will be a `Fetch ROMs` button in the top left corner of the tab. Upon clicking this, a request will be sent to the Myrient website and a list of all the links for ROMs will be collected. It will be added to the cache so next time you launch the app it will already be loaded. 
The age of the cached data is not considered currently, but I will add a check to see if the data is more than 14 days old. 

The last tab is the downloads tab which will show any ongoing downloads. 

#### Yuzu & Ryujinx 

Yuzu and Ryujinx have the same manage ROMs menu. 
The only tab is the tab for your current games.
Upon opening the manage ROMs menu for yuzu and ryujinx the presence of the [titlesDB](https://github.com/arch-box/titledb) will be checked for. If it is not present it will be downloaded and stored in the cache directory.
The methodology is as follows:
- Scan the relevant folder within the emulators user directory(`cache\game_list\` and `games` for yuzu and ryujinx respectively) and obtain a list of title IDs.
- Use this title ID to obtain all the relevant metadata using the eShop data from this 
- Grab the name, description and icon url for each title.
- Search the cache for the icon of each title and use the icon if available. If the icon has not been cached, then use a placeholder_icon for now and download the icon and update the image and cache it.
- Generate a frame for each title. The cover will take up the left side of the frame with the title and description alongisde the download saves and download mdos button to the right.

The icon for each game can be right clicked to choose a custom image as the cover. 

If you hold shift while right clicking the cover, the app will attempt to download the original icon again.

Upon clicking the download saves button, the presence of the list of all saves will be checked for in cache. If the list does not exist in the cache, then it will be fetched from https://new.mirror.lewd.wtf/archive/nintendo/switch/savegames/. 
Using the games title ID, the list of saves will be searched for any saves of the corresponding title. If no saves are found, then show an error saying no saves were found. Otherwise, initialise a new window that will have a scrollable frame containing a button for each save that was found. When clicked, open a new ProgressWindow that will show the progress of the save being downloaded. 


### Settings 

Each emulator has its own settings within the app. There will be a user directory setting, which is used for handling user data, and a emulator install directory, where the emulator will be downloaded to. 
Some emulators will have a ROM directory setting if there is the option to download ROMs for the emulator within the app. 

#### Yuzu settings 

Yuzu has 2 additional custom settings that control the usage of a external application to install/update yuzu. One is to provide the path to this application. The other is a toggleable checkbox that controls whether to make use of the application or not. 
It was designed to work with the official liftinstall developed by the yuzu team but it works with [pinEApple's liftinstall](https://github.com/pineappleEA/liftinstall) that allows you to install early access for free using their builds from the same repository I use to source early access builds. The sources to everything I use are provided at the bottom of this README.md

#### App settings 

There is an appearance mode setting which will control whether the app is in light mode or dark mode. 
Switching the appearance mode may not change the appearance by a huge amount depending on the theme. 

The theme can be controlled through the theme setting. These themes were sourced from various GitHub repositories which I linked above. 

The next two settings are toggleable checkboxes. One is to control whether files are deleted after their contents have been installed to the emulators directory. This includes firmware and key archives or archives of builds of emulators. 
The other settings controls whether the app will check for an update upon starting the app. 


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
   
## Images
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


## Aknowledgements

- [Yuzu Team](https://yuzu-emu.org/) - Nintendo Switch Emulator Developers
- [Dolphin Team](https://dolphin-emu.org/) - Nintendo Wii & Nintendo GameCube Emulator Developers
- [Ryujinx Team](https://ryujinx.org/) - Nintendo Switch Emulator Developers
- [Xenia Team](https://xenia.jp/) - Xbox 360 Emulator Developers
- [Myrient](https://myrient.erista.me/) - Video Game collection
- Ecchibitionist - For the saves.
- [RyuSAK](https://github.com/Ecks1337/RyuSAK) 
- [Kewl](https://www.steamgriddb.com/profile/76561199389486997), [supernova](https://www.steamgriddb.com/profile/76561198042356275), [Crazy](https://www.steamgriddb.com/profile/76561198041637425), [TalkyPup](https://www.steamgriddb.com/profile/76561198025210011) - Banners for emulators. 



## [Early Access Source](https://github.com/pineappleEA/pineapple-src) | [Firmware & Keys](https://github.com/Viren070/Emulator-Manager-Resources) | [Nintendo Switch Savegames](https://new.mirror.lewd.wtf/archive/nintendo/switch/savegames/) | [Dolphin ROMs](https://myrient.erista.me/)

All emulators not listed here are sourced from either their website or GitHub repository.
