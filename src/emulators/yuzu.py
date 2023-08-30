import json
import os
import shutil
import subprocess
import time
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

import requests

from gui.progress_frame import ProgressFrame
from utils.file_utils import copy_directory_with_progress


class Yuzu:
    def __init__(self, gui, settings):
        self.settings = settings
        self.gui = gui
        self.updating_ea = False
    def check_yuzu_installation(self):
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc", 'yuzu.exe')):
            return True
        else:
            return False
    def check_yuzu_installer(self):
        path = self.settings.yuzu.installer_path
        if os.path.exists(path):
            return True
        return False 
        
    def check_current_firmware(self):

        if os.path.exists ( os.path.join(self.settings.yuzu.user_directory, "nand", "system", "Contents", "registered")) and os.listdir(os.path.join(self.settings.yuzu.user_directory, "nand\\system\\Contents\\registered")):
            return True
        return False

    def check_current_keys(self):
        if os.path.exists(os.path.join(self.settings.yuzu.user_directory, "keys", "prod.keys")):
            return True 
        return False

    def verify_firmware_archive(self):
        archive = self.settings.yuzu.firmware_path
        if not os.path.exists(archive):
            return False 
        if not archive.endswith(".zip"):
            return False 
        with ZipFile(archive, 'r') as r_archive:
            for filename in r_archive.namelist():
                if not filename.endswith(".nca"):
                    return False 
        return True 
        
    def verify_key_archive(self):
        archive = self.settings.yuzu.key_path
        if not os.path.exists(archive):
            return False 
        if not archive.endswith(".zip"):
            return False 
        with ZipFile(archive, 'r') as r_archive:
            for filename in r_archive.namelist():
                if not filename.endswith(".keys"):
                    return False 
                if filename=="prod.keys":
                    found=True
        if found:
            return True 
        else:
            return False 
    
    def run_yuzu_install_wrapper(self, event=None):
        if self.gui.yuzu_install_yuzu_button.cget("state") == "disabled":
            return
        if event is None:
            return
        if not self.check_yuzu_installer():
            messagebox.showerror("Yuzu Error", "Please verify that you have specified the path to the yuzu installer in the settings page.")
            return
        
        self.gui.yuzu_install_yuzu_button.configure(state="disabled")
        self.gui.yuzu_launch_yuzu_button.configure(state="disabled")
        Thread(target=self.run_yuzu_install).start()
    
    def run_yuzu_install(self):
        temp_dir = os.path.join(os.getenv("TEMP"),"yuzu-installer")
        os.makedirs(temp_dir, exist_ok=True)
        path_to_installer = self.settings.yuzu.installer_path
        target_installer = os.path.join(temp_dir, 'yuzu_install.exe')
        try:
            shutil.copy(path_to_installer, target_installer)
        except Exception as error:
            messagebox.showerror("Copy Error", f"Unable to make a copy of yuzu_install.exe\n\n{error}")
        subprocess.run([target_installer], capture_output = True)
        time.sleep(0.3) # trying to delete instantly causes PermissionError
        try:
            shutil.rmtree(temp_dir)
        except PermissionError as error:
            messagebox.showerror("Delete Error", "Unable to delete temporary yuzu installer directory.")
        except Exception as error:
            messagebox.showerror("Error", f"An unexpected error has occured: \n{error}")
        self.gui.yuzu_install_yuzu_button.configure(state="normal")
        self.gui.yuzu_launch_yuzu_button.configure(state="normal")
    
    def check_and_install_yuzu_ea(self):
        if self.check_for_ea_update():
            if messagebox.askyesno("Yuzu Early Access", "There is an update available, do you wish to download it?"):
                self.gui.yuzu_launch_yuzu_button.configure(state="disabled", text="Updating...  ", width=170)
                Thread(target=self.install_ea_yuzu, args=(True, )).start()
                return
        self.gui.yuzu_install_yuzu_button.configure(state="disabled")
        self.gui.yuzu_launch_yuzu_button.configure(state="disabled", text="Launching...  ", width=170)
        Thread(target=self.start_yuzu, args=(None,True,)).start()
    def start_yuzu_wrapper(self, event=None, ea_mode=None):
        if self.gui.yuzu_launch_yuzu_button.cget("state") == "disabled":
            return
        if event==None:
            return
        if ea_mode:
            self.gui.yuzu_launch_yuzu_button.configure(state="disabled", text="Checking for Updates...  ", width=220)
            Thread(target=self.check_and_install_yuzu_ea).start()
            return
        if not self.check_yuzu_installation():
            messagebox.showerror("Yuzu", "Please ensure that you have installed yuzu before trying to launch it")
            return
        self.gui.yuzu_install_yuzu_button.configure(state="disabled")
        self.gui.yuzu_launch_yuzu_button.configure(state="disabled", text="Launching...  ")
        Thread(target=self.start_yuzu, args=(event,ea_mode,)).start()
    
    def start_yuzu(self, event=None, ea_mode=False):
        if self.gui.yuzu_global_data.get() == "1" and os.path.exists(os.path.join(self.settings.yuzu.global_save_directory, os.getlogin())):
            try:
                copy_directory_with_progress((os.path.join(self.settings.yuzu.global_save_directory, os.getlogin())), self.settings.yuzu.user_directory, "Loading Yuzu Data", self.gui.yuzu_log_frame)
            except Exception as error:
                for widget in self.gui.yuzu_log_frame.winfo_children():
                        widget.destroy()
                if not messagebox.askyesno("Error", f"Unable to load your data, would you like to continue\n\n Full Error: {error}"):
                    self.gui.yuzu_launch_yuzu_button.configure(state="normal", text="Launch Yuzu  ")
                    self.gui.yuzu_install_yuzu_button.configure(state="normal")
                    return 
                    
        if not self.check_current_firmware() or not self.check_current_keys():
            if messagebox.askyesno("Error","You are missing your keys or firmware. Keys are required. Without the firmware, some games will not run (e.g. Mario Kart 8 Deluxe). Would you like to install the missing files?"):
                if not self.install_missing_firmware_or_keys():
                    self.gui.yuzu_launch_yuzu_button.configure(state="normal", text="Launch Yuzu  ")
                    self.gui.yuzu_install_yuzu_button.configure(state="normal")
                    return
        
        
        maintenance_tool = os.path.join(self.settings.yuzu.install_directory, "maintenancetool.exe")
        yuzu_exe = os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc","yuzu.exe") if not ea_mode else os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access", "yuzu.exe")
        if ea_mode or (not event is None and event.state & 1):  # either shift key was pressed or launching yuzu EA
            args = [yuzu_exe]
        elif not event.state & 1 and os.path.exists(maintenance_tool):  # Button was clicked normally so run maintenance tool to update yuzu and then launch
            args = [maintenance_tool,"--launcher",yuzu_exe,]  
        self.gui.yuzu_launch_yuzu_button.configure(text="Launched!  ")
        
        try:     
            subprocess.run(args, capture_output=True) # subprocess.run with arguments defined earlier
        except Exception as error_msg:
            messagebox.showerror("Error", f"Error when running Yuzu: \n{error_msg}")
        if self.gui.yuzu_global_data.get() == "1":
            try:
                self.gui.yuzu_launch_yuzu_button.configure(state="disabled", text="Launch Yuzu  ")
                copy_directory_with_progress(self.settings.yuzu.user_directory, (os.path.join(self.settings.yuzu.global_save_directory, os.getlogin())), "Saving Yuzu Data", self.gui.yuzu_log_frame)
            except Exception as error:
                messagebox.showerror("Save Error", f"Unable to save your data\n\nFull Error: {error}")
        self.gui.yuzu_launch_yuzu_button.configure(state="normal", text="Launch Yuzu  ")
        self.gui.yuzu_install_yuzu_button.configure(state="normal")
    
    
    def check_for_ea_update(self):
        
        contents = self.get_launcher_file_content()
        ea_info = contents['yuzu']['early_access']
        if contents:
            installed = ea_info["installed_version"]
        else:
            installed = ''
        
        latest_release = self.get_latest_yuzu_ea_release()
        if latest_release.version != installed:
            return latest_release
        else:
            return False
        
    def install_ea_yuzu_wrapper(self, event):
        if not messagebox.askyesno("Confirmation", "This will require an internet connection and will download the files from the internet, continue?"):
            return 
        self.gui.yuzu_install_yuzu_button.configure(state="disabled")
        self.gui.yuzu_launch_yuzu_button.configure(state="disabled")
        Thread(target=self.install_ea_yuzu).start()

    def reset_launcher_file(self):
        launcher_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "launcher.json")
        if not os.path.exists(os.path.dirname(launcher_file)):
            os.makedirs(os.path.dirname(launcher_file))
        with open(launcher_file, "w") as f:
            template = {
                "dolphin": {},
                "yuzu": {
                    "early_access": {
                        "installed_version": ''
                    }
                }
            }
            json.dump(template, f)
    def get_launcher_file_content(self):
        launcher_file = os.path.join(
            os.getenv("APPDATA"), "Emulator Manager", "launcher.json"
        )
        if os.path.exists(launcher_file):
            with open(launcher_file, 'r') as f:
                try:
                    contents = json.load(f)
                    if contents["yuzu"]["early_access"]["installed_version"] and not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access", "yuzu.exe")):
                        contents["yuzu"]["early_access"]["installed_version"] = ''
                except (KeyError, json.decoder.JSONDecodeError):
                    self.reset_launcher_file()
                    
                return contents
        else:
            return None

    def get_latest_yuzu_ea_release(self):
        class Release:
            def __init__(self) -> None:
                self.version = None
                self.download_url = None
                self.size = None 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
        }
        api_url = 'https://api.github.com/repos/pineappleEA/pineapple-src/releases'
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
        except requests.exceptions.RequestException:
            messagebox.showerror("Requests Error", "Failed to connect to API")
            return None
        try:
            release_info = json.loads(response.text)[0]
        except KeyError:
            messagebox.showerror("API Error", "Unable to handle response, could be an API ratelimit")
            return None
        latest_version = release_info["tag_name"].split("-")[-1]
        assets = release_info['assets']
        for asset in assets:
            if 'Windows' in asset['name']:
                url = asset['browser_download_url']
                size = asset['size']
                break
        release=Release()
        release.version = latest_version
        release.download_url = url
        release.size = size

        return release   
    def install_ea_yuzu(self, start_yuzu=False):
        # Get latest release info 
        self.updating_ea = True
        def download_latest_release(latest_release): 
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            download_path = os.path.join(temp_path, "yuzu-ea.zip")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
            response = requests.get(latest_release.download_url, stream=True, headers=headers, timeout=10)
            
            progress_frame.grid(row=0, column=0, sticky="ew")
            progress_frame.total_size = latest_release.size
            with open(download_path, 'wb') as f:
                downloaded_bytes = 0
                for chunk in response.iter_content(chunk_size=1024*512): 
                    if progress_frame.cancel_download_raised:
                        self.updating_ea = False
                        self.gui.yuzu_install_yuzu_button.configure(state="normal")
                        self.gui.yuzu_launch_yuzu_button.configure(state="normal")
                        progress_frame.destroy()
                        return
                    f.write(chunk)
                    downloaded_bytes += len(chunk)
                    progress_frame.update_download_progress(downloaded_bytes, 1024*512)
            progress_frame.complete_download(None, "Status: Extracting...")
            progress_frame.progress_bar.set(0)
            return download_path
        
        def extract_release_files(archive):
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            extract_folder = os.path.join(temp_path, "yuzu-ea")
            with ZipFile(archive, 'r') as zip_file:
                zip_file.extractall(extract_folder)
            progress_frame.progress_bar.set(1)
            return extract_folder
        
        yuzu_path = os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")
        temp_path = os.path.join(os.getenv("TEMP"), "Emulator Manager", "Yuzu Early Access Files")

        launcher_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "launcher.json")
        # Parse asset info
        contents = self.get_launcher_file_content()
        latest_release = self.check_for_ea_update()
        ea_info = contents['yuzu']['early_access']
        if contents:
            installed = ea_info["installed_version"]
        else:
            installed = ''
        
        if not latest_release:
            self.updating_ea = False
            self.gui.yuzu_install_yuzu_button.configure(state="normal")
            self.gui.yuzu_launch_yuzu_button.configure(state="normal")
            return

        if installed == latest_release.version:
            messagebox.showinfo("Info", "You already have the latest version of yuzu EA installed!")
        else:    

            # Download file
            progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Yuzu EA {latest_release.version}")
            early_access_zip = download_latest_release(latest_release)
            
            # Extract
            extracted_release = extract_release_files(early_access_zip)
            # Move and delete zip   
          
            try:
                if os.path.exists(yuzu_path):
                    shutil.rmtree(yuzu_path)
                shutil.move(os.path.join(extracted_release, "yuzu-windows-msvc-early-access"), yuzu_path) 
                installed = latest_release.version
            except Exception as error:
                messagebox.showerror("Error", error)
            
            with open(launcher_file, "w") as f:
                contents["yuzu"]["early_access"]["installed_version"] = installed
                json.dump(contents, f)
            progress_frame.finish_installation()
            progress_frame.destroy()
            
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        self.updating_ea = False
        if start_yuzu:
            self.gui.yuzu_install_yuzu_button.configure(state="disabled")
            self.gui.yuzu_launch_yuzu_button.configure(state="disabled", text="Launching...  ")
            Thread(target=self.start_yuzu, args=(None,True,)).start()
        else:
            self.gui.yuzu_install_yuzu_button.configure(state="normal")
            self.gui.yuzu_launch_yuzu_button.configure(state="normal")

            
    
    
    
    
    
    
    def install_missing_firmware_or_keys(self):
    
        if not self.check_current_keys():
            if not self.verify_key_archive():
                messagebox.showerror("Key Error", "Please verify that you have correctly set the path for the key archive in the settings page.")
            else:
                status_frame = ProgressFrame(
                self.gui.yuzu_log_frame, (os.path.basename(self.settings.yuzu.key_path)))
                status_frame.grid(row=0, pady=10, sticky="EW")
                status_frame.skip_to_installation()
                try:
                    self.gui.yuzu_firmware.start_key_installation_custom(self.settings.yuzu.key_path, status_frame)
                except Exception as error:
                    messagebox.showerror("Unknown Error", f"An unknown error occured during key installation \n\n {error}")
                    status_frame.destroy()
                    return False
                status_frame.destroy()
        if not self.check_current_firmware():
            if not self.verify_firmware_archive():
                messagebox.showerror("Firmware Error", "Please verify that you have correctly set the path for the firmware archive in the settings page.")
            else:
                status_frame = ProgressFrame(self.gui.yuzu_log_frame, (os.path.basename(self.settings.yuzu.firmware_path)))
                status_frame.grid(row=0, pady=10, sticky="EW")
                status_frame.skip_to_installation()
                try:
                    self.gui.yuzu_firmware.start_firmware_installation_from_custom_zip(self.settings.yuzu.firmware_path, status_frame)
                except Exception as error:
                    messagebox.showerror("Unknown Error", f"An unknown error occured during firmware installation \n\n {error}")
                    status_frame.destroy()
                    return False
                status_frame.destroy()
        if self.check_current_firmware() and self.check_current_keys():
            return True
       
    
    
        
    def export_yuzu_data(self):
        self.gui.configure_data_buttons(state="disabled")
        mode = self.gui.yuzu_export_optionmenu.get()
        user_directory = self.settings.yuzu.user_directory
        export_directory = self.settings.yuzu.export_directory
        users_global_save_directory = os.path.join(export_directory, os.getlogin())
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No yuzu data on local drive found")
            self.gui.configure_data_buttons(state="normal")
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            self.start_copy_thread(user_directory, users_export_directory, "Exporting All Yuzu Data", self.gui.yuzu_data_log)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            self.start_copy_thread(save_dir, os.path.join(users_export_directory, 'nand', 'user', 'save'), "Exporting Yuzu Save Data", self.gui.yuzu_data_log)
        elif mode == "Exclude 'nand' & 'keys'":
            self.start_copy_thread(user_directory, users_export_directory, "Exporting All Yuzu Data", self.gui.yuzu_data_log, ["nand", "keys"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def import_yuzu_data(self):
        self.gui.configure_data_buttons(state="disabled")
        mode = self.gui.yuzu_import_optionmenu.get()
        export_directory = self.settings.yuzu.export_directory
        user_directory = self.settings.yuzu.user_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
            self.gui.configure_data_buttons(state="normal")
            return
        if mode == "All Data":
            self.start_copy_thread(users_export_directory, user_directory, "Import All Yuzu Data", self.gui.yuzu_data_log)
        elif mode == "Save Data":
            save_dir = os.path.join(users_export_directory, 'nand', 'user', 'save')
            self.start_copy_thread(save_dir, os.path.join(user_directory, 'nand', 'user', 'save'), "Importing Yuzu Save Data", self.gui.yuzu_data_log)
        elif mode == "Exclude 'nand' & 'keys'":
            self.start_copy_thread(users_export_directory, user_directory, "Import All Yuzu Data", self.gui.yuzu_data_log, ["nand", "keys"])
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")
    def delete_yuzu_data(self):
        self.gui.configure_data_buttons(state="disabled")
        if not messagebox.askyesno("Confirmation", "This will delete the data from Yuzu's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
            self.gui.configure_data_buttons(state="normal")
            return

        mode = self.gui.yuzu_delete_optionmenu.get()
        result = ""

        user_directory = self.settings.yuzu.user_directory
        global_save_directory = self.settings.yuzu.global_save_directory
        export_directory = self.settings.yuzu.export_directory
        users_global_save_directory = os.path.join(global_save_directory, os.getlogin())
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
            result += f"Data deleted from {users_global_save_directory}\n" if delete_directory(users_global_save_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            save_dir = os.path.join(global_save_directory, os.getlogin(), 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            if export_directory != global_save_directory:
                save_dir = os.path.join(export_directory, os.getlogin(), 'nand', 'user', 'save')
                result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
        elif mode == "Exclude 'nand' & 'keys'":
            # Iterate through each of the 3 root folders and exclude 'nand' subfolder
            for root_folder in [user_directory, users_global_save_directory, users_export_directory]:
                if os.path.exists(root_folder) and os.listdir(root_folder):
                    subfolders_failed = []
                    deleted = False
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
    def start_copy_thread(self, *args):
        thread=Thread(target=copy_directory_with_progress, args=args)
        thread.start()
        Thread(target=self.wait_on_thread, args=(thread,)).start()
    def wait_on_thread(self, thread):
        thread.join()
        self.gui.configure_data_buttons(state="normal")