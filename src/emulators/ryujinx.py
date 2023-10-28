import json
import os
import shutil
import subprocess
from tkinter import messagebox
from zipfile import ZipFile

import emulators.switch_emulator as switch_emu
from gui.frames.progress_frame import ProgressFrame
from utils.downloader import download_through_stream
from utils.file_utils import copy_directory_with_progress
from utils.requests_utils import (create_get_connection, get_headers,
                                  get_release_from_assets,
                                  get_resources_release)


class Ryujinx:
    def __init__(self, gui, settings, metadata):
        self.settings = settings
        self.metadata = metadata
        self.gui = gui
        self.main_progress_frame = None
        self.data_progress_frame = None
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False
        
    def verify_ryujinx_zip(self, path_to_archive):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                if 'publish/Ryujinx.exe' in archive.namelist():
                    return True 
                else:
                    return False
        except Exception:
            return False

            
    def get_latest_release(self):
        response = create_get_connection('https://api.github.com/repos/Ryujinx/release-channel-master/releases' , headers=get_headers(self.settings.app.token))
        if not all(response): return (False, response[1])
        response = response[1]
        try:
            release_info = json.loads(response.text)[0]
            latest_version = release_info["tag_name"]
            assets = release_info['assets']
        except KeyError:
            return (False, "API Rate Limited")
        release = get_release_from_assets(assets, "win_x64")
        release.version = latest_version
        return (True, release )

    
    def download_release(self, release):
        
        response_result = create_get_connection(release.download_url, stream=True, headers=get_headers(self.settings.app.token))
        if not all(response_result):
            return response_result 
        response = response_result[1]   
        self.main_progress_frame.start_download(f"Ryujinx {release.version}", release.size)
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
        download_path = os.path.join(os.getcwd(), f"ryujinx-{release.version}-win_x64.zip")
        download_result = download_through_stream(response, download_path, self.main_progress_frame, 1024*203)
        return download_result
    
    def extract_release(self, zip_path):
        extract_folder = self.settings.ryujinx.install_directory
        extracted_files = []

        self.main_progress_frame.start_download(os.path.basename(zip_path).replace(".zip", ""), 0)
        self.main_progress_frame.complete_download()
        self.main_progress_frame.update_status_label("Extracting... ")
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
        if os.path.exists(os.path.join(self.settings.ryujinx.install_directory,"publish")):
            self.delete_ryujinx()
        try:
            with ZipFile(zip_path, 'r') as archive:
                total_files = len(archive.namelist())     
                for file in archive.namelist():
                    if self.main_progress_frame.cancel_download_raised:
                        self.main_progress_frame.grid_forget()
                        return (False, "Cancelled")
                    archive.extract(file, extract_folder)
                    extracted_files.append(file)
                    # Calculate and display progress
                    self.main_progress_frame.update_extraction_progress(len(extracted_files) / total_files) 
        except Exception as error:
            self.main_progress_frame.grid_forget()
            return (False, error)
        self.main_progress_frame.grid_forget()
        return (True, extract_folder)
    
    def install_release_handler(self, updating=False, path_to_archive=None):
        release_archive = path_to_archive
        if path_to_archive is None:
            release_result = self.get_latest_release()
            if not all(release_result):
                messagebox.showerror("Install Ryujinx", f"There was an error while attempting to fetch the latest release of Ryujinx:\n\n{release_result[1]}")
                return
            release = release_result[1]
            if release.version == self.metadata.get_installed_version("ryujinx"):
                if updating:
                    return 
                if not messagebox.askyesno("Ryujinx", "You already have the latest version of Ryujinx  installed, download anyways?"):
                    return
            download_result = self.download_release(release)
            if not all(download_result):
                if download_result[1] != "Cancelled":
                    messagebox.showerror("Error", f"There was an error while attempting to download the latest release of Ryujinx:\n\n{download_result[1]}")
                return 
            release_archive = download_result[1]
        elif not self.verify_ryujinx_zip(path_to_archive):
            messagebox.showerror("Error", "The archive you have provided is invalid")
            return 
        extract_result = self.extract_release(release_archive)
        if not all(extract_result):
            if extract_result[1]!="Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{extract_result[1]}")
            return 
        if path_to_archive is None:
            self.metadata.update_installed_version("ryujinx", release.version)
        if path_to_archive is None and self.settings.app.delete_files == "True" and os.path.exists(release_archive):
            os.remove(release_archive)
        messagebox.showinfo("Install Ryujinx", f"Ryujinx was successfully installed to {extract_result[1]}")

    
        
    def delete_ryujinx(self, skip_prompt=False):
        try:
            shutil.rmtree(os.path.join(self.settings.ryujinx.install_directory, "publish"))
            if not skip_prompt:
                messagebox.showinfo("Delete Yuzu", "Installation of Ryujinx successfully deleted")
        except Exception as error:
            messagebox.showerror("Delete Error", f"An error occured while trying to delete the installation of Ryujinx:\n\n{error}")
        
    
    def launch_ryujinx_handler(self, skip_update=False):
        if not skip_update:
            self.gui.configure_action_buttons("disabled", text="Fetching Updates...")
            self.install_release_handler(True)
 
        self.verify_and_install_firmware_keys()
        
        self.gui.configure_action_buttons("disabled", text="Launched!  ")
        ryujinx_exe = os.path.join(self.settings.ryujinx.install_directory, "publish", "Ryujinx.exe")
       
        args = [ryujinx_exe]
        self.running = True
        subprocess.run(args, capture_output=True, check=False)
        self.running = False
        
    def verify_and_install_firmware_keys(self):
        if not switch_emu.check_current_keys(os.path.join(self.settings.ryujinx.user_directory, "system", "prod.keys")):
            messagebox.showwarning("Missing Keys", "It seems you are missing the switch decryption keys. These keys are required to emulate games. Please install them using the download button below")
        
        if self.settings.app.ask_firmware != "False" and not switch_emu.check_current_firmware(os.path.join(self.settings.ryujinx.user_directory, "bis", "system", "Contents", "registered")):
            if not messagebox.askyesno("Firmware Missing", "It seems you are missing the switch firmware files. Without these files, some games may not run. You can install the firmware using the buttons below. Press Yes to remind you later or No to never ask again."):
                self.settings.app.ask_firmware = "False"
            

       
    def install_firmware_handler(self, mode, path_or_release):
        if switch_emu.check_current_firmware(os.path.join(self.settings.ryujinx.user_directory, "bis", "system", "Contents", "registered")) and not messagebox.askyesno("Firmware Exists", "You already seem to have firmware installed, install anyways?"):
            return 
   
        if mode == "release":
            release = path_or_release
            firmware_path= self.download_firmware_archive(release)
            if not all(firmware_path):
                if firmware_path[1] != "Cancelled":
                    messagebox.showerror("Download Error", firmware_path[1])
                return False
            firmware_path = firmware_path[1] 
            version = release.version
        elif mode == "path" and not switch_emu.verify_firmware_archive(path_or_release):
            messagebox.showerror("Error", "The firmware archive you have provided is invalid")
            return 
        else:
            firmware_path = path_or_release
        
        result = switch_emu.install_firmware_from_archive(firmware_path, os.path.join(self.settings.ryujinx.user_directory, "bis", "system", "Contents", "registered"), self.main_progress_frame, "ryujinx")
        if not result[0]:
            messagebox.showerror("Extract Error", f"There was an error while trying to extract the firmware archive: \n\n{result[1]}")
            return 
        result = result[1]
        if mode == "release": 
            if self.settings.app.delete_files == "True" and os.path.exists(firmware_path):
                try:
                    os.remove(firmware_path)
                except PermissionError as error:
                    messagebox.showerror("Error", f"Failed to delete firmware archive due to error below \n\n{error}")
            self.metadata.update_installed_version("ryujinx_firmware", version)
        if result:
            messagebox.showwarning("Unexpected Files" , f"These files were skipped in the extraction process: {result}")
        messagebox.showinfo("Firmware Install", "The switch firmware files were successfully installed")
        return True 
    
    def download_firmware_archive(self, release):
        firmware = release

        response_result = create_get_connection(firmware.download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response_result):
            return response_result

        response = response_result[1]
        self.main_progress_frame.start_download(f"Firmware {firmware.version}", firmware.size)
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
        
        download_path = os.path.join(os.getcwd(), f"Firmware {firmware.version}.zip")
        download_result = download_through_stream(response, download_path, self.main_progress_frame, 1024*203)
        self.main_progress_frame.complete_download()
        return download_result

    
    

    def install_key_handler(self, mode, path_or_release):
        if switch_emu.check_current_keys(os.path.join(self.settings.ryujinx.user_directory, "system", "prod.keys")) and not messagebox.askyesno("Keys Exist", "You already seem to have the decryption keys, install anyways?"):
            return 
        
        if mode == "release":
            release = path_or_release
            key_path = self.download_key_archive(release)
            if not all(key_path):
                if key_path[1] != "Cancelled":
                    messagebox.showerror("Download Error", key_path[1])
                return False
            key_path = key_path[1] 
            version = release.version
            
        elif not switch_emu.verify_key_archive(path_or_release):
            messagebox.showerror("Error", "The key archive you have provided is invalid")
            return
        else:
            key_path = path_or_release
        if key_path.endswith(".keys"):
            switch_emu.install_keys_from_file(key_path, os.path.join(self.settings.ryujinx.user_directory, "system"))
        else:
            result = switch_emu.install_keys_from_archive(key_path, os.path.join(self.settings.ryujinx.user_directory, "system"), self.main_progress_frame)
            if not all(result):
                messagebox.showerror("Extract Error", f"There was an error while trying to extract the key archive: \n\n{result[1]}")
                return 
            result = result[1]
            if "prod.keys" not in result:
                messagebox.showwarning("Keys", "Was not able to find any prod.keys within the archive, the archive was still extracted successfully.")
                return False 
        if mode == "release":
            if self.settings.app.delete_files == "True" and os.path.exists(key_path):
                os.remove(key_path)
            self.metadata.update_installed_version("ryujinx_keys", version)
        messagebox.showinfo("Keys", "Decryption keys were successfully installed!")
        return True 
            
    def download_key_archive(self, release):
       
        key = release
        response_result = create_get_connection(key.download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response_result):
            return response_result
           
        response = response_result[1]
        self.main_progress_frame.start_download(f"Keys {key.version}", key.size)
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
        download_path = os.path.join(os.getcwd(), f"Keys {key.version}.zip")
        download_result = download_through_stream(response, download_path, self.main_progress_frame, 1024*128)
        self.main_progress_frame.complete_download()
        
        return download_result
    

        
    def export_ryujinx_data(self, mode, directory_to_export_to):
        user_directory = self.settings.ryujinx.user_directory
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No Ryujinx data on local drive found")
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Ryujinx Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'bis', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(directory_to_export_to, 'bis', 'user', 'save'), "Exporting Ryujinx Save Data", self.data_progress_frame)
        elif mode == "Exclude 'bis' & 'system'":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Ryujinx Data", self.data_progress_frame, ["bis", "system"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def import_ryujinx_data(self, mode, directory_to_import_from):
        user_directory = self.settings.ryujinx.user_directory
        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
            return
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Ryujinx Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(directory_to_import_from, 'bis', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(user_directory, 'bis', 'user', 'save'), "Importing Ryujinx Save Data", self.data_progress_frame)
        elif mode == "Exclude 'bis' & 'system'":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Ryujinx Data", self.data_progress_frame, ["bis", "system"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def delete_ryujinx_data(self, mode):
        result = ""

        user_directory = self.settings.ryujinx.user_directory
    
        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except Exception as error:
                    messagebox.showerror("Delete Ryujinx Data", f"Unable to delete {directory}:\n\n{error}")
                    return False
            return False

        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'bis', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
        elif mode == "Exclude 'bis' & 'system'":
            deleted = False
            for root_folder in user_directory:
                if os.path.exists(root_folder) and os.listdir(root_folder):
                    subfolders_failed = []
                    for folder_name in os.listdir(root_folder):
                        folder_path = os.path.join(root_folder, folder_name)
                        if os.path.isdir(folder_path) and not(folder_name == 'bis' or folder_name == 'system'):
                            deleted = True
                            if not delete_directory(folder_path):
                                subfolders_failed.append(folder_name)

                    if subfolders_failed:
                        failed_subfolders_message = ", ".join(subfolders_failed)
                        result += f"Deletion failed in {root_folder} for subfolders: {failed_subfolders_message}\n"
                    else:
                        result += f"Data deleted from {root_folder}\n"
                    if not deleted:
                        result = ""

        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")
        self.gui.configure_data_buttons(state="normal")

