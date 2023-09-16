import os
import shutil
import subprocess
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

import requests

from gui.frames.progress_frame import ProgressFrame
from utils.downloader import download_through_stream
from utils.file_utils import copy_directory_with_progress
from utils.requests_utils import get_headers, get_resources_release, get_file_links_from_page


class Dolphin:
    def __init__(self, gui, settings, metadata):
        self.settings = settings
        self.metadata = metadata
        self.gui = gui
        self.running = False
        self.dolphin_is_running = False
       
        self.dolphin_download_api = 'https://api.github.com/repos/Viren070/dolphin-beta-downloads/releases/latest'
                    
                
    def delete_dolphin_zip(self, zip_path):
        import time 
        time.sleep(2)
        os.remove(zip_path)
        
    

    def download_release(self, release):
        download_folder = os.getcwd()
        
        progress_frame = ProgressFrame(self.gui.dolphin_log_frame, f"Dolphin {release.version}")
        download_path = os.path.join(download_folder, f"Dolphin {release.version}.zip")
        response = requests.get(release .download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.total_size = release.size
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
        progress_frame.destroy() 
        return download_result

        

        
            
                          
        
    def install_dolphin_handler(self, updating=False):
            
        release_result = get_resources_release("Dolphin", headers=get_headers(self.settings.app.token))
        if not all(release_result):
            messagebox.showerror("Install Dolphin", f"There was an error while attempting to fetch the latest release of Dolphin:\n\n{release_result[1]}")
        release = release_result[1]
        release.version = release.name.replace("Dolphin.", "").replace(".zip", "")
        if release.version == self.metadata.get_installed_version("dolphin"):
            if updating:
                return 
            messagebox.showinfo("Dolphin", "You already have the latest version of Dolphin installed")
            return
        download_result = self.download_release(release)
        if not all(download_result):
            if download_result[1] != "Cancelled":
                messagebox.showerror("Error", f"There was an error while attempting to download the latest release of Dolphin\n\n{download_result[1]}")
            return 
        release_archive = download_result[1]
        extract_result = self.extract_release(release_archive)
        if self.settings.app.delete_files == "True":
            os.remove(release_archive)
        if not all(extract_result):
            if extract_result[1]!="Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{extract_result[1]}")
            return 
        self.metadata.update_installed_version("dolphin", release.version)
        messagebox.showinfo("Install Dolphin", f"Dolphin was successfully installed to {self.settings.dolphin.install_directory}")
        
   
    def extract_release(self, release): 
        dolphin_install_frame = ProgressFrame(self.gui.dolphin_log_frame, f"Extracting {os.path.basename(release)}")
        dolphin_install_frame.skip_to_installation()
        dolphin_install_frame.cancel_download_button.configure(state="normal")
        dolphin_install_frame.update_status_label("Status: Extracting... ")
        dolphin_install_frame.grid(row=0, column=0, sticky="nsew")
        extracted=True
        try:
            with ZipFile(release, 'r') as archive:
                total_files = len(archive.namelist())
                extracted_files = []
                
                for file in archive.namelist():
                    if dolphin_install_frame.cancel_download_raised:
                        extracted=False
                        break
                    archive.extract(file, self.settings.dolphin.install_directory)
                    extracted_files.append(file)
                    # Calculate and display progress
                    dolphin_install_frame.update_extraction_progress(len(extracted_files) / total_files) 
            dolphin_install_frame.destroy()
            if extracted:
                return (True, extracted_files)
            else:
                return (False, "Cancelled")
        except Exception as error:
            return (False, error)
   
    def delete_dolphin(self):
        try:
            shutil.rmtree(self.settings.dolphin.install_directory)
            messagebox.showinfo("Success", "The Dolphin installation was successfully was removed")
        except Exception as e:
            messagebox.showerror("Error", f"There was an error while attempting to delete Dolphin: \n\\n{e}")
            return
       
        
    def launch_dolphin_handler(self, skip_update=False):
        if not skip_update:

            a=self.gui.configure_buttons("disabled", text="Fetching Updates...  ") 
            self.install_dolphin_handler(True)
    
        a=self.gui.configure_buttons("disabled", text="Launched!  ") 
        dolphin_exe = os.path.join(self.settings.dolphin.install_directory, "Dolphin.exe")
        args = [dolphin_exe]
        self.running = True
        subprocess.run(args, capture_output=True, check=False)
        self.running = False
    
    def export_dolphin_data(self, mode):
        user_directory = self.settings.dolphin.user_directory
        export_directory = self.settings.dolphin.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No dolphin data on local drive found")
            self.gui.configure_data_buttons(state="normal")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(user_directory, users_export_directory, "Exporting All Dolphin Data", self.gui.dolphin_data_log)
    def import_dolphin_data(self, mode):
        user_directory = self.settings.dolphin.user_directory
        export_directory = self.settings.dolphin.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No dolphin data associated with your username was found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(users_export_directory, user_directory, "Importing All Dolphin Data", self.gui.dolphin_data_log)
    def delete_dolphin_data(self, mode):
        result = ""
        user_directory = self.settings.dolphin.user_directory
        export_directory = self.settings.dolphin.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except:
                    messagebox.showerror("Delete Dolphin Data", f"Unable to delete {directory}")
                    return False
                
            return False
        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
            
        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")
    def get_downloadable_roms(self, console):
        link = "https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20[zstd-19-128k]/" if console == "wii" else "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20[zstd-19-128k]/"
        return get_file_links_from_page(link, ".zip", get_headers())
   
    def get_current_roms(self):
        class ROMFile:
            def __init__(self, name, path, size):
                self.name = name 
                self.path = path
                self.size = size 
        roms = [] 
        allowed_extensions = (".wbfs", ".iso", ".rvz", ".gcm", ".gcz", ".ciso")
        rom_directory = self.settings.dolphin.rom_directory
        
        for file in os.listdir(rom_directory):
            if file.endswith(allowed_extensions) and os.path.isfile(os.path.join(rom_directory, file)):
                # Create a ROMFile object and append it to the roms list
                full_path = os.path.join(rom_directory, file)
                rom = ROMFile(name=file, path=full_path, size=os.path.getsize(full_path))
                roms.append(rom)
        return roms 