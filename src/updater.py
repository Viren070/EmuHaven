from pathlib import Path
import shutil
import sys
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

def download_release(release):
    return download_file_with_progress(
        download_url=release["download_url"],
        download_path=Path(release["filename"]).resolve(),
        progress_handler=None
    )
    
def extract_release(archive_path):
    return extract_zip_archive_with_progress(
        zip_path=archive_path,
        extract_directory=Path(".tmp") / "update",
        progress_handler=None
    )

def finish_installation():
    # move the extracted files to the correct location
    parent_folder = Path("")
    subfolder = Path(".tmp") / "update"

    # move all files from the subfolder to the parent folde
    for item in subfolder.iterdir():
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

    subfolder.rmdir()
    
if __name__ == "__main__":
    update_check = is_update_available()
    if not update_check["status"]:
        log.error(f"Failed to check for updates: {update_check["message"]}")
        sys.exit(1)
        
    if not update_check["update_available"]:
        log.info("No updates available")
        sys.exit(0)
        
    download_result = download_release(update_check["latest_release"])
    if not download_result["status"]:
        log.error(f"Failed to download the latest release: {download_result["message"]}")
        sys.exit(1)
        
    extract_result = extract_release(download_result["download_path"])
    if not extract_result["status"]:
        log.error(f"Failed to extract the latest release: {extract_result["message"]}")
        sys.exit(1)
        
    finish_installation()
    log.info("Update successful")
    sys.exit(0)
    

    




