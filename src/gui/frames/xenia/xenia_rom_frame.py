import os
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

import customtkinter

from core import constants
from gui.frames.current_roms_frame import CurrentROMSFrame
from gui.frames.rom_search_frame import ROMSearchFrame


class XeniaROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, xenia, settings, cache):
        super().__init__(master, height=500, width=700)
        self.master = master
        self.roms = None
        self.cache = cache
        self.settings = settings
        self.xenia = xenia
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()

    def build_frame(self):
        self.grid(row=0, column=0, sticky="nsew")
        self.add("My ROMs")
        self.add("Xbox 360 ROMs")
        self.add("Xbox 360 Digital")
        self.add("Downloads")
        self.tab("My ROMs").grid_columnconfigure(0, weight=1)
        self.tab("My ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Xbox 360 ROMs").grid_columnconfigure(0, weight=1)
        self.tab("Xbox 360 ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Xbox 360 Digital").grid_columnconfigure(0, weight=1)
        self.tab("Xbox 360 Digital").grid_rowconfigure(0, weight=1)

        self.current_roms_frame = CurrentROMSFrame(self.tab("My ROMs"), self, self.settings.xenia,  (".wbfs", ".iso", ".rvz", ".gcm", ".gcz", ".ciso"))
        self.current_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.xbox_roms_frame = ROMSearchFrame(self.tab("Xbox 360 ROMs"), self, myrient_path=constants.Xenia.MYRIENT_XBOX_360_PATH, console_name="microsoft_xbox_360")
        self.xbox_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.gamecube_roms_frame = ROMSearchFrame(self.tab("Xbox 360 Digital"), self, myrient_path=constants.Xenia.MYRIENT_XBOX_360_DIGITAL_PATH, console_name="microsoft_xbox_360_digital")
        self.gamecube_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.downloads_frame = customtkinter.CTkScrollableFrame(self.tab("Downloads"), width=650, height=420)
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
        download_folder = self.settings.xenia.rom_directory
        if download_folder == "":
            if messagebox.askyesno("No ROM Directory", "You have not set a ROM directory in the settings. Would you like to download to the current directory?"):
                download_folder = os.getcwd()
            else:
                return (False, "Cancelled", "")
        os.makedirs(download_folder, exist_ok=True)
        download_path = os.path.join(download_folder, rom.filename)
        response = create_get_connection(rom.url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response):
            return response
        response = response[1]
        progress_frame = ProgressFrame(self.downloads_frame)
        progress_frame.start_download(rom.filename, int(response.headers.get("content-length", 0)))
        progress_frame.grid(row=self.downloads_in_progress, column=0, padx=10, pady=10, sticky="ew")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
        progress_frame.destroy()
        return download_result

    def extract_rom(self, path_to_rom_archive):
        try:
            with ZipFile(path_to_rom_archive, 'r') as zip_ref:

                file_list = zip_ref.namelist()
                if len(file_list) != 1:
                    return (False, "Unexpected number of files")

                extracted_file_name = file_list[0]
                extracted_file_path = os.path.join(self.settings.xenia.rom_directory, extracted_file_name)
                zip_ref.extract(extracted_file_name, self.settings.xenia.rom_directory)

                return (True, extracted_file_path)

        except Exception as error:
            return (False, error)
