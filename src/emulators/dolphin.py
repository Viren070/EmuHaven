import os
import shutil
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile

from gui.progress_frame import ProgressFrame


class Dolphin:
    def __init__(self):
        self.name = "Dolphin"
        self.version = "5.0-19870"
    def start(self):
        print(f"starting {self.name} with version {self.version}")
        
        
    def install_dolphin_wrapper(self):
        self.validate_optional_paths()
        if self.check_dolphin_installation() and not messagebox.askyesno("Confirmation", "Dolphin seems to already be installed, install anyways?"):
            return 
        if not self.dolphin_installer_available:
            messagebox.showerror("Error", "The path to the Dolphin ZIP has not been set or is invalid, please check the settings")
            return
        Thread(target=self.extract_dolphin_install).start()
        
   
    def extract_dolphin_install(self): 
        self.dolphin_install_dolphin_button.configure(state="disabled")
        self.dolphin_delete_dolphin_button.configure(state="disabled")
        self.dolphin_launch_dolphin_button.configure(state="disabled")
        dolphin_install_frame = ProgressFrame(self.dolphin_log_frame, f"Extracting {os.path.basename(self.dolphin_settings_dolphin_zip_directory_variable.get())}", self)
        dolphin_install_frame.skip_to_installation()
        dolphin_install_frame.grid(row=0, column=0, sticky="nsew")
        with ZipFile(self.dolphin_settings_dolphin_zip_directory_variable.get(), 'r') as archive:
            total_files = len(archive.namelist())
            extracted_files = 0
            
            for file in archive.namelist():
                archive.extract(file, self.dolphin_settings_install_directory_variable.get())
                extracted_files += 1
                # Calculate and display progress
                dolphin_install_frame.update_extraction_progress(extracted_files / total_files) 
        messagebox.showinfo("Done", f"Installed Dolphin to {self.dolphin_settings_install_directory_variable.get()}")
        dolphin_install_frame.destroy()
        self.dolphin_install_dolphin_button.configure(state="normal")
        self.dolphin_delete_dolphin_button.configure(state="normal")
        self.dolphin_launch_dolphin_button.configure(state="normal")
        self.check_dolphin_installation()
    
    def delete_dolphin_button_event(self):
        if self.dolphin_is_running:
            messagebox.showerror("Error", "Please close Dolphin before trying to delete it. If dolphin is not open, try restarting the application")
            return
        if messagebox.askyesno("Confirmation", "Are you sure you wish to delete the Dolphin Installation. This will not delete your user data."):
            self.dolphin_delete_dolphin_button.configure(state="disabled", text="Deleting...")
            Thread(target=self.delete_dolphin).start()
        
    def delete_dolphin(self):
        try:
            shutil.rmtree(self.dolphin_settings_install_directory_variable.get())
            self.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
        except FileNotFoundError as error:
            messagebox.showinfo("Dolphin", "Installation of dolphin not found")
            self.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            return
        except Exception as e:
            messagebox.showerror("Error", e)
            self.dolphin_delete_dolphin_button.configure(state="normal", text="Delete")
            return
        messagebox.showinfo("Success", "The Dolphin installation was successfully was removed")
        
    def start_dolphin_wrapper(self):
        self.validate_optional_paths()
        if self.check_dolphin_installation():
            self.dolphin_is_running = True
            self.dolphin_launch_dolphin_button.configure(state="disabled", text="Launching...  ")
            self.dolphin_install_dolphin_button.configure(state="disabled")
            Thread(target=self.start_dolphin).start()
        else:
            messagebox.showerror("Error","A dolphin installation was not found. Please press Install Dolphin below to begin.")
    def start_dolphin(self):
        if self.dolphin_global_data.get() == "1" and os.path.exists(os.path.join(self.dolphin_settings_global_save_directory_variable.get(), os.getlogin())):
            try:
                self.copy_directory_with_progress((os.path.join(self.dolphin_settings_global_save_directory_variable.get(), os.getlogin())), self.dolphin_settings_user_directory_variable.get(), "Loading Dolphin Data", self.dolphin_log_frame)
            except Exception as error:
                for widget in self.dolphin_log_frame.winfo_children():
                        widget.destroy()
                if not messagebox.askyesno("Error", f"Unable to load your data, would you like to continue\n\n Full Error: {error}"):
                    self.dolphin_launch_dolphin_button.configure(state="normal", text="Launch Dolphin  ")
                    self.dolphin_install_dolphin_button.configure(state="normal")
                    return 
        
        self.dolphin_launch_dolphin_button.configure(state="disabled", text="Launched!  ")
        try:
            run([os.path.join(self.dolphin_settings_install_directory_variable.get(),'Dolphin.exe')], capture_output = True)
        except Exception as error_msg:
            messagebox.showerror("Error", f"Error when running Dolphin: \n{error_msg}")
        self.dolphin_is_running = False
        if self.dolphin_global_data.get() == "1":
            self.dolphin_launch_dolphin_button.configure(state="disabled", text="Launch Dolphin  ")
            self.copy_directory_with_progress(self.dolphin_settings_user_directory_variable.get(), (os.path.join(self.dolphin_settings_global_save_directory_variable.get(), os.getlogin())), "Saving Dolphin Data", self.dolphin_log_frame)
        self.dolphin_launch_dolphin_button.configure(state="normal", text="Launch Dolphin  ")
        self.dolphin_install_dolphin_button.configure(state="normal")
    def check_dolphin_installation(self):
        default_dolphin_location = os.path.join(self.dolphin_settings_install_directory_variable.get(),'Dolphin.exe')
        if os.path.exists(default_dolphin_location):
            self.dolphin_installed = True
            return True
        else:
            self.dolphin_installed = False
            return False
    
    def export_dolphin_data(self):
        mode = self.dolphin_export_optionmenu.get()
        user_directory = self.dolphin_settings_user_directory_variable.get()
        export_directory = self.dolphin_settings_export_directory_variable.get()
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No dolphin data on local drive found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            self.start_copy_thread(user_directory, users_export_directory, "Exporting All Dolphin Data", self.dolphin_data_log)
    def import_dolphin_data(self):
        mode = self.dolphin_export_optionmenu.get()
        user_directory = self.dolphin_settings_user_directory_variable.get()
        export_directory = self.dolphin_settings_export_directory_variable.get()
        users_export_directory = os.path.join(export_directory, os.getlogin())
        
        if not os.path.exists(users_export_directory):
            messagebox.showerror("Missing Folder", "No dolphin data associated with your username was found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            self.start_copy_thread(users_export_directory, user_directory, "Importing All Dolphin Data", self.dolphin_data_log)
    def delete_dolphin_data(self):
        if not messagebox.askyesno("Confirmation", "This will delete the data from Dolphin's directory and from the global saves directory. This action cannot be undone, are you sure you wish to continue?"):
            return
        mode = self.dolphin_delete_optionmenu.get()
        result = ""
        user_directory = self.dolphin_settings_user_directory_variable.get()
        global_save_directory = self.dolphin_settings_global_save_directory_variable.get()
        export_directory = self.dolphin_settings_export_directory_variable.get()
        users_global_save_directory = os.path.join(global_save_directory, os.getlogin())
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
            result += f"Data deleted from {users_global_save_directory}\n" if delete_directory(users_global_save_directory) else ""
            result += f"Data deleted from {users_export_directory}\n" if delete_directory(users_export_directory) else ""
            
        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")