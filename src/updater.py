import os
import sys
from pathlib import Path

from packaging import version

from core import constants
from core.utils import logger
from core.utils.files import extract_zip_archive_with_progress
from core.utils.github import get_latest_release_with_asset
from core.utils.web import download_file_with_progress

log = logger.Logger(__name__).get_logger()



def is_update_available():
    latest_release = get_latest_release_with_asset(
        repo_owner=constants.App.GH_OWNER.value,
        repo_name=constants.App.GH_REPO.value,
        regex=constants.App.GH_ASSET_REGEX.value
    )

    if not latest_release["status"]:
        log.error(f"Failed to get the latest release: {latest_release["message"]}")
        return {"status": False, "update_available": False, "message": "Failed to get the latest release"}
        
    current_version = version.parse(constants.App.VERSION.value)
    latest_version = version.parse(latest_release["release"]["version"])
    if current_version > latest_version:
        log.info(f"Current version {current_version} is greater than the latest version {latest_version}")
        return {"status": True, "update_available": False, "message": "Current version is greater than the latest version"}
    
    return {"status": True, "update_available": True, "latest_release": latest_release["release"]}

def download_release(release)

def update_app(release):
    

    




# download the latest release



if not download_result["status"]:
    log.error(f"Failed to download the latest release: {download_result["message"]}")
    sys.exit(1)
    
log.info(f"Downloaded the latest release to {Path(latest_release["release"]["filename"]).resolve()}")

    

if __name__ == "__main__":
    if not Path(f"{constants.App.NAME.value}.exe").exists():
        log.error(f"Failed to find {Path(f"{constants.App.NAME.value}.exe").resolve()}")
        sys.exit(1)
    
    update_result = is_update_available()
    if not update_result["status"]:
        log.error(f"Failed to check if update is available: {update_result["message"]}")
        sys.exit(1)
    
    if not update_result["update_available"]:
        log.info(f"No update available")
        sys.exit(0)
        
    latest_release = update_result["latest_release"]
    log.info(f"Update available: {latest_release["version"]}")
    
    download_result = download_file_with_progress(
        download_url=latest_release["release"]["download_url"],
        download_path=f"{latest_release["release"]["filename"]}",
        progress_handler=None
    )
    if not download_result["status"]:
        log.error(f"Failed to download the latest release: {download_result["message"]}")
        sys.exit(1)
    download_path = download_result["download_path"]
        
    log.info(f"Downloaded the latest release to {Path(download_result["download_path"]).resolve()}")
    
    extract_result = extract_zip_archive_with_progress(
        zip_path=download_path,
        extract_directory=Path(f"{constants.App.NAME.value}_update").resolve(),
        progress_handler=None
    )
    
    
    