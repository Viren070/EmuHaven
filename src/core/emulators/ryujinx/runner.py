import json
import os
import re
import shutil
import subprocess
from tkinter import messagebox
from zipfile import ZipFile
import platform
from pathlib import Path

from packaging import version

from core.emulators.switch_emulator import SwitchEmulator
from core.utils.github import get_latest_release_with_asset
from core.utils.web import download_file_with_progress
from core.utils.files import copy_directory_with_progress, extract_zip_archive_with_progress
from core import constants



class Ryujinx(SwitchEmulator):
    def __init__(self, gui, settings, versions):
        super().__init__(emulator="ryujinx", emulator_settings=settings.ryujinx, versions=versions, firmware_path="bis/system/Contents/registered", key_path="system")
        self.settings = settings
        self.versions = versions
        self.gui = gui
        self.main_progress_frame = None
        self.data_progress_frame = None
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False

    def get_installed_version(self):
        return (self.versions.get_version("ryujinx") or "Unknown") if (self.settings.ryujinx.install_directory / "publish" / "Ryujinx.exe").exists() else ""

    def get_user_directory(self):
        if self.settings.ryujinx.portable_mode:
            return self.settings.ryujinx.install_directory / "portable"
        match platform.system().lower():
            case "windows":
                return Path.home() / "AppData" / "Roaming" / "Ryujinx"
                
    def verify_ryujinx_zip(self, path_to_archive):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                if 'publish/Ryujinx.exe' in archive.namelist():
                    return True
                else:
                    return False
        except Exception:
            return False

    def _determine_release_regex(self):
        machine = platform.machine()
        system = platform.system()
        match system:
            case "Windows":
                match machine:
                    case "AMD64" | "x86_64":
                        return constants.Ryujinx.GH_RELEASE_WINDOWS_ASSET_REGEX
                    case _:
                        raise ValueError("Unsupported architecture")
            case _:
                raise ValueError("Unsupported system")

    def get_release(self):
        return get_latest_release_with_asset(
            repo_owner=constants.Ryujinx.GH_RELEASE_REPO_OWNER.value,
            repo_name=constants.Ryujinx.GH_RELEASE_REPO_NAME.value,
            regex=constants.Ryujinx.GH_RELEASE_WINDOWS_ASSET_REGEX.value,
            token=self.settings.token,
        )

    def download_release(self, release, progress_handler=None):
        return download_file_with_progress(
            download_url=release["download_url"],
            download_path=release["filename"],
            progress_handler=progress_handler
        )

    def extract_release(self, zip_path, progress_handler=None):
        return extract_zip_archive_with_progress(
            zip_path=zip_path,
            extract_directory=self.settings.ryujinx.install_directory,
            progress_handler=progress_handler
        )

    def delete_ryujinx(self, skip_prompt=False):
        try:
            shutil.rmtree(os.path.join(self.settings.ryujinx.install_directory, "publish"))
            return {
                "status": True,
                "message": "Ryujinx was successfully deleted",
            }
        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to delete Ryujinx due to error: {error}",
            }
            
    def launch_ryujinx(self):
        ryujinx_exe = self.settings.ryujinx.install_directory / "publish" / "Ryujinx.exe"
        
        if not ryujinx_exe.exists():
            return {
                "status": False,
                "message": "Ryujinx executable not found",
            }
        match platform.system().lower():
            case "windows":
                args = ["cmd", "/c", "start", "cmd", "/c", str(ryujinx_exe)]
            case _:
                args = [ryujinx_exe]
        
        try:
            run = subprocess.run(args, check=False, capture_output=True, shell=True)
        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to launch Ryujinx due to error: {error}",
            }
        if run.returncode != 0:
            return {    
                "status": True,
                "error_encountered": True,
                "message": f"The process exited with a non zero exit code:\n\n{run.stderr.decode("utf-8")}"
            }
        return {
            "status": True,
            "error_encountered": False,
            "message": "Ryujinx successfully launched and exited with no errors"
        }


    def export_ryujinx_data(self, mode, directory_to_export_to, folders=None):
        user_directory = self.settings.ryujinx.user_directory
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No Ryujinx data on local drive found")
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Ryujinx Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'bis', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(directory_to_export_to, 'bis', 'user', 'save'), "Exporting Ryujinx Save Data", self.data_progress_frame)
        elif mode == "Custom...":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting Custom Ryujinx Data", self.data_progress_frame, include=folders)
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")

    def import_ryujinx_data(self, mode, directory_to_import_from, folders=None):
        user_directory = self.settings.ryujinx.user_directory
        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No Ryujinx data associated with your username found")
            return
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Ryujinx Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(directory_to_import_from, 'bis', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(user_directory, 'bis', 'user', 'save'), "Importing Ryujinx Save Data", self.data_progress_frame)
        elif mode == "Custom...":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Ryujinx Data", self.data_progress_frame, include=folders)
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")

    def delete_ryujinx_data(self, mode, folders=None):
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
        elif mode == "Custom...":
            deleted = False
            for folder in folders:
                folder_path = os.path.join(user_directory, folder)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    if delete_directory(folder_path):
                        deleted = True
                        result += f"Data deleted from {folder_path}\n"
                    else:
                        result += f"Deletion failed for {folder_path}\n"
            if not deleted:
                result = ""

        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")
        self.gui.configure_data_buttons(state="normal")
