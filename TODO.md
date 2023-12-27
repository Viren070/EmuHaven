## For 0.11

- [x] Minimise PathDialog when browse is clicked
- [x] adjust fg colour for root window
- [x] Adjust fg, bg colour values and border widths for PathDialog
- [x] Fix search for current ROMS
- [x] Fix duplication of last ROM on any page after searching for downloading

## For 0.12

- [x] Make menubar on LHS scrollable 
- [x] Don't update text to include version if text has been altered
- [x] Move `Use Yuzu Installer` setting to yuzu settings
- [x] Redesign firmware and key install section and add dropdown menu to select version and show installed version
- [x] Rewrite or delete firmware downloader
- [x] Use Dolphin website for dolphin downloads and add ability to switch from beta and development channels.
- [x] factor out common switch emulator functions from yuzu into switch emulator 
- [x] Write firmware and key version to metadata
- [x] Add Ryujinx Support 
    - [x] Add ryujinx.py 
    - [x] Add ryujinx_frame.py
    - [x] Add ryujinx_settings_frame.py
    - [x] Add ryujinx_settings.py 
    
- [x] Add base EmulatorFrame class that all other emulator_frame classes inherit from.
- [x] More accurate download speed by averaging across set amount of intervals and not since starting time

## For 0.13
- [ ] Add Xenia support for both master and nightly builds. 
- [ ] redesign "My ROMS" section for yuzu and ryujinx

    - Use cache\game_list\ for yuzu
    - use games for ryujinx
    - use https://github.com/arch-box/titledb for covers
    - https://new.mirror.lewd.wtf/archive/nintendo/switch/savegames/ for saves
    - maybe mods as well

     
- [x] Add shortcuts for emulators which will show window with progress bar for updating.
    - basically just add CLI support
    - Add shortcut setting to each emulator. User provides path. If left empty or changed to empty, disable and/or remove shortcut.
    - Add new updater window and logic to handle launching this window and updating emulator through arguments
- [x] Add option to use current directory for settings and metadata instead of attempting to use %appdata%\Roaming\Emulator Manager

- [x] Add custom option for import/exports. remove 'exclude nand and keys'
- [x] add option `check for update at start-up` that will control whether or not the app will check for an update at start-up

## other 

- [x] consider removing export directory setting and instead ask user for each export 


