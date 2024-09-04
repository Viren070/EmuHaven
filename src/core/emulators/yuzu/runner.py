import json
import os
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path
from tkinter import messagebox
from zipfile import ZipFile

from packaging import version

from core.emulators.switch_emulator import SwitchEmulator
from core.utils.files import (copy_directory_with_progress,
                              extract_zip_archive_with_progress)


class Yuzu(SwitchEmulator):
    def __init__(self, gui, settings, metadata):
        super().__init__(emulator="yuzu", emulator_settings=settings.yuzu, firmware_path="nand/system/Contents/registered", key_path="keys")
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


    def get_user_directory(self):
        
        if self.settings.yuzu.portable_mode:
            return self.settings.yuzu.install_directory / "user"
        
        match platform.system().lower():
            case "windows":
                return Path.home() / "AppData" / "Roaming" / "yuzu"
            case _:
                raise NotImplementedError("Only Windows is supported for non-portable mode")
                
    def extract_release(self, zip_path, progress_handler=None):
        return extract_zip_archive_with_progress(
            zip_path=zip_path,
            extract_directory=self.settings.yuzu.install_directory,
            progress_handler=progress_handler
        )

    def install_yuzu(self, archive_path, progress_handler=None):
        extract_directory = self.settings.yuzu.install_directory / ("yuzu-windows-msvc-early-access" if self.settings.yuzu.release_channel == "early_access" else "yuzu-windows-msvc")
        if not self.verify_yuzu_zip(archive_path, self.settings.yuzu.release_channel):
            return {
                "status": False,
                "message": "The archive is not a valid yuzu release"
            }
        return self.extract_release(archive_path, progress_handler)

    def launch_yuzu(self):
        yuzu_path = self.settings.yuzu.install_directory / ("yuzu-windows-msvc-early-access" if self.settings.yuzu.release_channel == "early_access" else "yuzu-windows-msvc") / "yuzu.exe"
        args = [yuzu_path]
        try:
            output = subprocess.run(args, check=False, capture_output=True)
        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to launch yuzu:\n\n{error}"
            }
        if output.returncode != 0:
            return {
                "status": True,
                "error_encountered": True,
                "message": f"Yuzu exited with a non-zero:\n\n{output.stderr.decode()}"
            }
        return {
            "status": True, 
            "error_encountered": False,
            "message": "Yuzu safely launched and exited"
        }

    
    def delete_yuzu(self):
        yuzu_path = self.settings.yuzu.install_directory / ("yuzu-windows-msvc-early-access" if self.settings.yuzu.release_channel == "early_access" else "yuzu-windows-msvc")
        if not yuzu_path.is_dir() or not any(yuzu_path.iterdir()):
            return {
                "status": False,
                "message": f"Could not find a yuzu installation at {yuzu_path}"
            }
        try:
            shutil.rmtree(yuzu_path)
            return {
                "status": True,
                "message": f"Successfully deleted yuzu {self.settings.yuzu.release_channel}"
            }
        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to delete yuzu {self.settings.yuzu.release_channel}:\n\n{error}"
            }

    def export_yuzu_data(self, mode, directory_to_export_to, folders=None):
        user_directory = self.settings.yuzu.user_directory
        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No yuzu data on local drive found")
            return  # Handle the case when the user directory doesn't exist.

        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Yuzu Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(user_directory, 'nand', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(directory_to_export_to, 'nand', 'user', 'save'), "Exporting Yuzu Save Data", self.data_progress_frame)
        elif mode == "Custom...":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting Custom Yuzu Data", self.data_progress_frame, include=folders)
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")

    def import_yuzu_data(self, mode, directory_to_import_from, folders=None):
        user_directory = self.settings.yuzu.user_directory
        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No yuzu data associated with your username found")
            return
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import All Yuzu Data", self.data_progress_frame)
        elif mode == "Save Data":
            save_dir = os.path.join(directory_to_import_from, 'nand', 'user', 'save')
            copy_directory_with_progress(save_dir, os.path.join(user_directory, 'nand', 'user', 'save'), "Importing Yuzu Save Data", self.data_progress_frame)
        elif mode == "Custom...":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Import Custom", self.data_progress_frame, include=folders)
        else:
            messagebox.showerror("Error", f"An unexpected error has occured, {mode} is an invalid option.")

    def delete_yuzu_data(self, mode, folders=None):
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
