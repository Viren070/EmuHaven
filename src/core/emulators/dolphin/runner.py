import os
import re
import shutil
import subprocess
import time
import platform
from zipfile import ZipFile
from pathlib import Path
import py7zr

from core import constants
from core.utils.web import download_file_with_progress, get_all_files_from_page
from core.utils.files import copy_directory_with_progress, extract_zip_archive_with_progress
from core.utils.progress_handler import ProgressHandler


class Dolphin:
    """
    This runner class is for Dolphin. 
    It handles downloading and extracting Dolphin releases, launching Dolphin, and deleting Dolphin.
    It also has methods for exporting, importing, and deleting Dolphin data.
    
    Available methods:
    - get_dolphin_release(release_channel)
    - download_release(release, progress_handler)
    - extract_release(release, progress_handler)
    - delete_dolphin()
    - launch_dolphin()
    - export_dolphin_data(mode, directory_to_export_to, folders_to_export=None)
    - import_dolphin_data(mode, directory_to_import_from, folders_to_import=None)
    - delete_dolphin_data(mode, folders_to_delete=None)
    """
    def __init__(self, settings, versions):
        self.settings = settings
        self.versions = versions
        
        self.running = False

    def get_installed_version(self):
        return (self.versions.get_version("dolphin") or "Unknown") if (self.settings.dolphin.install_directory / "Dolphin.exe").exists() else ""

    def _verify_dolphin_archive(self, path_to_archive):
        if path_to_archive.endswith(".7z"):  # don't know how else to check if its valid for 7z
            return True
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                return 'Dolphin.exe' in archive.namelist()
        except Exception:
            return False

    def _determine_release_regex(self):
        machine = platform.machine()
        system = platform.system()
        match system:
            case "Windows":
                match machine:
                    case "AMD64" | "x86_64":
                        return constants.Dolphin.RELEASE_WINDOWS_X64_REGEX.value if self.settings.dolphin.release_channel == "release" else constants.Dolphin.DEVELOPMENT_WINDOWS_X64_REGEX.value
                    case "ARM64" | "aarch64":
                        return constants.Dolphin.RELEASE_WINDOWS_ARM64_REGEX.value if self.settings.dolphin.release_channel == "release" else constants.Dolphin.DEVELOPMENT_WINDOWS_ARM64_REGEX.value
                    case _:
                        raise ValueError("Unsupported architecture")
            case _:
                raise ValueError("Unsupported system")

    def get_dolphin_release(self):
        release_download_url_mapping = {
            "development": "master",
            "release": "releases"
        }
        download_page = constants.Dolphin.RELEASE_LIST_URL.value.format(
            release_download_url_mapping[self.settings.dolphin.release_channel]
        )
        
        files_result = get_all_files_from_page(download_page, file_ext=".7z")
        
        if not files_result["status"]:
            return files_result

        releases = files_result["files"]
        # determine file regex
        release_regex = self._determine_release_regex()
        # find the release
        for release in releases:
            filename = release.split("/")[-1]
            if re.match(release_regex, filename):
                version = re.search(r"\d+(-\d+)?", filename).group()
                release = {
                    "download_url": release,
                    "filename": filename,
                    "version": version,
                }
                return {
                    "status": True,
                    "message": "Release found",
                    "release": release
                }
        return {"status": False, "message": "Unable to find a release for your system"}

    def download_release(self, release, progress_handler=ProgressHandler()):
        download_path = Path(release["filename"]).resolve()
        return download_file_with_progress(
            download_url=release["download_url"],
            download_path=download_path,
            progress_handler=progress_handler,
        )
        
    def extract_release(self, release: Path, progress_handler=ProgressHandler()):
        match release.suffix:
            case ".zip":
                if not self._verify_dolphin_archive(release):
                    return {
                        "status": False,
                        "message": "Invalid archive",
                        "extracted_files": []
                    }
                return self._extract_zip_archive(release, progress_handler)
            case ".7z":
                return self._extract_7z_archive(release, progress_handler)
            case _:
                return {
                    "status": False,
                    "message": "Unsupported archive type",
                    "extracted_files": []
                }


    def _extract_7z_archive(self, release_archive, progress_handler):

        try:
            # check if the installation directory exists and has files
            if self.settings.dolphin.install_directory.exists() and self.settings.dolphin.install_directory.iterdir():
                # delete old installation 
                # check for portable mode and temporarily move the user directory
                pass
            self.settings.dolphin.install_directory.mkdir(exist_ok=True, parents=True)
            
            
            with py7zr.SevenZipFile(release_archive, mode="r") as archive:
                archive.extractall(path=self.settings.dolphin.install_directory)
            parent_folder = self.settings.dolphin.install_directory
            subfolder = self.settings.dolphin.install_directory / "Dolphin-x64"

            contents = os.listdir(subfolder)
            for item in contents:
                item_path = subfolder / item
                destination_path = parent_folder / item
                shutil.move(item_path, destination_path)
                
            os.rmdir(subfolder)
    
            extracted_files = os.listdir(self.settings.dolphin.install_directory)
            progress_handler.report_progress(1)
            progress_handler.report_success()
            return {
                "status": True,
                "message": "Extraction successful",
                "extracted_files": extracted_files
            }

        except Exception as error:
            # fix later. need to add more specific error handling
            # and rollback changes if necessary
            return {
                "status": False,
                "message": error,
                "extracted_files": []
            }

    def _extract_zip_archive(self, release_archive, progress_handler):
        return extract_zip_archive_with_progress(release_archive, self.settings.dolphin.install_directory, progress_handler)

    def delete_dolphin(self):
        try:
            shutil.rmtree(self.settings.dolphin.install_directory)
            return {
                "status": True,
                "message": "Dolphin deleted successfully"
            }
        except Exception as error:
            return {
                "status": False,
                "message": error
            }

    def launch_dolphin(self):
        dolphin_exe = self.settings.dolphin.install_directory / "Dolphin.exe" 
        if not dolphin_exe.exists():
            return {
                "run_status": False,
                "message": "Dolphin executable not found"
            }
        
        args = [dolphin_exe]
        run = subprocess.run(args, check=False, capture_output=True)
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

    """
    def export_dolphin_data(self, mode, directory_to_export_to, folders_to_export=None):
       

        if not user_directory.:
            messagebox.showerror("Missing Folder", "No dolphin data on local drive found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Dolphin Data", self.data_progress_frame)
        elif mode == "Custom":
            if not folders_to_export:
                messagebox.showerror("Missing Folder", "No folders were selected to export")
                return
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Dolphin Data", self.data_progress_frame, include=folders_to_export)

    def import_dolphin_data(self, mode, directory_to_import_from, folders_to_import=None):
        user_directory = self.settings.dolphin.user_directory

        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No dolphin data associated with your username was found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All Dolphin Data", self.data_progress_frame)
        elif mode == "Custom":
            if not folders_to_import:
                messagebox.showerror("Missing Folder", "No folders were selected to import")
                return
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All Dolphin Data", self.data_progress_frame, include=folders_to_import)

    def delete_dolphin_data(self, mode, folders_to_delete=None):
        result = ""
        user_directory = self.settings.dolphin.user_directory

        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except Exception as error:
                    messagebox.showerror("Delete Dolphin Data", f"Unable to delete \n{directory}\ndue to error:\n\n{error}")
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
    """