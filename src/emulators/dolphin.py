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
from utils.requests_utils import get_headers, get_resources_release


class Dolphin:
    def __init__(self, gui, settings):
        self.settings = settings
        self.gui = gui
        self.running = False
        self.dolphin_is_running = False
       
        self.dolphin_download_api = 'https://api.github.com/repos/Viren070/dolphin-beta-downloads/releases/latest'
        
        
    
            
    def verify_dolphin_zip(self):
        if not os.path.exists(self.settings.dolphin.zip_path):
            return False
        if not self.settings.dolphin.zip_path.endswith(".zip"):
            return False 
        try:
            with ZipFile(self.settings.dolphin.zip_path, 'r') as archive:
                if 'Dolphin.exe' in archive.namelist():
                    return True 
                else:
                    return False
        except Exception:
            return False
                    
                
    def delete_dolphin_zip(self, zip_path):
        import time 
        time.sleep(2)
        os.remove(zip_path)
        
    

    def download_dolphin_zip(self):
        download_folder = os.getcwd()
        os.makedirs(download_folder, exist_ok=True)
        dolphin_release = get_resources_release("https://api.github.com/repos/Viren070/Emulator-Manager-Resources/releases", "Dolphin", headers=get_headers(self.settings.app.token))
        if not all(dolphin_release):
            messagebox.showerror("Dolphin Download Error", dolphin_release[1])
            return 
        dolphin = dolphin_release[1]
        progress_frame = ProgressFrame(self.gui.dolphin_log_frame, f"Dolphin {dolphin.version}")
        download_path = os.path.join(download_folder, f"Dolphin {dolphin.version}.zip")
        response = requests.get(dolphin.download_url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        
        progress_frame.grid(row=0, column=0, sticky="ew")
        progress_frame.total_size = dolphin.size
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203)
        if not all(download_result):
            self.gui.configure_action_buttons(state="normal")
            if download_result[1] != "Cancelled":
                messagebox.showerror("Requests Error", f"Failed to download file\n\n{download_result[1]}")
            if os.path.exists(download_path):
                Thread(target=self.delete_dolphin_zip, args=(download_path, )).start()
            return 
        
        try:
            self.settings.dolphin.zip_path = download_path
            self.gui.parent_frame.revert_settings()
        except Exception as error:
            messagebox.showerror("Unknown Error", error)
            self.gui.configure_action_buttons(state="normal")
            return False
        if self.verify_dolphin_zip():
            self.extract_dolphin_install()
        else:
            messagebox.showerror("Dolphin Install", "An unknown error has occured and the downloaded zip file could not be verified.")
            
           
        
        
        
    def install_dolphin_wrapper(self, skip_prompt = False):
        if not skip_prompt and self.check_dolphin_installation() and not messagebox.askyesno("Confirmation", "Dolphin seems to already be installed, install anyways?"):
            return 
        if not self.verify_dolphin_zip():
            if messagebox.askyesno("Dolphin", "Your Dolphin ZIP seems to be invalid, do you want to download it from the internet?"):
                self.gui.dolphin_install_dolphin_button.configure(state="disabled")
                self.gui.dolphin_delete_dolphin_button.configure(state="disabled")
                self.gui.dolphin_launch_dolphin_button.configure(state="disabled")
                Thread(target=self.download_dolphin_zip).start()
            return 
        Thread(target=self.extract_dolphin_install).start()
        
   
    def extract_dolphin_install(self): 
        self.gui.dolphin_install_dolphin_button.configure(state="disabled")
        self.gui.dolphin_delete_dolphin_button.configure(state="disabled")
        self.gui.dolphin_launch_dolphin_button.configure(state="disabled")
        dolphin_install_frame = ProgressFrame(self.gui.dolphin_log_frame, f"Extracting {os.path.basename(self.settings.dolphin.zip_path)}")
        dolphin_install_frame.skip_to_installation()
        dolphin_install_frame.cancel_download_button.configure(state="normal")
        dolphin_install_frame.update_status_label("Status: Extracting... ")
        dolphin_install_frame.grid(row=0, column=0, sticky="nsew")
        extracted=True
        try:
            with ZipFile(self.settings.dolphin.zip_path, 'r') as archive:
                total_files = len(archive.namelist())
                extracted_files = 0
                
                for file in archive.namelist():
                    if dolphin_install_frame.cancel_download_raised:
                        extracted=False
                        break
                    archive.extract(file, self.settings.dolphin.install_directory)
                    extracted_files += 1
                    # Calculate and display progress
                    dolphin_install_frame.update_extraction_progress(extracted_files / total_files) 
            if extracted:
                messagebox.showinfo("Done", f"Successfully extracted Dolphin to {self.settings.dolphin.install_directory}")
        except Exception as error:
            messagebox.showerror("Error", error)
            
        dolphin_install_frame.destroy()
        self.gui.dolphin_install_dolphin_button.configure(state="normal")
        self.gui.dolphin_delete_dolphin_button.configure(state="normal")
        self.gui.dolphin_launch_dolphin_button.configure(state="normal")
   
    
    def delete_dolphin_button_event(self):
        if self.dolphin_is_running:
            messagebox.showerror("Error", "Please close Dolphin before trying to delete it. If dolphin is not open, try restarting the application")
            return
        if messagebox.askyesno("Confirmation", "Are you sure you wish to delete the Dolphin Installation. This will not delete your user data."):
            self.gui.dolphin_delete_dolphin_button.configure(state="disabled", text="Deleting...")
            Thread(target=self.delete_dolphin).start()
        
    def delete_dolphin(self):
        try:
            shutil.rmtree(self.settings.dolphin.install_directory)
            self.gui.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            messagebox.showinfo("Success", "The Dolphin installation was successfully was removed")
        except FileNotFoundError as error:
            messagebox.showinfo("Dolphin", "Installation of dolphin not found")
            self.gui.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            return
        except Exception as e:
            messagebox.showerror("Error", e)
            self.gui.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            return
       
        
    def start_dolphin_wrapper(self):
        if self.check_dolphin_installation():
            self.dolphin_is_running = True
            self.gui.dolphin_launch_dolphin_button.configure(state="disabled", text="Launching...  ")
            self.gui.dolphin_install_dolphin_button.configure(state="disabled")
            Thread(target=self.start_dolphin).start()
        else:
            messagebox.showerror("Error","A dolphin installation was not found. Please press Install Dolphin below to begin.")
    def start_dolphin(self):
        self.running = True
        if self.gui.dolphin_global_data.get() == "True" and os.path.exists(os.path.join(self.settings.dolphin.auto_import__export_directory, os.getlogin())):
            try:
                copy_directory_with_progress((os.path.join(self.settings.dolphin.auto_import__export_directory, os.getlogin())), self.settings.dolphin.user_directory, "Loading Dolphin Data", self.gui.dolphin_log_frame)
            except Exception as error:
                for widget in self.gui.dolphin_log_frame.winfo_children():
                        widget.destroy()
                if not messagebox.askyesno("Error", f"Unable to load your data, would you like to continue\n\n Full Error: {error}"):
                    self.gui.dolphin_launch_dolphin_button.configure(state="normal", text="Launch Dolphin  ")
                    self.gui.dolphin_install_dolphin_button.configure(state="normal")
                    self.running = False
                    return 
        
        self.gui.dolphin_launch_dolphin_button.configure(state="disabled", text="Launched!  ")
        try:
            subprocess.run([os.path.join(self.settings.dolphin.install_directory,'Dolphin.exe')], capture_output = True)
        except Exception as error_msg:
            messagebox.showerror("Error", f"Error when running Dolphin: \n{error_msg}")
        self.dolphin_is_running = False
        if self.gui.dolphin_global_data.get() == "True":
            self.gui.dolphin_launch_dolphin_button.configure(state="disabled", text="Launch Dolphin  ")
            copy_directory_with_progress(self.settings.dolphin.user_directory, (os.path.join(self.settings.dolphin.auto_import__export_directory, os.getlogin())), "Saving Dolphin Data", self.gui.dolphin_log_frame)
        self.gui.dolphin_launch_dolphin_button.configure(state="normal", text="Launch Dolphin  ")
        self.gui.dolphin_install_dolphin_button.configure(state="normal")
        self.running = False
    
    
    def export_dolphin_data(self):
        self.gui.configure_data_buttons(state="disabled")
        mode = self.gui.dolphin_export_optionmenu.get()
        user_directory = self.settings.dolphin.user_directory
        export_directory = self.settings.dolphin.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No dolphin data on local drive found")
            self.gui.configure_data_buttons(state="normal")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            self.start_copy_thread(user_directory, users_export_directory, "Exporting All Dolphin Data", self.gui.dolphin_data_log)
    def import_dolphin_data(self):
        self.gui.configure_data_buttons(state="disabled")
        mode = self.gui.dolphin_export_optionmenu.get()
        user_directory = self.settings.dolphin.user_directory
        export_directory = self.settings.dolphin.export_directory
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No dolphin data associated with your username was found")
            self.gui.configure_data_buttons(state="normal")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            self.start_copy_thread(users_export_directory, user_directory, "Importing All Dolphin Data", self.gui.dolphin_data_log)
    def delete_dolphin_data(self):
        self.gui.configure_data_buttons(state="disabled")
        if not messagebox.askyesno("Confirmation", "This will delete the data from Dolphin's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
            self.gui.configure_data_buttons(state="normal")
            return
        mode = self.gui.dolphin_delete_optionmenu.get()
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
        self.gui.configure_data_buttons(state="normal")
    def start_copy_thread(self, *args):
        thread=Thread(target=copy_directory_with_progress, args=args)
        thread.start()
        Thread(target=self.wait_on_thread, args=(thread,)).start()
    def wait_on_thread(self, thread):
        thread.join()
        self.gui.configure_data_buttons(state="normal")
        
    def check_dolphin_installation(self):
        default_dolphin_location = os.path.join(self.settings.dolphin.install_directory,'Dolphin.exe')
        if os.path.exists(default_dolphin_location):
            self.dolphin_installed = True
            return True
        else:
            self.dolphin_installed = False
            return False
        
    
    