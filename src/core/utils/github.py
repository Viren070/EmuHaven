from core.constants import GitHub, Requests, GitHubOAuth
from core.utils import web
from core.utils.logger import Logger

logger = Logger(__name__).get_logger()


def get_headers(token=None):
    logger.debug("Getting headers with token: %s", token)
    headers = Requests.GH_HEADERS.value.copy()
    if token:
        headers["Authorization"] = headers["Authorization"].format(GH_TOKEN=token)
    else:
        headers.pop("Authorization")
    logger.debug("Headers: %s", headers)
    return headers


def get_all_releases(repo_owner, repo_name, token=None):
    logger.debug("Getting all releases for %s/%s", repo_owner, repo_name)
    response = web.get(GitHub.API_RELEASES.value.format(owner=repo_owner, repo=repo_name), headers=get_headers(token)) 
    if response["status"]:
        response["response"] = response["response"].json()
        return response
    logger.error("Failed to get all releases: %s", response)
    return response


def get_latest_release(repo_owner, repo_name, token=None):
    logger.debug("Getting latest release for %s/%s", repo_owner, repo_name)
    response = web.get(GitHub.API_LATEST_RELEASE.value.format(owner=repo_owner, repo=repo_name), headers=get_headers(token))
    if response["status"]:
        response["response"] = response["response"].json()
        return response
    logger.error("Failed to get latest release: %s", response)
    return response


def find_asset_with_regex(assets, regex):
    for asset in assets:
        if regex.match(asset["name"]):
            return {"status": True, "message": "Regex matched", "asset": asset}
    return {"status": False, "message": "No asset found"}


def get_latest_release_with_asset(repo_owner, repo_name, regex, token=None):
    """
    Get the version, size, download URL and filename for the asset that matches
    the given regex for the latest release of the GitHub repository with the given owner and name.
    
    Args:
        repo_owner (str): The owner/organisation of the repository
        repo_name (str): The name of the repository
        regex (str): The regex to match the asset name
        token (str, optional): The GitHub token to use for the request. Defaults to None.

    Returns:
       dict: Get a dictionary containing
       
            - status: True if successful, False otherwise
            - message: A message describing the status
            - version: The version of the release
            - size: The size of the asset
            - download_url: The download url of the asset
            - filename: The name of the asset
            - 
                
    """
    release = {
        "status": False,
        "message": None,
        "version": None,
        "size": None,
        "download_url": None,
        "filename": None,
    }
    latest_release = get_latest_release(repo_owner, repo_name, token)
    if not latest_release["status"]:
        release["message"] = latest_release["message"]
        return release
    version = latest_release["response"].get("tag_name")
    assets = latest_release["response"].get("assets")
    if any(value is None for value in [version, assets]):
        release["message"] = "Failed to get the version or assets for the latest release"
        return release
    asset = find_asset_with_regex(assets, regex)
    if not asset["status"]:
        release["message"] = "Failed to find the asset with the given regex"
        return release
    asset = asset["asset"]
    release = {
        "status": True,
        "message": "Successfully retrieved the metadata for the asset",
        "version": version,
        "size": asset.get("size"),
        "download_url": asset.get("browser_download_url"),
        "filename": asset.get("name"),
        
    }
    return release


def get_rate_limit_status(token):
    headers = get_headers(token)
    response = web.get(GitHub.API_RATE_LIMIT.value, headers=headers)
    if response["status"]:
        data = response["response"].json()
        return {
            "status": True,
            "message": "Rate limit status retrieved",
            "requests_remaining": data["resources"]["core"]["remaining"],
            "reset_time": data["resources"]["core"]["reset"],
        }
    else:
        return {
            "status": False,
            "message": f"Failed to get rate limit status: {response.status_code} - {response.text}",
        }


def request_token(device_code):
    data = {
        "client_id": GitHubOAuth.GH_CLIENT_ID.value,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    headers = {"Accept": "application/json"}
    return web.post(GitHubOAuth.TOKEN_REQUEST_URL.value, data=data, headers=headers)


def request_device_code():
    data = {"client_id": GitHubOAuth.GH_CLIENT_ID.value}
    headers = {"Accept": "application/json"}
    return web.post(GitHubOAuth.DEVICE_CODE_REQUEST_URL.value, data=data, headers=headers)

def is_token_valid(token):
    if not token:
        return False
    return web.get(GitHub.API_USER, headers=get_headers(token))["status"]