from core.constants import Switch
from core.utils.github import get_all_releases


def get_firmware_keys_dict(github_token=None):
    releases = get_all_releases(
        repo_owner=Switch.FIRMWARE_KEYS_GITHUB_REPO_OWNER.value,
        repo_name=Switch.FIRMWARE_KEYS_GITHUB_REPO_NAME.value,
        token=github_token,
    )
    if not releases["status"]:
        return releases
    firmware_keys = {}
    releases = releases["response"].json()

    for release in releases:
        if not release["assets"]:
            continue
        version = release["name"]
        assets = release["assets"]
        key_release = {}
        firmware_release = {}

        for asset in assets:
            if "Alpha" in asset["name"]:
                firmware_release = {
                    "name": asset["name"].replace("Alpha", "Firmware"),
                    "download_url": asset["browser_download_url"],
                    "size": asset["size"],
                    "version": version,
                }
            elif "Rebootless" not in version and "Beta" in asset["name"]:
                key_release = {
                    "name": asset["name"].replace("Beta", "Keys"),
                    "download_url": asset["browser_download_url"],
                    "size": asset["size"],
                    "version": version,
                }

        if firmware_release is not None:
            firmware_keys["firmware"][version] = firmware_release
        if key_release is not None and "Rebootless" not in version:
            firmware_keys["keys"][version] = key_release

    return {
        "status": True,
        "message": "Firmware and keys retrieved successfully",
        "firmware_keys": firmware_keys,
    }
