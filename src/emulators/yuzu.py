import json
import os
import shutil
import subprocess
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

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
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False
        
    def check_current_firmware(self):

        if os.path.exists ( os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")) and os.listdir(os.path.join(self.settings.yuzu.user_directory, "nand\\system\\Contents\\registered")):
            return True
        return False

    def check_current_keys(self):
        if os.path.exists(os.path.join(self.settings.yuzu.user_directory, "keys", "prod.keys")):
            return True 
        return False
    
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
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Yuzu {release.version}" if release_type == "mainline" else f"Yuzu EA {release.version}")
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.total_size = release.size
        download_path = os.path.join(os.getcwd(), f"Yuzu-{release.version}.zip" if release_type == "mainline" else f"Yuzu-EA-{release.version}.zip")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
        progress_frame.destroy()
        return download_result
    
    def extract_release(self, zip_path, release_type):
        extract_folder = self.settings.yuzu.install_directory
        extracted_files = []
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, os.path.basename(zip_path))
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.skip_to_installation()
        progress_frame.update_extraction_progress(0)
        progress_frame.update_status_label("Status: Extracting... ")
        progress_frame.cancel_download_button.configure(state="normal")
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc" if release_type == "mainline" else "yuzu-windows-msvc-early-access")):
            self.delete_mainline(True) if release_type == "mainline" else self.delete_early_access(True)
        try:
            with ZipFile(zip_path, 'r') as archive:
                total_files = len(archive.namelist())     
                for file in archive.namelist():
                    if progress_frame.cancel_download_raised:
                        progress_frame.destroy()
                        return (False, "Cancelled")
                    archive.extract(file, extract_folder)
                    extracted_files.append(file)
                    # Calculate and display progress
                    progress_frame.update_extraction_progress(len(extracted_files) / total_files) 
        except Exception as error:
            progress_frame.destroy()
            return (False, error)
        progress_frame.destroy()
        return (True, extract_folder)
    
    def install_release_handler(self, release_type, updating=False):
        release_result = self.get_latest_release(release_type)
        if not all(release_result):
            messagebox.showerror("Install Yuzu", f"There was an error while attempting to fetch the latest release of Yuzu:\n\n{release_result[1]}")
        release = release_result[1]
        if release.version == self.metadata.get_installed_version(release_type):
            if updating:
                return 
            messagebox.showinfo("Yuzu", f"You already have the latest version of yuzu {release_type.replace('_',' ').title()} installed")
            return
        download_result = self.download_release(release, release_type)
        if not all(download_result):
            if download_result[1] != "Cancelled":
                messagebox.showerror("Error", f"There was an error while attempting to download the latest release of yuzu {release_type.replace('_',' ').title()}:\n\n{download_result[1]}")
            return 
        release_archive = download_result[1]
        extract_result = self.extract_release(release_archive, release_type)
        if not all(extract_result):
            if extract_result[1]!="Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{extract_result[1]}")
            return 
        self.metadata.update_installed_version(release_type, release.version)
        if self.settings.app.delete_files == "True" and os.path.exists(release_archive):
            os.remove(release_archive)
        messagebox.showinfo("Install Yuzu", f"Yuzu was successfully installed to {extract_result[1]}")

        
    def launch_yuzu_installer(self):
        path_to_installer = self.settings.yuzu.installer_path
        self.running = True
        subprocess.run([path_to_installer], capture_output = True)
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
                a=self.gui.configure_mainline_buttons("disabled", text="Fetching Updates...  ") if release_type == "mainline"  else self.gui.configure_early_access_buttons("disabled", text="Fetching Updates...  ")
                self.install_release_handler(release_type, True)
        if release_type == "mainline":
            self.gui.configure_mainline_buttons("disabled", text="Launching...  ")
            yuzu_folder = "yuzu-windows-msvc"
        elif release_type == "early_access":
            self.gui.configure_early_access_buttons("disabled", text="Launching...  ")
            yuzu_folder = "yuzu-windows-msvc-early-access"    
        self.verify_and_install_firmware_keys()
        a=self.gui.configure_mainline_buttons("disabled", text="Launched!  ") if release_type == "mainline" else self.gui.configure_early_access_buttons("disabled", text="Launched!  ")
        yuzu_exe = os.path.join(self.settings.yuzu.install_directory, yuzu_folder, "yuzu.exe")
        maintenance_tool = os.path.join(self.settings.yuzu.install_directory, "maintenancetool.exe")
        args = [maintenance_tool, "--launcher", yuzu_exe] if release_type == "mainline" and self.settings.app.use_yuzu_installer == "True" and not skip_update else [yuzu_exe]
        self.running = True
        subprocess.run(args, capture_output=True, check=False)
        self.running = False
        
    def verify_and_install_firmware_keys(self):
        if not self.check_current_keys() and messagebox.askyesno("Missing Keys", "It seems you are missing the switch decryption keys. These keys are required to emulate games. Would you like to install them?"):
            self.install_key_handler()
        
        if self.settings.app.ask_firmware != "False" and not self.check_current_firmware():
            if messagebox.askyesno("Firmware Missing", "It seems you are missing the switch firmware files. Without these files, some games may not run. Would you like to install the firmware now? If you select no, then you will not be asked again."):
                self.install_firmware_handler()
            else:
                self.settings.app.ask_firmware = "False"
            

       
    def install_firmware_handler(self):
        self.gui.configure_firmware_key_buttons("disabled")
        firmware_path = self.download_firmware_archive()
        if not all(firmware_path):
            if firmware_path[1] != "Cancelled":
                messagebox.showerror("Download Error", firmware_path[1])
            return False
        firmware_path = firmware_path[1] if isinstance(firmware_path, tuple) else firmware_path
        result = self.install_firmware_from_archive(firmware_path)
        if self.settings.app.delete_files == "True" and os.path.exists(firmware_path):
            os.remove(firmware_path)
        if result:
            messagebox.showwarning("Unexpected Files" , f"These files were skipped in the extraction process: {result}")
        messagebox.showinfo("Firmware Install", "The switch firmware files were successfully installed")
        return True 
    
    def download_firmware_archive(self):
        firmware_release = get_resources_release("Firmware", get_headers(self.settings.app.token))
        if not all(firmware_release):
            return firmware_release
            
        firmware = firmware_release[1]
        firmware.version = firmware.name.replace("Alpha.", "").replace(".zip", "")
        response_result = create_get_connection(firmware.download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response_result):
            return response_result

        response = response_result[1]
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Firmware {firmware.version}")
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.total_size = firmware.size
        download_path = os.path.join(os.getcwd(), f"Firmware {firmware.version}.zip")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
        progress_frame.destroy()
        if not all(download_result):
            return download_result

        download_path = download_result[1]
        
        return download_path

    def install_firmware_from_archive(self, firmware_source):
        extract_folder = os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
        extracted_files = []
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, os.path.basename(firmware_source))
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.update_extraction_progress(0)
        progress_frame.skip_to_installation()
        progress_frame.complete_download(None, "Status: Extracting...")
        excluded = []
        with open(firmware_source, "rb") as file:
            with ZipFile(file, 'r') as archive:
                total = len(archive.namelist())
                for entry in archive.infolist():
                    if entry.filename.endswith(".nca") or entry.filename.endswith(".nca/00"):
                        path_components = entry.filename.replace(".cnmt", "").split("/")
                        nca_id = path_components[-1]
                        if nca_id == "00":
                            nca_id = path_components[-2]
                        if ".nca" in nca_id:
                            extracted_file_path = os.path.join(extract_folder, nca_id)
                            os.makedirs(extract_folder, exist_ok=True)
                            with open(extracted_file_path, "wb") as f:
                                f.write(archive.read(entry))
                            extracted_files.append(entry.filename)
                            progress_frame.update_extraction_progress(len(extracted_files)/total)
                        else:
                            excluded.append(entry.filename)
        progress_frame.destroy()
        return excluded
    
    def install_key_handler(self):
        self.gui.configure_firmware_key_buttons("disabled")
        key_path = self.download_key_archive()
        if not all(key_path):
            if key_path[1] != "Cancelled":
                messagebox.showerror("Download Error", key_path[1])
            return False
        key_path = key_path[1] if isinstance(key_path, tuple) else key_path
        if key_path.endswith(".keys"):
            self.install_keys_from_file(key_path)
        else:
            result = self.install_keys_from_archive(key_path)
            if "prod.keys" not in result:
                messagebox.showwarning("Keys", "Was not able to find any prod.keys within the archive, the archive was still extracted successfully.")
                return False 
        if self.settings.app.delete_files == "True" and os.path.exists(key_path):
            os.remove(key_path)
        messagebox.showinfo("Keys", "Decryption keys were successfully installed!")
        return True 
            
    def download_key_archive(self):
        key_release = get_resources_release("Keys", get_headers(self.settings.app.token))
        if not all(key_release):
            return key_release
        
        key = key_release[1]
        key.version = key.name.replace("Beta.", "").replace(".zip","")
        response_result = create_get_connection(key.download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response_result):
            return response_result
           
        response = response_result[1]
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Keys {key.version}")
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.total_size = key.size
        download_path = os.path.join(os.getcwd(), f"Keys {key.version}.zip")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*128)
        progress_frame.destroy()
        if not all(download_result):
            return download_result
        download_path = download_result[1]
        
        return download_path
    
    def install_keys_from_file(self, key_path):
        target_key_folder = os.path.join(self.settings.yuzu.user_directory, "keys")
        if not os.path.exists(target_key_folder):
            os.makedirs(target_key_folder)
        target_key_location = os.path.join(target_key_folder, "prod.keys")
        shutil.copy(key_path, target_key_location)
        return target_key_location
    
    def install_keys_from_archive(self, archive):
        extract_folder = os.path.join(self.settings.yuzu.user_directory, "keys")
        extracted_files = []
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, os.path.basename(archive))
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.update_extraction_progress(0)
        with ZipFile(archive, 'r') as zip_ref:
            total = len(zip_ref.namelist())
            for file_info in zip_ref.infolist():
                extracted_file_path = os.path.join(extract_folder, file_info.filename)
                os.makedirs(os.path.dirname(extracted_file_path), exist_ok=True)
                with zip_ref.open(file_info.filename) as source, open(extracted_file_path, 'wb') as target:
                    target.write(source.read())
                extracted_files.append(file_info.filename)
                progress_frame.update_extraction_progress(len(extracted_files)/total)
        progress_frame.destroy()
        return extracted_files
        
    def export_yuzu_data(self, mode):
        user_directory = self.settings.yuzu.user_directory
        export_directory = self.settings.yuzu.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No yuzu data on local drive found")
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            copy_directory_with_progress(user_directory, users_export_directory, "Exporting All Yuzu Data", self.gui.yuzu_data_log)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(users_export_directory, 'nand', 'user', 'save'), "Exporting Yuzu Save Data", self.gui.yuzu_data_log)
        elif mode == "Exclude 'nand' & 'keys'":
            copy_directory_with_progress(user_directory, users_export_directory, "Exporting All Yuzu Data", self.gui.yuzu_data_log, ["nand", "keys"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def import_yuzu_data(self, mode):
        export_directory = self.settings.yuzu.export_directory
        user_directory = self.settings.yuzu.user_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
            return
        if mode == "All Data":
            copy_directory_with_progress(users_export_directory, user_directory, "Import All Yuzu Data", self.gui.yuzu_data_log)
        elif mode == "Save Data":
            save_dir = os.path.join(users_export_directory, 'nand', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(user_directory, 'nand', 'user', 'save'), "Importing Yuzu Save Data", self.gui.yuzu_data_log)
        elif mode == "Exclude 'nand' & 'keys'":
            copy_directory_with_progress(users_export_directory, user_directory, "Import All Yuzu Data", self.gui.yuzu_data_log, ["nand", "keys"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def delete_yuzu_data(self, mode):
        result = ""

        user_directory = self.settings.yuzu.user_directory
        export_directory = self.settings.yuzu.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except:
                    messagebox.showerror("Delete Yuzu Data", f"Unable to delete {directory}")
                    return False
            return False

        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
        elif mode == "Exclude 'nand' & 'keys'":
            # Iterate through each of the 3 root folders and exclude 'nand' and 'keys' subfolder
            deleted = False
            for root_folder in [user_directory, users_export_directory]:
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

