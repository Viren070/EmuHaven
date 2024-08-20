import os
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

import customtkinter

from gui.frames.current_roms_frame import CurrentROMSFrame
from gui.frames.progress_frame import ProgressFrame
from gui.frames.rom_search_frame import ROMSearchFrame
from core.utils.web import download_file_with_progress


class DolphinROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, dolphin, settings, cache):
        super().__init__(master)
        self.master = master
        self.roms = None
        self.cache = cache
        self.settings = settings
        self.dolphin = dolphin
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()

    def build_frame(self):
        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.add("Wii ROMs")
        self.add("GameCube ROMs")
        self.add("Downloads")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Wii ROMs").grid_columnconfigure(0, weight=1)
        self.tab("Wii ROMs").grid_rowconfigure(0, weight=1)
        self.tab("GameCube ROMs").grid_columnconfigure(0, weight=1)
        self.tab("GameCube ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Downloads").grid_columnconfigure(0, weight=1)
        self.tab("Downloads").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = CurrentROMSFrame(self.tab("My ROMs"), self, self.settings.dolphin,  (".wbfs", ".iso", ".rvz", ".gcm", ".gcz", ".ciso"))
        self.current_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.wii_roms_frame = ROMSearchFrame(self.tab("Wii ROMs"), root=self, console_name="nintendo_wii", rom_link="https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20[zstd-19-128k]/",)
        self.wii_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.gamecube_roms_frame = ROMSearchFrame(self.tab("GameCube ROMs"), root=self, console_name="nintendo_gamecube", rom_link="https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20[zstd-19-128k]/")
        self.gamecube_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.downloads_frame = customtkinter.CTkScrollableFrame(self.tab("Downloads"))
        self.downloads_frame.grid_columnconfigure(0, weight=1)
        self.downloads_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    def download_rom_event(self, rom, button):
        Thread(target=self.download_rom_handler, args=(rom, button)).start()

    def download_rom_handler(self, rom, button):
        self.downloads_in_progress += 1
        button.configure(state="disabled", text="Downloading...")
        self.set("Downloads")
        download_result = self.download_rom(rom)
        if not all(download_result):
            if download_result[1] != "Cancelled":
                messagebox.showerror("Error", f"An error occurred while attempting to download this ROM\n\n{download_result[1]}")
            else:
                if os.path.exists(download_result[2]):
                    os.remove(download_result[2])
            self.downloads_in_progress -= 1
            button.configure(state="normal", text="Download")
            return
        extract_result = self.extract_rom(download_result[1])
        if not all(extract_result):
            messagebox.showerror("Error", f"An error occurred while attempting to extract this ROM\n\n{extract_result[1]}")
            button.configure(state="normal", text="Download")
            return
        if self.settings.app.delete_files == "True":
            if os.path.exists(download_result[1]):
                os.remove(download_result[1])
        messagebox.showinfo("ROM Install", f"The ROM was successfully installed at path: \n\n{extract_result[1]}")
        button.configure(state="normal", text="Download")

    def download_rom(self, rom):
        download_folder = self.settings.dolphin.rom_directory
        if download_folder == "":
            if messagebox.askyesno("No ROM Directory", "No ROM directory has been set in the settings. Would you like to download to the current directory?"):
                download_folder = os.getcwd()
            else:
                return (False, "Cancelled", "")
        download_file_with_progress(
            download_url=rom["url"],
            download_path=download_folder / rom["name"],
            progress_handler=None,
            chunk_size=1024,
        )

    def extract_rom(self, path_to_rom_archive):
        try:
            with ZipFile(path_to_rom_archive, 'r') as zip_ref:

                file_list = zip_ref.namelist()
                if len(file_list) != 1:
                    return (False, "Unexpected number of files")

                extracted_file_name = file_list[0]
                extracted_file_path = os.path.join(self.settings.dolphin.rom_directory, extracted_file_name)
                zip_ref.extract(extracted_file_name, self.settings.dolphin.rom_directory)

                return (True, extracted_file_path)

        except Exception as error:
            return (False, error)
