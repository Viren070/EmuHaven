import customtkinter 
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile
import os 
from utils.downloader import download_through_stream
from utils.requests_utils import create_get_connection, get_headers
from gui.frames.progress_frame import ProgressFrame
from gui.frames.rom_search_frame import ROMSearchFrame
from gui.frames.current_roms_frame import CurrentROMSFrame
class DolphinROMFrame(customtkinter.CTkTabview):
    def __init__(self, master, dolphin, settings):
        super().__init__(master, height=500, width=700)
        self.master = master 
        self.roms = None
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
        
        self.current_roms_frame = CurrentROMSFrame(self.tab("My ROMs"), self, self.settings.dolphin,  (".wbfs", ".iso", ".rvz", ".gcm", ".gcz", ".ciso"))
        self.current_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.wii_roms_frame = ROMSearchFrame(self.tab("Wii ROMs"), self, "https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20[zstd-19-128k]/",)
        self.wii_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.gamecube_roms_frame = ROMSearchFrame(self.tab("GameCube ROMs"), self, "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20[zstd-19-128k]/")
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
        os.makedirs(download_folder, exist_ok=True)
        download_path = os.path.join(download_folder, rom.filename)
        response = create_get_connection(rom.url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response):
            return response 
        response = response[1]
        progress_frame = ProgressFrame(self.downloads_frame, rom.filename)
        progress_frame.total_size = int(response.headers.get("content-length", 0))
        progress_frame.grid(row=self.downloads_in_progress, column=0, padx=10,pady=10, sticky="ew")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203, total_size=int(response.headers.get('content-length', 0)))
        progress_frame.destroy()
        return download_result
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

       