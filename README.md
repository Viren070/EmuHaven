# Emulator Manager

A program that will help manage your emulators, currently supports: 

 - Dolphin
 - Yuzu
 - Ryujinx
 - Xenia

Currently only works for Windows and will not run on other operating systems. This can be fixed though. 

[View images here](https://github.com/Viren070/Emulator-Manager?tab=readme-ov-file#images)

## Installation

### Windows Executable Installation

If you prefer using an EXE file to run the app:

1. Go to the [latest release](https://github.com/Viren070/Emulator-Manager/releases/latest)
2. Scroll down to the assets and download `Emulator.Manager.v0.x.x.zip`
3. Extract the downloaded zip file and inside the extracted folder launch Emulator Manager.exe 

Note: Windows Defender will detect the file as a virus since the file is unsigned. This is a false positive and can be ignored. To avoid the warning, follow the steps below.

### Running from Source

If you want to run Emulator Manager from the source code:

1. Clone the repository with the command below or click Code > Download ZIP
   ```
   git clone https://github.com/Viren070/Emulator-Manager
   ```
2. Install the dependencies with this command inside the cloned repository
   ```
   pip install -r requirements.txt
   ```
   - Make sure you have Python 3.12 installed
    
3. Simply run main.py and you should see the app open.
4. To build an executable file, use this command:
   ```
   pyinstaller --noconfirm --onedir --console --name "Emulator Manager" --clean --add-data "%localappdata%/Programs/Python/Python312/Lib/site-packages/customtkinter;customtkinter/" --add-data src/assets;assets/  src/main.py
   ```
   - If you don't have pyinstaller, you can install it with `pip install pyinstaller`
   - You can replace `--onedir` with `--onefile`.
   - Replace the path to customtkinter as necessary


## Features

### Dolphin

- **Installation Options**: Install, delete, or launch Dolphin with customisable installation location.
- **Channel Switching**: Easily switch between beta and development builds through a dropdown menu.
- **Automatic Updates:** Dolphin updates automatically on launch. (Can be skipped by holding shift)
- **Game Library**: Download GameCube or Wii games directly from the manager with easy browsing and searching.
- **User Data Management**: Efficiently manage your user data with support for importing or exporting
- 
### Yuzu
- **Installation**: Install, delete, or launch yuzu with a customisable installation locatiion
- **Channel Switching:** Easily switch between mainline and early access channels through a dropdown menu. Can keep both installed at the samet time
- **Automatic Updates:** Yuzu updates automatically on launch, detecting and installing missing firmware and keys. (Can be skipped by holding shift)
- **Firmware and Keys:** Detect missing installation of firmware and keys and provide automatic installations with customisable versions.
- **User Data Management**: Customise user data with options for deletion, import, and export.
- **Game Management:** Manage games, install mods, and download save games within the app.



### Ryujinx

- **Installation:** Install, delete, or launch Ryujinx with customiable installation location.
- **Automatic Updates:** Ryujinx updates automatically on launch. (Can be skipped by holding shift)
- **Firmware and Keys Management**: Detect missing installation of firmware and keys and provide automatic installations with customisable versions.
- **User Data Management:** Customise user data with options for deletion, import, and export.
- **Game Management:** Manage games, install mods, and download save games within the app.

>  [!NOTE]
> For yuzu and ryujinx: The ability to download mods for games is planned for future updates.

### Xenia

- **Installation and Updates:** Install, delete, or launch Xenia
- **Build Switching**: Easily switch between master and canary builds. Can keep both installed at the same time
- **Automatic Updates**: Update Xenia automatically on launch (Can be skipped by holding shfit)
- **Game Downloads:** Download games and digital content directly from within the app.
- **User Data Management:** Manage user data with options for export, import, and deletion.

### Other

- **Customisation:** Personalise the app through a variety of themes sourced from [avalon60/ctk_theme_builder/](https://github.com/avalon60/ctk_theme_builder) and [a13xe/CTkThemesPack](https://github.com/a13xe/CTkThemesPack)
- **Portable Mode:** Enable portable mode by creating a PORTABLE.txt file.
  
> [!NOTE]
> If you are using an executable, you must be using the ZIP asset for it to be portable. Otherwise, it will attempt to use the %TMP% path which is located in %localappdata%



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

3 option menus on the left with a button to the right for each. 
option menus are used to determine what part to carry out the action on. 
The button is used to perform the action 

All emulators have the choice of either All Data or Custom. 

Choosing custom will open a menu where you can select specific folders to carry out the action on (You can only choose root folders).
Choosing All Data does as described - it will simply carry out the action on every folder and file within the user directory or directory you select. 

#### Yuzu & Ryujinx 

These 2 emulators have the extra choice of 'Save Data'. This will export/import/delete ALL save data for every profile within the emulator. 

### `Manage ROMs` Menu

This menu contains a Tabview frame which as it suggests, allows you to display separate tabs.

#### Dolphin

Dokphin's Manage ROMs menu has 4 tabs. One called `My ROMs` which will show you the roms you currently have downloaded (provided that the correct path is provided in the settings). And it will display the size that it takes and a delete button next to it. 
The next 2 tabs allow you to download ROMs from Myrient. One tab for Wii ROMs and one for GameCube ROMS. 

Shift clicking the download button will open the download link in your browser.

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



   
## Images

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/be259b14-4908-4c4f-964d-d1cda35e6497)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/0efa4183-e7ee-4ec5-b928-e70a894cae66)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/a9320702-ac36-4b40-b053-45280528ccfe)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/69e34f4b-9765-4210-bbcc-3818b0ac6517)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/d6ba8ddf-3949-4834-9ae4-6007154b43aa)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/59db024a-5e4e-4556-881d-77809b970619)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/965600d7-1e60-458e-b70d-4d87e192dd4b)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/45c3581c-4f74-4581-888c-5269a1919138)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/81955397-d1e0-4ed8-be74-83fce021dcd2)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/6c0b73b9-fe19-42dd-b46d-eaafcf097eef)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/fd970ca6-ebbb-405f-9ad5-2942565a3dab)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/f3dcd629-5b4d-46d1-9fe0-1cd1114c60e9)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/22b9f520-adc8-4f6c-a1d5-a9ba3b0b251d)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/e5b6ae5c-7534-4af4-963e-5abc63e2c8e0)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/3fcde0f3-e919-4e2e-84e9-cd258dfffd28)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/dea33238-314e-413a-a198-ce81b6f95fb5)

![image](https://github.com/Viren070/Emulator-Manager/assets/71220264/9ee23034-0a70-4807-bad5-655f0ed5e964)


## Aknowledgements

- [Yuzu Team](https://yuzu-emu.org/) - Nintendo Switch Emulator Developers
- [Dolphin Team](https://dolphin-emu.org/) - Nintendo Wii & Nintendo GameCube Emulator Developers
- [Ryujinx Team](https://ryujinx.org/) - Nintendo Switch Emulator Developers
- [Xenia Team](https://xenia.jp/) - Xbox 360 Emulator Developers
- [Myrient](https://myrient.erista.me/) - Video Game collection
- Ecchibitionist - For the saves they used to provide on their archive.
- [THZoria](https://github.com/THZoria) - For providing the firmware on their [repository](https://github.com/THZoria/NX_Firmware)
- [RyuSAK](https://github.com/Ecks1337/RyuSAK) - For providing inspiration for some features and how to code them.
- [Kewl](https://www.steamgriddb.com/profile/76561199389486997), [supernova](https://www.steamgriddb.com/profile/76561198042356275), [Crazy](https://www.steamgriddb.com/profile/76561198041637425), [StaticMachina](https://www.steamgriddb.com/profile/76561198129822760), [TalkyPup](https://www.steamgriddb.com/profile/76561198025210011) - Banners for emulators. 



## [Early Access Source](https://github.com/pineappleEA/pineapple-src) | [Firmware & Keys](https://github.com/Viren070/Emulator-Manager-Resources) | [Nintendo Switch Savegames](https://github.com/Viren070/NX_Saves/) | [Dolphin ROMs](https://myrient.erista.me/)

All emulators not listed here are sourced from either their website or GitHub repository.
