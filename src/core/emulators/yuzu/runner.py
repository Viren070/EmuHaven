import platform
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

from core import constants
from core.emulators.switch_emulator import SwitchEmulator
from core.utils.files import (copy_directory_with_progress,
                              extract_zip_archive_with_progress)
from core.utils.logger import Logger


class Yuzu(SwitchEmulator):
    def __init__(self, settings, versions):
        super().__init__(emulator="yuzu", emulator_settings=settings.yuzu, versions=versions, firmware_path="nand/system/Contents/registered", key_path="keys")
        self.settings = settings
        self.metadata = versions
        self.logger = Logger(__name__).get_logger()
        self.main_progress_frame = None
        self.data_progress_frame = None
        self.updating_ea = False
        self.installing_firmware_or_keys = False
        self.running = False

    def verify_yuzu_zip(self, path_to_archive, release_type):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                return bool((release_type == "mainline" and 'yuzu-windows-msvc/yuzu.exe' in archive.namelist()) or (release_type == "early_access" and "yuzu-windows-msvc-early-access/yuzu.exe" in archive.namelist()))
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
        if not self.verify_yuzu_zip(archive_path, self.settings.yuzu.release_channel):
            progress_handler.cancel()
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

    def export_yuzu_data(self, export_directory, folders=None, progress_handler=None, save_folder=False):

        user_directory = self.get_user_directory()
        if save_folder:
            user_directory = user_directory / "bis" / "user" / "save"
            export_directory = export_directory / "bis" / "user" / "save"
        if not user_directory.exists():
            progress_handler.report_error("FileNotFoundError")
            return {
                "status": False,
                "message": f"No yuzu data was found. Nothing to export.\n\nPortable: {"True" if self.settings.yuzu.portable_mode else "False"}\nUser Directory:{user_directory}"
            }

        return copy_directory_with_progress(
            source_dir=user_directory,
            target_dir=export_directory,
            progress_handler=progress_handler,
            include=folders
        )

    def import_yuzu_data(self, import_directory, folders=None, progress_handler=None, save_folder=False):
        user_directory = self.get_user_directory()
        if not user_directory.exists():
            return {
                "status": False,
                "message": f"No Yuzu data was found. Nothing to import.\n\nPortable: {"True" if self.settings.yuzu.portable_mode else "False"}\nUser Directory:{user_directory}"
            }
        if save_folder:
            import_directory = import_directory / "nand" / "user" / "save"
            user_directory = user_directory / "nand" / "user" / "save"
            
        return copy_directory_with_progress(
            source_dir=import_directory,
            target_dir=user_directory,
            progress_handler=progress_handler,
            include=folders
        )

    def delete_yuzu_data(self, folders_to_delete=None, progress_handler=None):
        user_directory = self.get_user_directory()

        if folders_to_delete is None:
            folders_to_delete = constants.Yuzu.USER_FOLDERS.value

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
            "message": "Yuzu data deleted successfully"
        }
