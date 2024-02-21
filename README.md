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

- **Installation and Updates:** Install, delete, or launch Xenia with customisable installation location
- **Build Switching**: Easily switch between master and canary builds. Can keep both installed at the same time
- **Automatic Updates**: Update Xenia automatically on launch (Can be skipped by holding shfit)
- **Game Downloads:** Download games and digital content directly from within the app.
- **User Data Management:** Manage user data with options for export, import, and deletion.

### Other

- **Customisation:** Personalise the app through a variety of themes sourced from [avalon60/ctk_theme_builder/](https://github.com/avalon60/ctk_theme_builder) and [a13xe/CTkThemesPack](https://github.com/a13xe/CTkThemesPack)
- **Portable Mode:** Enable portable mode by creating a PORTABLE.txt file.
  
> [!NOTE]
> If you are using an executable, you must be using the ZIP asset for it to be portable. Otherwise, it will attempt to use the %TMP% path which is located in %localappdata%


   
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
