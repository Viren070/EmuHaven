import platform
import re
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

import py7zr

from core.config import constants
from core.logging.logger import Logger
from core.network.web import (download_file_with_progress,
                              get_all_files_from_page)
from core.utils.files import (copy_directory_with_progress,
                              extract_zip_archive_with_progress)


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
        self.logger = Logger(__name__).get_logger()
        self.running = False

    def get_user_directory(self):
        if self.settings.dolphin.portable_mode:
            return self.settings.dolphin.install_directory / "User"
        match platform.system().lower():
            case "windows":
                return Path.home() / "AppData" / "Roaming" / "Dolphin Emulator"
            case _:
                raise NotImplementedError("Unsupported system")

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

    def download_release(self, release, progress_handler=None):
        return download_file_with_progress(
            download_url=release["download_url"],
            download_path=Path(release["filename"]).resolve(),
            progress_handler=progress_handler,
        )

    def extract_release(self, release: Path, progress_handler=None):
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

        # check if the installation directory exists and has files
        if self.settings.dolphin.install_directory.exists() and self.settings.dolphin.install_directory.iterdir():
            # delete old installation
            # check for portable mode and temporarily move the user directory
            pass
        self.settings.dolphin.install_directory.mkdir(exist_ok=True, parents=True)

        try:
            with py7zr.SevenZipFile(release_archive, mode="r") as archive:
                archive.extractall(path=self.settings.dolphin.install_directory)
        except Exception as error:
            self.logger.error("Error extracting 7z archive: %s", error)
            return {
                "status": False,
                "message": "Extraction failed",
                "error": error,
                "extracted_files": []
            }

        parent_folder = self.settings.dolphin.install_directory
        subfolder = self.settings.dolphin.install_directory / "Dolphin-x64"

        # move all files from the subfolder to the parent folder
        progress_handler.set_total_units(len(list(subfolder.iterdir())))
        progress_handler.report_progress(5)
        for x, item in enumerate(subfolder.iterdir()):
            destination = parent_folder / item.name

            # If the destination exists, remove it
            if destination.exists():
                if destination.is_dir():
                    # cant use rmdir as it only works on empty directories
                    shutil.rmtree(destination)
                else:
                    destination.unlink()

            # Move the item to the parent folder
            shutil.move(str(item), str(destination))
            progress_handler.report_progress(x + 1)

        subfolder.rmdir()

        progress_handler.report_progress(1)
        progress_handler.report_success()
        return {
            "status": True,
            "message": "Extraction successful",
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

        if self.settings.dolphin.sync_user_data:
            last_used_data_path = Path(self.settings.dolphin.last_used_data_path) if self.settings.dolphin.last_used_data_path else None
            current_data_path = self.get_user_directory()

            if last_used_data_path is not None and last_used_data_path.exists() and last_used_data_path != current_data_path:
                self.logger.info("Copying user directory from %s to %s", last_used_data_path, current_data_path)
                shutil.copytree(last_used_data_path, current_data_path, dirs_exist_ok=True)

        if self.settings.dolphin.portable_mode:
            (self.settings.dolphin.install_directory / "portable.txt").touch()
        else:
            (self.settings.dolphin.install_directory / "portable.txt").unlink(missing_ok=True)

        args = [dolphin_exe]
        run = subprocess.run(args, check=False, capture_output=True)
        self.settings.dolphin.last_used_data_path = self.get_user_directory()
        self.settings.save()
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

    def export_dolphin_data(self, export_directory, folders, progress_handler=None):
        user_directory = self.get_user_directory()

        if not user_directory.exists():
            return {
                "status": False,
                "message": f"No dolphin data was found. Nothing to export.\n\nPortable: {"True" if self.settings.dolphin.portable_mode else "False"}\nUser Directory:{user_directory}"
            }

        return copy_directory_with_progress(
            source_dir=user_directory,
            target_dir=export_directory,
            progress_handler=progress_handler,
            include=folders
        )

    def import_dolphin_data(self, import_directory, folders, progress_handler=None):
        user_directory = self.get_user_directory()

        if not user_directory.exists():
            return {
                "status": False,
                "message": f"No dolphin data was found. Nothing to import.\n\nPortable: {"True" if self.settings.dolphin.portable_mode else "False"}\nUser Directory:{user_directory}"
            }

        return copy_directory_with_progress(
            source_dir=import_directory,
            target_dir=user_directory,
            progress_handler=progress_handler,
            include=folders
        )

    def delete_dolphin_data(self, folders_to_delete=None, progress_handler=None):
        user_directory = self.get_user_directory()

        if folders_to_delete is None:
            folders_to_delete = constants.Dolphin.USER_FOLDERS.value

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
            "message": "Dolphin data deleted successfully"
        }
