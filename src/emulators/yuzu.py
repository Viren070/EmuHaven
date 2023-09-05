import json
import os
import shutil
import subprocess
import time
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

import requests

from gui.frames.progress_frame import ProgressFrame
from utils.file_utils import copy_directory_with_progress
from utils.requests_utils import get_headers, get_resources_release, create_get_connection, get_release_from_assets, get_assets_from_latest_release
from utils.downloader import download_through_stream

class Yuzu:
    def __init__(self, gui, settings):
        self.settings = settings
        self.gui = gui
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False
    def check_yuzu_installation(self):
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc", 'yuzu.exe')):
            return True
        else:
            return False
    def check_yuzu_ea_installation(self):
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access", 'yuzu.exe')):
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
        if archive.endswith("prod.keys"):
            return True
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
    
    def get_latest_yuzu_ea_release(self):
        response = create_get_connection('https://api.github.com/repos/pineappleEA/pineapple-src/releases', headers=get_headers(self.settings.app.token))
        if not all(response): return (False, response[1])
        response = response[1]
        try:
            release_info = json.loads(response.text)[0]
            latest_version = release_info["tag_name"].split("-")[-1]
            assets = release_info['assets']
        except KeyError:
            return (False, "API Rate Limited")
        release = get_release_from_assets(assets, "Windows")
        release.version = latest_version
        return (True, release )
        
    def get_latest_yuzu_mainline_release(self):
        response = create_get_connection('https://api.github.com/repos/yuzu-emu/yuzu-mainline/releases', headers=get_headers(self.settings.app.token))
        if not all(response): return (False, response[1])
        response = response[1]
        try:
            release_info = json.loads(response.text)[0]
            latest_version = release_info["tag_name"].split("-")[-1]
            assets = release_info['assets']
        except KeyError:
            return (False, "API Rate Limited")
        release = get_release_from_assets(assets, "yuzu-windows-msvc-{}.zip", True)
        release.version = latest_version
        return (True, release )
    def download_latest_mainline_release(self):
        mainline_release_result = self.get_latest_yuzu_mainline_release()
        if not all(mainline_release_result):
            return mainline_release_result
        mainline_release = mainline_release_result[1]
        response_result = create_get_connection(mainline_release.download_url, stream=True, headers=get_headers(self.settings.app.token))
        if not all(response_result):
            return response_result 
        response = response_result[1]   
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Yuzu {mainline_release.version}")
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.total_size = mainline_release.size
        download_path = os.path.join(os.getcwd(), f"Yuzu-{mainline_release.version}.zip")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
        progress_frame.destroy()
        if not all(download_result):
            return download_result
        return (True, download_result[1])
    
    def install_mainline_from_zip(self, zip_path):
        extract_folder = self.settings.yuzu.install_directory
        extracted_files = []
        progress_frame = ProgressFrame(self.gui.yuzu_log_frame, os.path.basename(zip_path))
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.skip_to_installation()
        progress_frame.update_extraction_progress(0)
        progress_frame.update_status_label("Status: Extracting... ")
        if os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc")):
            self.delete_mainline()
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
    
    def install_mainline_handler(self):
        latest_mainline_release = self.download_latest_mainline_release()
        if not all(latest_mainline_release):
            messagebox.showerror("Error", f"There was an error while attempting to download the latest release of Yuzu:\n\n{latest_mainline_release[1]}")
            return 
        path_to_mainline_zip = latest_mainline_release[1]
        result = self.install_mainline_from_zip(path_to_mainline_zip)
        if not all(result):
            if result[1]!="Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{result[1]}")
            return 
        messagebox.showinfo("Install Yuzu", f"Yuzu was successfully installed to {result[1]}")
    
    def delete_mainline(self):
        try:
            shutil.rmtree(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc"))
        except Exception as error:
            messagebox.showerror("Delete Error", f"An error occured while trying to delete the installation of yuzu:\n\n{error}")
    def run_yuzu_install_wrapper(self):
        if not self.check_yuzu_installer():
            messagebox.showerror("Yuzu Error", "Please verify that you have specified the path to the yuzu installer in the settings page.")
            return
        self.gui.configure_mainline_buttons(state="disabled")
        Thread(target=self.run_yuzu_install).start()
    
    def run_yuzu_install(self):
        path_to_installer = self.settings.yuzu.installer_path
        self.running = True
        subprocess.run([path_to_installer], capture_output = True)
        self.running = False
        self.gui.configure_mainline_buttons(state="normal")
    
    def check_and_install_yuzu_ea(self):
        if not self.updating_ea and self.check_for_ea_update():
            if messagebox.askyesno("Yuzu Early Access", "There is an update available, do you wish to download it?"):
                self.gui.launch_early_access_button.configure(state="disabled", text="Updating...  ", width=170)
                Thread(target=self.install_ea_yuzu, args=(True, )).start()
                return
        self.gui.launch_early_access_button.configure(state="disabled", text="Launching...  ", width=170)
        Thread(target=self.start_yuzu, args=(None,True,)).start()
    def start_yuzu_wrapper(self, event=None, ea_mode=None):
        if not ea_mode and self.gui.launch_mainline_button.cget("state") == "disabled":
            return
        elif ea_mode and self.gui.launch_early_access_button.cget("state") == "disabled":
            return
        if event==None:
            return
        if ea_mode:
            if not self.check_yuzu_ea_installation():
                messagebox.showerror("Yuzu EA", "Please ensure that you have installed yuzu EA before trying to launch it. Press 'Install Yuzu EA' to the left to install it")
                return 
            self.gui.configure_early_access_buttons(state="disabled")
            if not event.state & 1:
                self.gui.launch_early_access_button.configure(text="Fetching Updates...  ", width=200)
                Thread(target=self.check_and_install_yuzu_ea).start()
            else:
                Thread(target=self.start_yuzu, args=(None,True,)).start()
            return
        if not self.check_yuzu_installation():
            messagebox.showerror("Yuzu", "Please ensure that you have installed yuzu before trying to launch it")
            return
        
        self.gui.configure_mainline_buttons(state="disabled", text="Launching...  ")
        Thread(target=self.start_yuzu, args=(event,ea_mode,)).start()
    
    def start_yuzu(self, event=None, ea_mode=False):
        if self.gui.yuzu_global_data.get() == "True" and os.path.exists(os.path.join(self.settings.yuzu.auto_import__export_directory, os.getlogin())):
            try:
                copy_directory_with_progress((os.path.join(self.settings.yuzu.auto_import__export_directory, os.getlogin())), self.settings.yuzu.user_directory, "Loading Yuzu Data", self.gui.yuzu_log_frame)
            except Exception as error:
                for widget in self.gui.yuzu_log_frame.winfo_children():
                        widget.destroy()
                if not messagebox.askyesno("Error", f"Unable to load your data, would you like to continue\n\n Full Error: {error}"):
                    return self.gui.revert_early_access_buttons() if ea_mode else self.gui.revert_mainline_buttons()
                    
                    
        if not self.check_current_keys() and messagebox.askyesno("Missing Keys", "It seems you are missing the switch decryption keys. These keys are required to emulate games. Would you like to install them?"):
            result = self.install_key_handler()
            self.gui.configure_firmware_key_buttons("normal")
            if not result:
                return self.gui.revert_early_access_buttons() if ea_mode else self.gui.revert_mainline_buttons()
        if self.settings.app.ask_firmware != "False" and not self.check_current_firmware():
            if messagebox.askyesno("Firmware Missing", "It seems you are missing the switch firmware files. Without these files, some games may not run. Would you like to install the firmware now? If you select no, then you will not be asked again."):
                result = self.install_firmware_handler()
                self.gui.configure_firmware_key_buttons("normal")
                if not result:
                    return self.gui.revert_early_access_buttons() if ea_mode else self.gui.revert_mainline_buttons()
            else:
                self.settings.app.ask_firmware = "False"
   
                    
        
        maintenance_tool = os.path.join(self.settings.yuzu.install_directory, "maintenancetool.exe")
        yuzu_exe = os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc","yuzu.exe") if not ea_mode else os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access", "yuzu.exe")
        if ea_mode or (not event is None and event.state & 1):  # either shift key was pressed or launching yuzu EA
            args = [yuzu_exe]
        elif not event.state & 1 and os.path.exists(maintenance_tool):  # Button was clicked normally so run maintenance tool to update yuzu and then launch
            args = [maintenance_tool,"--launcher",yuzu_exe,]  
        
        self.gui.configure_early_access_buttons("disabled", text="Launched!  ") if ea_mode else self.gui.configure_mainline_buttons("disabled", text="Launched!  ")
        self.running = True
        try:     
            subprocess.run(args, capture_output=True, check=False) # subprocess.run with arguments defined earlier
        except Exception as error_msg:
            messagebox.showerror("Error", f"Error when running Yuzu: \n{error_msg}")
        self.running = False
        if self.gui.yuzu_global_data.get() == "True":
            try:
                self.gui.configure_early_access_buttons("disabled", text="Launched Yuzu EA  ") if ea_mode else self.gui.configure_mainline_buttons("disabled", text="Launch Yuzu  ")
                copy_directory_with_progress(self.settings.yuzu.user_directory, (os.path.join(self.settings.yuzu.auto_import__export_directory, os.getlogin())), "Saving Yuzu Data", self.gui.yuzu_log_frame)
            except Exception as error:
                messagebox.showerror("Save Error", f"Unable to save your data\n\nFull Error: {error}")
                
        self.gui.revert_early_access_buttons() if ea_mode else self.gui.revert_mainline_buttons()
        
    def check_for_ea_update(self):
        
        contents = self.get_launcher_file_content()
        ea_info = contents['yuzu']['early_access']
        if contents:
            installed = ea_info["installed_version"]
        else:
            installed = ''
        
        latest_release_result = get_latest_yuzu_ea_release(headers=get_headers(self.settings.app.token))
        if not all(latest_release_result):
            messagebox.showerror("Error", f"There was an error while fetching the latest release of yuzu EA:\n\n{latest_release_result[1]}")
            return 
        latest_release = latest_release_result[1]
        if latest_release.version != installed:
            return True
        else:
            return False
        
    def install_ea_yuzu_wrapper(self):
        if self.updating_ea or not messagebox.askyesno("Confirmation", "This will require an internet connection and will download the files from the internet, continue?"):
            return 
        self.gui.configure_early_access_buttons(state="disabled")
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
        launcher_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "launcher.json")
        if os.path.exists(launcher_file):
            with open(launcher_file, 'r') as f:
                try:
                    contents = json.load(f)
                    if contents["yuzu"]["early_access"]["installed_version"] and not os.path.exists(os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access", "yuzu.exe")):
                        contents["yuzu"]["early_access"]["installed_version"] = ''
                except (KeyError, json.decoder.JSONDecodeError):
                    self.reset_launcher_file()
                    return self.get_launcher_file_content()
                return contents
        else:
            self.reset_launcher_file()
            return self.get_launcher_file_content()

    
    def install_ea_yuzu(self, start_yuzu=False):
        # Get latest release info 
        self.updating_ea = True
        
        def install_yuzu_ea():
            # Download file
            progress_frame = ProgressFrame(self.gui.yuzu_log_frame, f"Yuzu EA {latest_release.version}")
            early_access_zip = download_latest_release(latest_release, progress_frame)
            # Extract
            if early_access_zip:
                extracted_release = extract_release_files(early_access_zip, progress_frame)
            # Move and delete zip   
                try:
                    shutil.rmtree(yuzu_path) if os.path.exists(yuzu_path) else None
                    shutil.move(os.path.join(extracted_release, "yuzu-windows-msvc-early-access"), yuzu_path) 
                    installed = latest_release.version
                    with open(launcher_file, "w") as f:
                        contents["yuzu"]["early_access"]["installed_version"] = installed
                        json.dump(contents, f)
                except Exception as error:
                    messagebox.showerror("Error", error)
            progress_frame.destroy()
            
        def download_latest_release(latest_release, progress_frame): 
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            download_path = os.path.join(temp_path, "yuzu-ea.zip")
            response_result = create_get_connection(latest_release.download_url, stream=True, headers=get_headers(self.settings.app.token))
            if not all(response_result):
                messagebox.showerror("Error", response_result[1])
            response = response_result[1]
            progress_frame.grid(row=0, column=0, sticky="ew")
            progress_frame.total_size = latest_release.size
            download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
            if not all(download_result):
                if download_result[1] == "Cancelled":
                    return False
                else:
                    messagebox.showerror("Requests Error", f"Failed to download file\n\n{download_result[1]}")
                    return False
            return download_path
        
        def extract_release_files(archive, progress_frame):
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            extract_folder = os.path.join(temp_path, "yuzu-ea")
            with ZipFile(archive, 'r') as zip_file:
                zip_file.extractall(extract_folder)
            progress_frame.update_extraction_progress(1)
            return extract_folder
        
        yuzu_path = os.path.join(self.settings.yuzu.install_directory,"yuzu-windows-msvc-early-access")
        temp_path = os.path.join(os.getenv("TEMP"), "Emulator Manager", "Yuzu Early Access Files")

        launcher_file = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "launcher.json")
        # Parse asset info
        
        latest_release = self.get_latest_yuzu_ea_release()
        if not all(latest_release):
            messagebox.showerror("Error", f"There was an error while fetching the latest version of Yuzu EA from GitHub:\n\n{latest_release[1]}")
            self.gui.configure_early_access_buttons(state="normal")
            self.updating_ea = False
            return 
        latest_release = latest_release[1]
        contents = self.get_launcher_file_content()
        ea_info = contents['yuzu']['early_access']
        installed = ea_info["installed_version"]

        if installed != latest_release.version or (installed == latest_release.version and messagebox.askyesno("Yuzu EA", "You already have the latest version of yuzu EA installed, would you still like to install yuzu EA?")):
            install_yuzu_ea()
      
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        self.updating_ea = False
        if start_yuzu:
            self.gui.configure_early_access_buttons(state="disabled", text="Launching...")
            Thread(target=self.start_yuzu, args=(None,True,)).start()
        else:
            self.gui.configure_early_access_buttons(state="normal")
    def delete_early_access(self):
        try:
            shutil.rmtree(os.path.join(self.settings.yuzu.install_directory, "yuzu-windows-msvc-early-access"))
            messagebox.showinfo("Success", "The installation of yuzu EA was successfully deleted!")
        except Exception as error_msg:
            messagebox.showerror("Delete Error", f"Failed to delete yuzu-ea: \n\n{error_msg}")
        self.gui.configure_early_access_buttons("normal")
            
       
    def install_firmware_handler(self):
        self.gui.configure_firmware_key_buttons("disabled")
        firmware_path = self.settings.yuzu.firmware_path if self.verify_firmware_archive() else self.download_firmware_archive()
        if not all(firmware_path):
            if firmware_path[1] != "Cancelled":
                messagebox.showerror("Download Error", firmware_path[1])
            return False
        firmware_path = firmware_path[1] if isinstance(firmware_path, tuple) else firmware_path
        result = self.install_firmware_from_archive(firmware_path)
        if result:
            messagebox.showwarning("Unexpected Files" , f"These files were skipped in the extraction process: {result}")
        messagebox.showinfo("Firmware Install", "The switch firmware files were successfully installed")
        return True 
    
    def download_firmware_archive(self):
        firmware_release = get_resources_release('https://api.github.com/repos/Viren070/Emulator-Manager-Resources/releases', "Firmware", get_headers(self.settings.app.token))
        if not all(firmware_release):
            return firmware_release
            
        firmware = firmware_release[1]
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
        key_path = self.settings.yuzu.key_path if self.verify_key_archive() else self.download_key_archive()
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
        messagebox.showinfo("Keys", "Decryption keys were successfully installed!")
        return True 
            
    def download_key_archive(self):
        key_release = get_resources_release('https://api.github.com/repos/Viren070/Emulator-Manager-Resources/releases', "Keys", get_headers(self.settings.app.token))
        if not all(key_release):
            return key_release
        
        key = key_release[1]
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
        
    def export_yuzu_data(self):
        self.gui.configure_data_buttons(state="disabled")
        mode = self.gui.yuzu_export_optionmenu.get()
        user_directory = self.settings.yuzu.user_directory
        export_directory = self.settings.yuzu.export_directory
        users_auto_import__export_directory = os.path.join(export_directory, os.getlogin())
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
        auto_import__export_directory = self.settings.yuzu.auto_import__export_directory
        export_directory = self.settings.yuzu.export_directory
        users_auto_import__export_directory = os.path.join(auto_import__export_directory, os.getlogin())
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
            result += f"Data deleted from {users_auto_import__export_directory}\n" if delete_directory(users_auto_import__export_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            save_dir = os.path.join(auto_import__export_directory, os.getlogin(), 'nand', 'user', 'save')
            result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
            if export_directory != auto_import__export_directory:
                save_dir = os.path.join(export_directory, os.getlogin(), 'nand', 'user', 'save')
                result += f"Data deleted from {save_dir}\n" if delete_directory(save_dir) else ""
        elif mode == "Exclude 'nand' & 'keys'":
            # Iterate through each of the 3 root folders and exclude 'nand' and 'keys' subfolder
            deleted = False
            folders = [user_directory, users_auto_import__export_directory, users_export_directory] if os.path.abspath(users_export_directory) != os.path.abspath(users_auto_import__export_directory) else [user_directory, users_export_directory]
            for root_folder in folders:
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
    def start_copy_thread(self, *args):
        thread=Thread(target=copy_directory_with_progress, args=args)
        thread.start()
        Thread(target=self.wait_on_thread, args=(thread,)).start()
    def wait_on_thread(self, thread):
        thread.join()
        self.gui.configure_data_buttons(state="normal")