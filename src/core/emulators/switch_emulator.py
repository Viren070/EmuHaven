import os
import re
import shutil
from zipfile import ZipFile
from packaging import version
from core import constants
from core.utils.github import get_all_releases, get_file_list
from core.utils.progress_handler import ProgressHandler
from core.utils.web import download_file_with_progress


class SwitchEmulator:
    def __init__(self, emulator, emulator_settings, firmware_path, key_path):
        """_summary_

        Args:
            emulator (str): switch emulator to use
            settings (Settings): settings object
            firmware_path (str): relative path to the firmware directory
            key_path (str): relative path to the key directory
        """
        self.emulator = emulator
        self.emulator_settings = emulator_settings
        self.firmware_path = firmware_path
        self.key_path = key_path

    def get_user_directory(self):
        return

    def check_current_firmware(self):
        """Check if the current firmware is present in the firmware directory
        Returns:
            bool: True if the firmware is present, False otherwise
        """
        firmware_directory = self.get_user_directory() / self.firmware_path
        if firmware_directory.is_dir() and any(firmware_directory.iterdir()):
            return True
        return False

    def check_current_keys(self):
        """Check if the current keys are present in the key directory

        Returns:
            dict: A dictionary containing the status of the prod.keys and title.keys files 
        """
        key_directory = self.get_user_directory() / self.key_path
        prod_key = key_directory / "prod.keys"
        title_key = key_directory / "title.keys"
        return {"prod.keys": prod_key.exists(), "title.keys": title_key.exists()}

    def verify_firmware_archive(self, path_to_archive):
        """Verify if the given archive is a valid firmware archive

        Args:
            path_to_archive (str): The path to the archive to verify

        Returns:
            bool: True if the archive is a valid firmware archive, False otherwise
        """
        archive = path_to_archive
        if not os.path.exists(archive):
            return False
        if not archive.endswith(".zip"):
            return False
        with ZipFile(archive, 'r') as r_archive:
            for filename in r_archive.namelist():
                if not filename.endswith(".nca"):
                    return False
        return True

    def verify_keys(self, path_to_file, check_all=False):
        if not path_to_file.exists() or not path_to_file.is_file():
            return False
        if path_to_file.name in ["title.keys", "prod.keys"]:
            return True
        if not path_to_file.endswith(".zip"):
            return False
        with ZipFile(path_to_file, 'r') as archive:
            title_found = False
            prod_found = False
            for filename in archive.namelist():
                if filename == "title.keys":
                    title_found = True
                elif filename == "prod.keys":
                    prod_found = True
                    if not check_all:
                        return True
            return {"title.keys": title_found, "prod.keys": prod_found}


    def download_firmware_release(self, release, progress_handler=None):
        return download_file_with_progress(
            download_url=release["download_url"],
            download_path=release["filename"],
            progress_handler=progress_handler,
        )

    def download_keys_release(self, release, progress_handler=None):
        return download_file_with_progress(
            download_url=release["download_url"],
            download_path=release["filename"],
            progress_handler=progress_handler,
        )

    def install_firmware_from_archive(self, firmware_source, progress_handler=None):
        if progress_handler is None:
            progress_handler = ProgressHandler()
        firmware_directory = self.get_user_directory() / self.firmware_path
        if firmware_directory.exists():
            shutil.rmtree(firmware_directory)
        firmware_directory.mkdir(parents=True, exist_ok=True)
        extracted_files = []
        try:
            with ZipFile(open(firmware_source, "rb"), 'r') as archive:
                # progress_handler.update_total(len(archive.namelist()))
                for entry in archive.infolist():
                    if not (entry.filename.endswith(".nca") or entry.filename.endswith(".nca/00")):
                        continue
                    path_components = entry.filename.replace(".cnmt", "").split("/")
                    nca_id = path_components[-1]
                    if nca_id == "00":
                        nca_id = path_components[-2]
                    if ".nca" not in nca_id:
                        # progress_handler.update_total(total - 1)
                        continue
                    new_path = firmware_directory / nca_id
                    if self.emulator == "ryujinx":
                        new_path.mkdir(exist_ok=True)
                        with open((new_path / "00"), "wb") as f:
                            f.write(archive.read(entry))
                    elif self.emulator == "yuzu":
                        firmware_directory.mkdir(exist_ok=True)
                        with open(new_path, "wb") as f:
                            f.write(archive.read(entry))
                    extracted_files.append(entry.filename)
                    progress_handler.report_progress(extracted_files)

        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to extract firmware archive: {error}",
            }
            
        return {
            "status": True,
            "message": "Firmware extracted successfully",
        }
       


    def install_keys_from_file(self, key_path):
        if not key_path.exists():
            return {
                "status": False,
                "message": f"Key file {key_path} does not exist",
            }
        
        target_key_folder = self.get_user_directory() / self.key_path
        try:
            target_key_folder.mkdir(parents=True, exist_ok=True)
            target_key_location = target_key_folder / key_path.name
            shutil.copy(key_path, target_key_location)
        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to copy key file: {error}",
            }
            
        return {
            "status": True,
            "message": "Key file copied successfully"
        }

    def install_keys_from_archive(self, key_archive, progress_handler=None):
        if progress_handler is None:
            progress_handler = ProgressHandler()
        extracted_files = []
        key_directory = self.get_user_directory() / self.key_path
        try:
            with ZipFile(key_archive, 'r') as zip_ref:
                # progress_handler.update_total(len(zip_ref.namelist()))
                for file_info in zip_ref.infolist():
                    extracted_file_path = key_directory / file_info.filename
                    extracted_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with zip_ref.open(file_info.filename) as source, open(extracted_file_path, 'wb') as target:
                        target.write(source.read())
                    extracted_files.append(file_info.filename)
                    progress_handler.report_progress(extracted_files)
        except Exception as error:
            return {
                "status": False,
                "message": f"Failed to extract keys archive: {error}",
            }

        return {
            "status": True,
            "message": "Keys extracted successfully",
        }
    
    @staticmethod
    def get_firmware_keys_dict(github_token=None):
        def convert_to_title(name):
            parsed_version = version.parse(name)
    
            if parsed_version.is_postrelease:
                base_version = parsed_version.base_version
                post_release = parsed_version.post
                return f"{base_version} (Rebootless Update {post_release})" if post_release != 0 else f"{base_version} (Rebootless Update)"

            return parsed_version.base_version
            
        releases = get_all_releases(
            repo_owner=constants.Switch.FIRMWARE_KEYS_GH_REPO_OWNER.value,
            repo_name=constants.Switch.FIRMWARE_KEYS_GH_REPO_NAME.value,
            token=github_token,
        )
        if not releases["status"]:
            return releases

        firmware_keys = {
            "firmware": {},
            "keys": {},
        }
        releases = releases["response"]

        for release in releases:
            if not release["assets"]:
                continue
            title = convert_to_title(release["name"])
            assets = release["assets"]
            key_release = {}
            firmware_release = {}

            for asset in assets:
                if "Alpha" in asset["name"]:
                    firmware_release = {
                        "filename": asset["name"].replace("Alpha", "Firmware"),
                        "download_url": asset["browser_download_url"],
                        "size": asset["size"],
                        "version": release["tag_name"],
                    }
                elif "Rebootless" not in asset["name"] and "Beta" in asset["name"]:
                    key_release = {
                        "filename": asset["name"].replace("Beta", "Keys"),
                        "download_url": asset["browser_download_url"],
                        "size": asset["size"],
                        "version": release["tag_name"],
                    }

            if firmware_release:
                firmware_keys["firmware"][title] = firmware_release
            if key_release and "Rebootless" not in asset["name"]:
                firmware_keys["keys"][title] = key_release

        return {
            "status": True,
            "message": "Firmware and keys retrieved successfully",
            "firmware_keys": firmware_keys,
        }
    
        
    @staticmethod
    def download_titledb(progress_handler=None):
        return download_file_with_progress(
            download_url=constants.Switch.TITLEDB_DOWNLOAD_URL.value,
            download_path=constants.Switch.TITLEDB_FILENAME.value,
            progress_handler=progress_handler,
        )
        
    @staticmethod
    def get_saves_list():
        saves = get_file_list(
            repo_owner=constants.Switch.SAVES_GH_REPO_OWNER.value,
            repo_name=constants.Switch.SAVES_GH_REPO_NAME.value,
            path=constants.Switch.SAVES_GH_REPO_PATH.value,
        )
        return [save["name"] for save in saves["response"]] if saves["status"] else saves
    
    @staticmethod
    def get_game_urls(game_name):
        return []
