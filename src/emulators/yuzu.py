from tkinter import messagebox
import os
from threading import Thread
import shutil 
import json
import time
import requests
import subprocess
from zipfile import ZipFile
from utils.file_utils import copy_directory_with_progress
from gui.progress_frame import ProgressFrame
class Yuzu:
    def __init__(self, gui, settings):
        self.settings = settings
        self.gui = gui
    def start(self):
        print("starting yuzu")
    def check_yuzu_installation(self):
        self.check_yuzu_firmware_and_keys()
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,'yuzu.exe')):
            self.yuzu_installed = True
            return True
        else:
            self.yuzu_installed = False
            return False
    
    def run_yuzu_install_wrapper(self, event=None):
        if self.gui.yuzu_install_yuzu_button.cget("state") == "disabled":
            return
        if event is None:
            return
                                                                        # add checks for appropriate paths here
        
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
    
    def install_ea_yuzu_wrapper(self, event):
        if not messagebox.askyesno("Confirmation", "This will require an internet connection and will download the files from the internet, continue?"):
            return 
        self.gui.yuzu_install_yuzu_button.configure(state="disabled")
        self.gui.yuzu_launch_yuzu_button.configure(state="disabled")
        Thread(target=self.install_ea_yuzu).start()


    def get_launcher_file_content(self):
        launcher_file = os.path.join(
            os.getenv("APPDATA"), "Emulator Manager", "launcher.json"
        )
        if os.path.exists(launcher_file):
            with open(launcher_file, 'r') as f:
                contents = json.load(f)
                if contents["yuzu"]["ea_version"] and not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access", "yuzu.exe")):
                    contents["yuzu"]["ea_version"] = ''
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
    def install_ea_yuzu(self):
        # Get latest release info 
        self.updating_ea = True
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
        }

        yuzu_path = os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")
        temp_path = os.path.join(os.getenv("TEMP"), "Emulator Manager", "Yuzu Early Access Files")
        download_path = os.path.join(temp_path, "yuzu-ea.zip")

        if os.path.exists(yuzu_path):
                shutil.rmtree(yuzu_path)

        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        launcher_file = os.path.join(
            os.getenv("APPDATA"), "Emulator Manager", "launcher.json"
        )
        # Parse asset info
        try:
            contents = self.get_launcher_file_content()
            if contents:
                installed = contents["yuzu"]["ea_version"]
            else:
                installed = ''
        except (KeyError, json.decoder.JSONDecodeError):
            installed = ''
        if not installed:
            contents = {
                "dolphin": {
                    "": ""
                    },
                "yuzu": {
                    "ea_version": ""
                }
            }

        latest_release = self.get_latest_yuzu_ea_release()
        if not latest_release:
            self.updating_ea = False
            self.gui.yuzu_install_yuzu_button.configure(state="normal")
            self.gui.yuzu_launch_yuzu_button.configure(state="normal")
            return

        if installed == latest_release.version:
            messagebox.showinfo("Info", "You already have the latest version of yuzu EA installed!")
        else:    

            # Download file

            response = requests.get(latest_release.download_url, stream=True, headers=headers, timeout=10)
            progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Yuzu EA {latest_release.version}")
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
            # Extract
            extract_folder = os.path.join(temp_path, "yuzu-ea")
            with ZipFile(download_path, 'r') as zip_file:
                zip_file.extractall(extract_folder)
            progress_frame.progress_bar.set(1)
            # Move and delete zip   
            try:
                shutil.move(os.path.join(extract_folder, "yuzu-windows-msvc-early-access"), yuzu_path) 
                installed = latest_release.version
            except Exception as error:
                messagebox.showerror("Error", error)
            with open(launcher_file, "w") as f:
                contents["yuzu"]["ea_version"] = installed
                json.dump(contents, f)
            progress_frame.finish_installation()
            progress_frame.destroy()
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        self.gui.yuzu_install_yuzu_button.configure(state="normal")
        self.gui.yuzu_launch_yuzu_button.configure(state="normal")

        self.updating_ea = False
    
    
    
    
    def check_yuzu_firmware_and_keys(self):
        to_return = True
        if os.path.exists( os.path.join(self.settings.yuzu.user_directory, "keys\\prod.keys")):
            self.yuzu_keys_installed = True
        else:
            self.yuzu_keys_installed = False
            to_return = False
        if os.path.exists ( os.path.join(self.settings.yuzu.user_directory, "nand\\system\\Contents\\registered")) and os.listdir(os.path.join(self.settings.yuzu.user_directory, "nand\\system\\Contents\\registered")):
            self.firmware_installed = True
        else:
            self.firmware_installed = False
            to_return = False
        return to_return
    
    def install_missing_firmware_or_keys(self):
        self.check_yuzu_firmware_and_keys()
        if not self.yuzu_keys_installed:
            status_frame = ProgressFrame(
            self.yuzu_log_frame, (os.path.basename(self.settings.yuzu.key_path)), self)
            status_frame.grid(row=0, pady=10, sticky="EW")
            status_frame.skip_to_installation()
            try:
                self.yuzu_firmware.start_key_installation_custom(self.settings.yuzu.key_path, status_frame)
            except Exception as error:
                messagebox.showerror("Unknown Error", f"An unknown error occured during key installation \n\n {error}")
                status_frame.destroy()
                return False
            status_frame.destroy()
        if not self.firmware_installed:
            status_frame = ProgressFrame(self.yuzu_log_frame, (os.path.basename(self.settings.yuzu.firmware_path)), self)
            status_frame.grid(row=0, pady=10, sticky="EW")
            status_frame.skip_to_installation()
            try:
                self.yuzu_firmware.start_firmware_installation_from_custom_zip(self.settings.yuzu.firmware_path, status_frame)
            except Exception as error:
                messagebox.showerror("Unknown Error", f"An unknown error occured during firmware installation \n\n {error}")
                status_frame.destroy()
                return False
            status_frame.destroy()
        if self.check_yuzu_firmware_and_keys():
            return True
        else:
            messagebox.showerror("Install Error", "Unable to install keys or firmware. Try using the SwitchEmuTool to manually install through the options Menu")
    
    
    def compare_yuzu_ea_version_and_update(self, installed_version):
        self.updating_ea = True 
        latest_release = self.get_latest_yuzu_ea_release()
        if not latest_release:
            self.updating_ea = None
            return
        if installed_version != latest_release.version and messagebox.askyesno("Yuzu EA Update", "There is an update available for yuzu EA, would you like to download it?"):
                self.updating_ea = True
                self.install_ea_yuzu_wrapper(None)
        else:
            self.updating_ea = False      
            self.start_yuzu_wrapper(1, True, True)
            return
        while self.updating_ea:
            time.sleep(1)
        self.start_yuzu_wrapper(1, True, True)

    def start_yuzu_wrapper(self, event=None, ea_mode=None, skip_check=False):
        if self.gui.yuzu_launch_yuzu_button.cget("state") == "disabled":
            return
        if event==None:
            return
        if ea_mode and not skip_check:
            try:
                contents = self.get_launcher_file_content() #
                print(contents)
                if contents:
                    installed = contents["yuzu"]["ea_version"]
                else:
                    installed = ''
            except (KeyError, json.decoder.JSONDecodeError):
                installed = ''
            if not installed:
                messagebox.showerror("Error", "You need to have the early access version of yuzu installed first to use this feature")
                return
            self.updating_ea = True
            Thread(target=self.compare_yuzu_ea_version_and_update, args=(installed,)).start()
            return
                       # add checks for appropriate paths here 
        
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
                    
        if not self.check_yuzu_firmware_and_keys():
            if messagebox.askyesno("Error","You are missing your keys or firmware. Keys are required. Without the firmware, some games will not run (e.g. Mario Kart 8 Deluxe). Would you like to install the missing files?"):
                if not self.yuzu_automatic_firmwarekeys_install:
                    messagebox.showerror("Error", "The paths to the firmware and key archives have not been set or are invalid, please check the settings page.")
                    if not messagebox.askyesno("Missing Firmware or Keys",  "Would you like to launch yuzu anyways?"):
                        self.yuzu_launch_yuzu_button.configure(state="normal", text="Launch Yuzu  ")
                        self.yuzu_install_yuzu_button.configure(state="normal")
                        return
                else:
                    self.install_missing_firmware_or_keys()
        
        
        maintenance_tool = os.path.join(self.settings.yuzu.install_directory, "maintenancetool.exe")
        yuzu_exe = os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc","yuzu.exe") if not ea_mode else os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access", "yuzu.exe")
        print(maintenance_tool)
        if ea_mode or event.state & 1:  # either shift key was pressed or launching yuzu EA
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
        
    def export_yuzu_data(self):
        
        mode = self.gui.yuzu_export_optionmenu.get()
        user_directory = self.settings.yuzu.user_directory
        export_directory = self.settings.yuzu.export_directory
        users_global_save_directory = os.path.join(export_directory, os.getlogin())
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No yuzu data on local drive found")
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
        mode = self.gui.yuzu_import_optionmenu.get()
        export_directory = self.settings.yuzu.export_directory
        user_directory = self.settings.yuzu.user_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
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
        
        if not messagebox.askyesno("Confirmation", "This will delete the data from Yuzu's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
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
                        print(folder_name)
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
        Thread(target=copy_directory_with_progress, args=args).start()