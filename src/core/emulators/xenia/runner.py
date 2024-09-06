import os
import shutil
import subprocess
import time
from tkinter import messagebox
from zipfile import ZipFile
from pathlib import Path

from core import constants
from core.utils.files import copy_directory_with_progress, extract_zip_archive_with_progress
from core.utils.github import get_latest_release_with_asset
from core.utils.web import download_file_with_progress

class Xenia:
    def __init__(self, gui, settings, versions):
        self.settings = settings
        self.versions = versions
        self.gui = gui
        self.running = False
        self.main_progress_frame = None
        self.data_progress_frame = None



    def get_installed_version(self, release_channel):
        return (self.versions.get_version(f"xenia_{release_channel.lower()}") or "Unknown") if ((self.settings.xenia.install_directory / release_channel.lower() / ("xenia_canary.exe" if release_channel == "canary" else "xenia.exe")).exists()) else ""

    def delete_xenia_zip(self, zip_path):
        time.sleep(2)
        os.remove(zip_path)

    def verify_xenia_zip(self, path_to_archive, release_channel):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                if ("xenia.exe" if release_channel == "Master" else "xenia_canary.exe") in archive.namelist():
                    return True
                else:
                    return False
        except Exception:
            return False

    def get_xenia_release(self):
        release_channel = self.settings.xenia.release_channel.lower()
        return get_latest_release_with_asset(
            repo_owner=constants.Xenia.GH_CANARY_RELEASE_REPO_OWNER.value if release_channel == "canary" else constants.Xenia.GH_RELEASE_REPO_OWNER.value,
            repo_name=constants.Xenia.GH_CANARY_RELEASE_REPO_NAME.value if release_channel == "canary" else constants.Xenia.GH_RELEASE_REPO_NAME.value,
            regex=constants.Xenia.GH_CANARY_RELEASE_ASSET_REGEX.value if release_channel == "canary" else constants.Xenia.GH_RELEASE_ASSET_REGEX.value,
            token=self.settings.token,
            use_commit_as_version=release_channel == "canary"
        )
    
    def download_xenia_release(self, release, progress_handler=None):
        download_path = Path(release["filename"]).resolve()
        return download_file_with_progress(
            download_url=release["download_url"],
            download_path=download_path,
            progress_handler=progress_handler,
        )

    def extract_xenia_release(self, release, progress_handler=None):
        if release.suffix != ".zip":
            return {
                    "status": False,
                    "message": "Unsupported archive type",
            }

        return self.extract_xenia_zip_archive(release, progress_handler)

    def extract_xenia_zip_archive(self, release_archive, progress_handler=None):
        return extract_zip_archive_with_progress(
            zip_path=release_archive,
            extract_directory=self.settings.xenia.install_directory / self.settings.xenia.release_channel,
            progress_handler=progress_handler
        )

    def delete_xenia(self):
        release_channel = self.settings.xenia.release_channel
        try:
            path_to_remove = self.settings.xenia.install_directory / release_channel
            shutil.rmtree(path_to_remove)
            return {
                "status": True,
                "message": f"Successfully deleted Xenia {release_channel}",
            }
            
        except OSError as e:
            return {
                "status": False,
                "message": f"Failed to delete Xenia {release_channel} due to error:\n\n{e}",
            }

    def launch_xenia(self):

        xenia_exe = self.settings.xenia.install_directory / self.settings.xenia.release_channel / ("xenia.exe" if self.settings.xenia.release_channel == "master" else "xenia_canary.exe")
        if not xenia_exe.exists():
            return {
                "run_status": False,
                "message": "Xenia executable does not exist",
            }
        args = [xenia_exe]
        try:
            run = subprocess.run(args, check=False, capture_output=True)
        except Exception as e:
            return {
                "run_status": False,
                "message": f"Failed to launch xenia due to error:\n\n{e}",
            }
        if run.returncode != 0:
            return {    
                "run_status": True,
                "error_encountered": True,
                "message": run.stderr.decode("utf-8")
            }
        return {
            "run_status": True,
            "error_encountered": False,
            "message": "Dolphin successfully launched and exited with no errors"
        }

    def export_xenia_data(self, mode, directory_to_export_to, folders_to_export=None):
        user_directory = self.settings.xenia.user_directory

        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No xenia data on local drive found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Xenia Data", self.data_progress_frame)
        elif mode == "Custom":
            if not folders_to_export:
                messagebox.showerror("Missing Folder", "No folders were selected to export")
                return
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Xenia Data", self.data_progress_frame, include=folders_to_export)

    def import_xenia_data(self, mode, directory_to_import_from, folders_to_import=None):
        user_directory = self.settings.xenia.user_directory

        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No xenia data associated with your username was found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All xenia Data", self.data_progress_frame)
        elif mode == "Custom":
            if not folders_to_import:
                messagebox.showerror("Missing Folder", "No folders were selected to import")
                return
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All xenia Data", self.data_progress_frame, include=folders_to_import)

    def delete_xenia_data(self, mode, folders_to_delete=None):
        result = ""
        user_directory = self.settings.xenia.user_directory

        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except Exception as error:
                    messagebox.showerror("Delete Xenia Data", f"Unable to delete \n{directory}\ndue to error:\n\n{error}")
                    return False
            return False
        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
        elif mode == "Custom":
            deleted = False
            for folder in folders_to_delete:
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
