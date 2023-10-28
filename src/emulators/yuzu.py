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


class Yuzu:
    def __init__(self, gui, settings, metadata):
        self.settings = settings
        self.metadata = metadata
        self.gui = gui
        self.main_progress_frame = None
        self.data_progress_frame = None
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False
        
    def verify_yuzu_zip(self, path_to_archive, release_type):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                if (release_type == "mainline" and 'yuzu-windows-msvc/yuzu.exe' in archive.namelist()) or (release_type == "early_access" and "yuzu-windows-msvc-early-access/yuzu.exe" in archive.namelist()):
                    return True 
                else:
                    return False
        except Exception:
            return False

# 
# 

    def delete_early_access(self, skip_prompt=False):
        try:
            shutil.rmtree(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access"))
            if not skip_prompt:
                messagebox.showinfo("Success", "The installation of yuzu EA was successfully deleted!")
        except Exception as error_msg:
            messagebox.showerror("Delete Error", f"Failed to delete yuzu-ea: \n\n{error_msg}")     
            
    def get_latest_release(self, release_type):
        response = create_get_connection('https://api.github.com/repos/pineappleEA/pineapple-src/releases' if release_type == "early_access" else "https://api.github.com/repos/yuzu-emu/yuzu-mainline/releases", headers=get_headers(self.settings.app.token))
        if not all(response): return (False, response[1])
        response = response[1]
        try:
            release_info = json.loads(response.text)[0]
            latest_version = release_info["tag_name"].split("-")[-1]
            assets = release_info['assets']
        except KeyError:
            return (False, "API Rate Limited")
        release = get_release_from_assets(assets, "Windows" if release_type == "early_access" else "yuzu-windows-msvc-{}.zip", False if release_type == "early_access" else True)
        release.version = latest_version
        return (True, release )

    
    def download_release(self, release, release_type):
        
        response_result = create_get_connection(release.download_url, stream=True, headers=get_headers(self.settings.app.token))
        if not all(response_result):
            return response_result 
        response = response_result[1]   
        download_title = f"{{}} {release.version}".format("Yuzu" if release_type == "mainline" else "Yuzu EA")
        self.main_progress_frame.start_download(download_title, release.size)
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
        download_path = os.path.join(os.getcwd(), f"Yuzu-{release.version}.zip" if release_type == "mainline" else f"Yuzu-EA-{release.version}.zip")
        download_result = download_through_stream(response, download_path, self.main_progress_frame, 1024*203)
        return download_result
    
    def extract_release(self, zip_path, release_type):
        extract_folder = self.settings.yuzu.install_directory
        extracted_files = []

        self.main_progress_frame.start_download(os.path.basename(zip_path).replace(".zip", ""), 0)
        self.main_progress_frame.complete_download()
        self.main_progress_frame.update_status_label("Extracting... ")
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc" if release_type == "mainline" else "yuzu-windows-msvc-early-access")):
            delete_func = self.delete_mainline if release_type == "mainline" else self.delete_early_access
            delete_func(True)
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
    
    def install_release_handler(self, release_type, updating=False, path_to_archive=None):
        release_archive = path_to_archive
        if path_to_archive is None:
            release_result = self.get_latest_release(release_type)
            if not all(release_result):
                messagebox.showerror("Install Yuzu", f"There was an error while attempting to fetch the latest release of Yuzu:\n\n{release_result[1]}")
                return
            release = release_result[1]
            if release.version == self.metadata.get_installed_version(release_type):
                if updating:
                    return 
                if not messagebox.askyesno("Yuzu", f"You already have the latest version of yuzu {release_type.replace('_',' ').title()} installed, download anyways?"):
                    return
            download_result = self.download_release(release, release_type)
            if not all(download_result):
                if download_result[1] != "Cancelled":
                    messagebox.showerror("Error", f"There was an error while attempting to download the latest release of yuzu {release_type.replace('_',' ').title()}:\n\n{download_result[1]}")
                return 
            release_archive = download_result[1]
        elif not self.verify_yuzu_zip(path_to_archive, release_type):
            messagebox.showerror("Error", "The archive you have provided is invalid")
            return 
        extract_result = self.extract_release(release_archive, release_type)
        if not all(extract_result):
            if extract_result[1]!="Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{extract_result[1]}")
            return 
        if path_to_archive is None:
            self.metadata.update_installed_version(release_type, release.version)
        if path_to_archive is None and self.settings.app.delete_files == "True" and os.path.exists(release_archive):
            os.remove(release_archive)
        messagebox.showinfo("Install Yuzu", f"Yuzu was successfully installed to {extract_result[1]}")

        
    def launch_yuzu_installer(self):
        path_to_installer = self.settings.yuzu.installer_path
        self.running = True
        subprocess.run([path_to_installer], capture_output = True, check=False)
        self.running = False
        
    def delete_mainline(self, skip_prompt=False):
        try:
            shutil.rmtree(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc"))
            if not skip_prompt:
                messagebox.showinfo("Delete Yuzu", "Installation of yuzu successfully deleted")
        except Exception as error:
            messagebox.showerror("Delete Error", f"An error occured while trying to delete the installation of yuzu:\n\n{error}")
        
    def launch_yuzu_handler(self, release_type, skip_update=False):
        if not skip_update:
            if (release_type == "mainline" and self.settings.app.use_yuzu_installer == "False") or release_type == "early_access":
                func = self.gui.configure_mainline_buttons if release_type == "mainline"  else self.gui.configure_early_access_buttons
                func("disabled", text="Fetching Updates...  ")
                self.install_release_handler(release_type, True)
        if release_type == "mainline":
            self.gui.configure_mainline_buttons("disabled", text="Launching...  ")
            yuzu_folder = "yuzu-windows-msvc"
        elif release_type == "early_access":
            self.gui.configure_early_access_buttons("disabled", text="Launching...  ")
            yuzu_folder = "yuzu-windows-msvc-early-access"    
        self.verify_and_install_firmware_keys()
        func_to_call=self.gui.configure_mainline_buttons if release_type == "mainline" else self.gui.configure_early_access_buttons
        func_to_call("disabled", text="Launched!  ")
        yuzu_exe = os.path.join(self.settings.yuzu.install_directory, yuzu_folder, "yuzu.exe")
        maintenance_tool = os.path.join(self.settings.yuzu.install_directory, "maintenancetool.exe")
        args = [maintenance_tool, "--launcher", yuzu_exe] if release_type == "mainline" and self.settings.app.use_yuzu_installer == "True" and not skip_update else [yuzu_exe]
        self.running = True
        subprocess.run(args, capture_output=True, check=False)
        self.running = False
        
    def verify_and_install_firmware_keys(self):
        if not switch_emu.check_current_keys(os.path.join(self.settings.yuzu.user_directory, "keys", "prod.keys")):
            messagebox.showwarning("Missing Keys", "It seems you are missing the switch decryption keys. These keys are required to emulate games. Please install them using the download button below")
        
        if self.settings.app.ask_firmware != "False" and not switch_emu.check_current_firmware(os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")):
            if not messagebox.askyesno("Firmware Missing", "It seems you are missing the switch firmware files. Without these files, some games may not run. You can install the firmware using the buttons below. Press Yes to remind you later or No to never ask again."):
                self.settings.app.ask_firmware = "False"
            

       
    def install_firmware_handler(self, mode, path_or_release):
        if switch_emu.check_current_firmware(os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")) and not messagebox.askyesno("Firmware Exists", "You already seem to have firmware installed, install anyways?"):
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
        
        result = switch_emu.install_firmware_from_archive(firmware_path, os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered"), self.main_progress_frame, "yuzu")
        if not result[0]:
            messagebox.showerror("Extract Error", f"There was an error while trying to extract the firmware archive: \n\n{result[1]}")
            return 
        result = result[1]
        if mode == "release": 
            if self.settings.app.delete_files == "True" and os.path.exists(firmware_path):
                try:
                    os.remove(firmware_path)
                except PermissionError as error:
                    messagebox.showerror("Error", f"Failed to delete firmware archive after installing due to error below: \n\n{error}")
            self.metadata.update_installed_version("yuzu_firmware", version)
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
        if switch_emu.check_current_keys(os.path.join(self.settings.yuzu.user_directory, "keys", "prod.keys")) and not messagebox.askyesno("Keys Exist", "You already seem to have the decryption keys, install anyways?"):
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
            switch_emu.install_keys_from_file(key_path, os.path.join(self.settings.yuzu.user_directory, "keys"))
        else:
            result = switch_emu.install_keys_from_archive(key_path, os.path.join(self.settings.yuzu.user_directory, "keys"), self.main_progress_frame)
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
            self.metadata.update_installed_version("yuzu_keys", version)
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
    

        
    def export_yuzu_data(self, mode, directory_to_export_to):
        user_directory = self.settings.yuzu.user_directory
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No yuzu data on local drive found")
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Yuzu Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(directory_to_export_to, 'nand', 'user', 'save'), "Exporting Yuzu Save Data", self.data_progress_frame)
        elif mode == "Exclude 'nand' & 'keys'":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Yuzu Data", self.data_progress_frame, ["nand", "keys"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def import_yuzu_data(self, mode, directory_to_import_from):
        user_directory = self.settings.yuzu.user_directory
        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
            return
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Yuzu Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(directory_to_import_from, 'nand', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(user_directory, 'nand', 'user', 'save'), "Importing Yuzu Save Data", self.data_progress_frame)
        elif mode == "Exclude 'nand' & 'keys'":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Yuzu Data", self.data_progress_frame, ["nand", "keys"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def delete_yuzu_data(self, mode):
        result = ""

        user_directory = self.settings.yuzu.user_directory
    
        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except Exception as error:
                    messagebox.showerror("Delete Yuzu Data", f"Unable to delete {directory}:\n\n{error}")
                    return False
            return False

        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
        elif mode == "Exclude 'nand' & 'keys'":
            deleted = False
            for root_folder in user_directory:
                if os.path.exists(root_folder) and os.listdir(root_folder):
                    subfolders_failed = []
                    for folder_name in os.listdir(root_folder):
                        folder_path = os.path.join(root_folder, folder_name)
                        if os.path.isdir(folder_path) and not(folder_name == 'nand' or folder_name == 'keys'):
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

