import os
import platform
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

from core import constants
from core.emulators.switch_emulator import SwitchEmulator
from core.utils.files import (copy_directory_with_progress,
                              extract_zip_archive_with_progress)
from core.utils.github import get_latest_release_with_asset
from core.utils.logger import Logger
from core.utils.web import download_file_with_progress


class Ryujinx(SwitchEmulator):
    def __init__(self, settings, versions):
        super().__init__(emulator="ryujinx", emulator_settings=settings.ryujinx, versions=versions, firmware_path="bis/system/Contents/registered", key_path="system")
        self.settings = settings
        self.versions = versions
        self.logger = Logger(__name__).get_logger()


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
            download_path=Path(release["filename"]).resolve(),
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


    def export_ryujinx_data(self, export_directory, folders=None, progress_handler=None, save_folder=False):

        user_directory = self.get_user_directory()
        if save_folder:
            user_directory = user_directory / "bis" / "user" / "save"
            export_directory = export_directory / "bis" / "user" / "save"
        if not user_directory.exists():
            progress_handler.report_error("FileNotFoundError")
            return {
                "status": False,
                "message": f"No ryujinx data was found. Nothing to export.\n\nPortable: {"True" if self.settings.ryujinx.portable_mode else "False"}\nUser Directory:{user_directory}"
            }

        return copy_directory_with_progress(
            source_dir=user_directory,
            target_dir=export_directory,
            progress_handler=progress_handler,
            include=folders
        )

    def import_ryujinx_data(self, import_directory, folders=None, progress_handler=None, save_folder=False):
        user_directory = self.get_user_directory()
        if not user_directory.exists():
            return {
                "status": False,
                "message": f"No Ryujinx data was found. Nothing to import.\n\nPortable: {"True" if self.settings.ryujinx.portable_mode else "False"}\nUser Directory:{user_directory}"
            }
        if save_folder:
            import_directory = import_directory / "bis" / "user" / "save"
            user_directory = user_directory / "bis" / "user" / "save"
            
        return copy_directory_with_progress(
            source_dir=import_directory,
            target_dir=user_directory,
            progress_handler=progress_handler,
            include=folders
        )

    def delete_ryujinx_data(self, folders_to_delete=None, progress_handler=None):
        user_directory = self.get_user_directory()

        if folders_to_delete is None:
            folders_to_delete = constants.Ryujinx.USER_FOLDERS.value

        total = len(folders_to_delete)
        progress = 0
        progress_handler.set_total_units(total)
        for folder in folders_to_delete:
            if progress_handler.should_cancel():
                progress_handler.cancel()
                return {
                    "status": False,
                    "message": "Delete operation cancelled"
                }
            path = user_directory / folder
            if not path.exists():
                total -= 1
                progress_handler.set_total_units(total)
                continue

            try:
                self.logger.info("Deleting %s", path)
                shutil.rmtree(path)
                progress += 1
                progress_handler.report_progress(progress)
            except Exception as error:
                self.logger.error("Delete error: %s", error)
                progress_handler.report_error(error)
                return {
                    "status": False,
                    "message": f"Error while attempting to delete {folder}: {error}"
                }
        progress_handler.report_success()
        return {
            "status": True,
            "message": "Ryujinx data deleted successfully"
        }