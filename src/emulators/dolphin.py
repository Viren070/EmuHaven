import os
import shutil
import subprocess
from tkinter import messagebox
from zipfile import ZipFile

import requests

from gui.frames.progress_frame import ProgressFrame
from utils.downloader import download_through_stream
from utils.file_utils import copy_directory_with_progress
from utils.requests_utils import get_headers, get_resources_release


class Dolphin:
    def __init__(self, gui, settings, metadata):
        self.settings = settings
        self.metadata = metadata
        self.gui = gui
        self.running = False
        self.dolphin_is_running = False
        self.main_progress_frame = None 
        self.data_progress_frame = None
        self.dolphin_download_api = 'https://api.github.com/repos/Viren070/dolphin-beta-downloads/releases/latest'
                    
                
    def delete_dolphin_zip(self, zip_path):
        import time 
        time.sleep(2)
        os.remove(zip_path)
        
    def verify_dolphin_zip(self, path_to_archive):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                if 'Dolphin.exe' in archive.namelist():
                    return True 
                else:
                    return False
        except Exception:
            return False
    def download_release(self, release):
        download_folder = os.getcwd()
        
        
        download_path = os.path.join(download_folder, f"Dolphin {release.version}.zip")
        response = requests.get(release .download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        self.main_progress_frame.start_download(f"Dolphin {release.version}", release.size)
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
 
        download_result = download_through_stream(response, download_path, self.main_progress_frame, 1024*203)
        self.main_progress_frame.complete_download() 
        return download_result
        
    def install_dolphin_handler(self, updating=False, path_to_archive=None):
        release_archive = path_to_archive
        if path_to_archive is None:
            release_result = get_resources_release("Dolphin", headers=get_headers(self.settings.app.token))
            if not all(release_result):
                messagebox.showerror("Install Dolphin", f"There was an error while attempting to fetch the latest release of Dolphin:\n\n{release_result[1]}")
                return 
            release = release_result[1]
            release.version = release.name.replace("Dolphin.", "").replace(".zip", "")
            if release.version == self.metadata.get_installed_version("dolphin"):
                if updating:
                    return 
                if not messagebox.askyesno("Dolphin", "You already have the latest version of Dolphin installed, install anyways?"):
                    return
            download_result = self.download_release(release)
            if not all(download_result):
                if download_result[1] != "Cancelled":
                    messagebox.showerror("Error", f"There was an error while attempting to download the latest release of Dolphin\n\n{download_result[1]}")
                return 
            release_archive = download_result[1]
        elif not self.verify_dolphin_zip(path_to_archive):
            messagebox.showerror("Error", "The dolphin archive you have provided is invalid. ")
            return 
        extract_result = self.extract_release(release_archive)
        if path_to_archive is None and self.settings.app.delete_files == "True":
            os.remove(release_archive)
        if not all(extract_result):
            if extract_result[1]!="Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{extract_result[1]}")
            return 
        if path_to_archive is None:
            self.metadata.update_installed_version("dolphin", release.version)
        messagebox.showinfo("Install Dolphin", f"Dolphin was successfully installed to {self.settings.dolphin.install_directory}")
        
   
    def extract_release(self, release): 
        self.main_progress_frame.start_download(f"{os.path.basename(release).replace(".zip", "")}", 0)
        self.main_progress_frame.complete_download()
        self.main_progress_frame.update_status_label("Extracting... ")
        self.main_progress_frame.grid(row=0, column=0, sticky="nsew")
        extracted=True
        try:
            with ZipFile(release, 'r') as archive:
                total_files = len(archive.namelist())
                extracted_files = []
                
                for file in archive.namelist():
                    if self.main_progress_frame.cancel_download_raised:
                        extracted=False
                        break
                    archive.extract(file, self.settings.dolphin.install_directory)
                    extracted_files.append(file)
                    # Calculate and display progress
                    self.main_progress_frame.update_extraction_progress(len(extracted_files) / total_files) 
            self.main_progress_frame.grid_forget()
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

            self.gui.configure_buttons("disabled", text="Fetching Updates...  ") 
            self.install_dolphin_handler(True)
    
        self.gui.configure_buttons("disabled", text="Launched!  ") 
        dolphin_exe = os.path.join(self.settings.dolphin.install_directory, "Dolphin.exe")
        args = [dolphin_exe]
        self.running = True
        subprocess.run(args, capture_output=True, check=False)
        self.running = False
    
    def export_dolphin_data(self, mode, directory_to_export_to):
        user_directory = self.settings.dolphin.user_directory
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No dolphin data on local drive found")
            self.gui.configure_data_buttons(state="normal")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Dolphin Data", self.data_progress_frame)
    def import_dolphin_data(self, mode, directory_to_import_from):
        user_directory = self.settings.dolphin.user_directory
        
        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No dolphin data associated with your username was found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All Dolphin Data", self.data_progress_frame)
    def delete_dolphin_data(self, mode):
        result = ""
        user_directory = self.settings.dolphin.user_directory
        
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
        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")
   
   