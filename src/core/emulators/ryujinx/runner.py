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
    def __init__(self, gui, settings, metadata):
        super().__init__(emulator="ryujinx", emulator_settings=settings.ryujinx, firmware_path="bis/system/Contents/registered", key_path="system")
        self.settings = settings
        self.metadata = metadata
        self.gui = gui
        self.main_progress_frame = None
        self.data_progress_frame = None
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False

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


    def check_and_prompt_firmware_keys_install(self):
        # Helper function to get version
        def get_version(key):
            version_str = self.metadata.get_installed_version(key)
            return version.parse(version_str.split(" ")[0]) if version_str not in ["", None] else None

        # Helper function to ask and set task
        def ask_and_set_task(task_key, version, message):
            if messagebox.askyesno("Missing Keys", message):
                install_tasks[task_key] = version

        # Setup a dict containing tasks to be done
        install_tasks = {"keys": None, "firmware": None}

        # Get installed version of firmware and keys
        installed_firmware_version = get_version("ryujinx_firmware")
        installed_keys_version = get_version("ryujinx_keys")

        # Get latest available common version release
        latest_release = self.get_latest_common_firmware_keys_version()
        # If keys is missing, prompt to install keys
        if not self.check_current_keys()["prod.keys"]:
            ask_and_set_task("keys", str(latest_release) if installed_firmware_version is None else str(installed_firmware_version), "It seems you are missing the switch decryption keys. These keys are required to emulate games. Would you like to install them right now?")

        # If no firmware tasks yet, and no firmware is installed, and the user has not been asked to install firmware yet, prompt to install firmware
        if install_tasks.get("firmware") is None and installed_firmware_version is None and self.settings.app.ask_firmware.lower() == "true":
            ask_and_set_task("firmware", str(latest_release) if installed_keys_version is None else str(installed_keys_version), "It seems you are missing the switch firmware files. Without these files, some games may not run.\n\nWould you like to install the firmware now? If you select no, you will not be asked again")
        else:
            # If user rejects, don't ask again
            self.settings.app.ask_firmware = "False"
            self.settings.update_file()

        # If installed firmware version does not match installed keys version, prompt to install matching versions
        if installed_firmware_version != installed_keys_version:
            if messagebox.askyesno("Error", "It seems that the installed firmware and keys versions do not match. This may cause issues. \n\nWould you like to install the keys and firmware for the same version? The highest version currently installed will be used or the latest available version if that fails."):
                max_version = max([installed_firmware_version, installed_keys_version], default=None)
                install_tasks["keys"] = str(max_version) if max_version is not None else latest_release
                install_tasks["firmware"] = str(max_version) if max_version is not None else latest_release

        # If no tasks, return
        if all(task is None for task in install_tasks.values()):
            return

        # If keys task is not None, install keys
        if install_tasks.get("keys") is not None:
            # Get key release
            key_release = self.get_key_release(install_tasks["keys"])
            # if key release is None and firmware is currently installed
            if key_release is None and installed_firmware_version is not None:
                if messagebox.askyesno("Error", "Failed to find the keys for the currently installed firmware version. Would you like to install the keys and firmware for latest instead"):
                    install_tasks["keys"] = str(latest_release) if str(installed_firmware_version) != latest_release else None
                    install_tasks["firmware"] = str(latest_release) if str(installed_firmware_version) != latest_release else None
                    key_release = self.get_key_release(str(latest_release))
                    firmware_release = self.get_firmware_release(str(latest_release))
                else:
                    install_tasks["keys"] = None

        # If firmware task is not None, install firmware
        if install_tasks.get("firmware") is not None:
            firmware_release = self.get_firmware_release(install_tasks["firmware"])
            if firmware_release is None and installed_keys_version is not None:
                if messagebox.askyesno("Error", "Failed to find the firmware for the currently installed keys version. Would you like to install the keys and firmware for latest instead"):
                    install_tasks["firmware"] = str(latest_release) if str(installed_keys_version) != latest_release else None
                    install_tasks["keys"] = str(latest_release) if str(installed_keys_version) != latest_release else None
                    firmware_release = self.get_firmware_release(str(latest_release))
                    key_release = self.get_key_release(str(latest_release))
                else:
                    install_tasks["firmware"] = None

        # Install keys and firmware if tasks are set
        if install_tasks.get("keys") is not None and install_tasks.get("keys") != str(installed_keys_version):
            if key_release is None:
                messagebox.showerror("Error", "An unexpected error occurred while trying to fetch the keys release. Please try again later.")
            else:
                self.install_key_handler("release", key_release, skip_prompt=True)

        if install_tasks.get("firmware") is not None and install_tasks.get("firmware") != str(installed_firmware_version):
            if firmware_release is None:
                messagebox.showerror("Error", "An unexpected error occurred while trying to fetch the firmware release. Please try again later.")
            else:
                self.install_firmware_handler("release", firmware_release, skip_prompt=True)
    
    def get_key_release(self, version):
        firmware_keys_frame = self.gui.firmware_keys_frame
        if not firmware_keys_frame.versions_fetched():
            firmware_keys_frame.fetch_firmware_and_key_versions()
        keys_dict = firmware_keys_frame.firmware_key_version_dict.get("keys", {})
        return keys_dict.get(version, None)
            
    def get_firmware_release(self, version):
        firmware_keys_frame = self.gui.firmware_keys_frame
        if not firmware_keys_frame.versions_fetched():
            firmware_keys_frame.fetch_firmware_and_key_versions()
        firmware_dict = firmware_keys_frame.firmware_key_version_dict.get("firmware", {})
        return firmware_dict.get(version, None)
    
    def get_latest_common_firmware_keys_version(self):
        firmware_keys_frame = self.gui.firmware_keys_frame
        if not firmware_keys_frame.versions_fetched():
            firmware_keys_frame.fetch_firmware_and_key_versions()
        return firmware_keys_frame.get_latest_common_version()
        

    def install_firmware_handler(self, mode, path_or_release, skip_prompt=False):
        if not skip_prompt and self.check_current_firmware() and not messagebox.askyesno("Firmware Exists", "It seems that you already have firmware installed. Would you like to continue?"):
            return
        if mode == "release":
            release = path_or_release
            firmware_path = self.download_firmware_archive(release)
            if not all(firmware_path):
                if firmware_path[1] != "Cancelled":
                    messagebox.showerror("Download Error", firmware_path[1])
                else:
                    try:
                        os.remove(firmware_path[2])
                    except Exception as error:
                        messagebox.showwarning("Error", f"Failed to delete file after cancelling due to error below:\n\n{error}")
                return False
            firmware_path = firmware_path[1]
            version = release.version
        elif mode == "path" and not self.verify_firmware_archive(path_or_release):
            messagebox.showerror("Error", "The firmware archive you have provided is invalid")
            return
        else:
            firmware_path = path_or_release
        result = self.install_firmware_from_archive(firmware_path, self.main_progress_frame)
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
        else:
            self.metadata.update_installed_version("ryujinx_firmware", version)
        if result:
            messagebox.showwarning("Unexpected Files", f"These files were skipped in the extraction process: {result}")
        messagebox.showinfo("Firmware Install", "The switch firmware files were successfully installed")
        self.gui.fetch_versions()
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

    def install_key_handler(self, mode, path_or_release, skip_prompt=False):
        if not skip_prompt and self.check_current_keys()["prod.keys"] and not messagebox.askyesno("Keys Exist", "It seems that you already have the decryption keys installed. Would you like to continue?"):
            return
        if mode == "release":
            release = path_or_release
            key_path = self.download_key_archive(release)
            if not all(key_path):
                if key_path[1] != "Cancelled":
                    messagebox.showerror("Download Error", key_path[1])
                else:
                    try:
                        os.remove(key_path[2])
                    except Exception as error:
                        messagebox.showwarning("Error", f"Failed to delete file after cancelling due to below error:\n\n{error}")
                return False
            key_path = key_path[1]
            version = release.version

        elif not self.verify_key_archive(path_or_release):
            messagebox.showerror("Error", "The key archive or file you have provided is invalid. \nPlease ensure that it is a .zip file containing the 'prod.keys' or 'title.keys' in the root directory\nor a 'prod.keys' or 'title.keys' file.")
            return
        else:
            key_path = path_or_release

        if key_path.endswith(".keys"):
            self.install_keys_from_file(key_path)
        else:
            result = self.install_keys_from_archive(key_path, self.main_progress_frame)
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
        else:
            self.metadata.update_installed_version("ryujinx_keys", "")
        messagebox.showinfo("Keys", "Decryption keys were successfully installed!")
        self.gui.fetch_versions()
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
