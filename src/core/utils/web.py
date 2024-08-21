import requests
from bs4 import BeautifulSoup
from requests import RequestException
from urllib.parse import urlparse, urljoin, unquote

from core.utils.logger import Logger
from core.utils.progress_handler import ProgressHandler
from core import constants 

logger = Logger(__name__).get_logger()


def get(url, timeout=30, headers=constants.Requests.DEFAULT_HEADERS.value, **kwargs):
    """Create a GET request to the given URL.

    Args:
        url (str): URL to make the request to.
        headers (dict, optional): Headers to include in the request. Defaults to None.
        timeout (int, optional): The timeout for the request. Defaults to 10.

    Returns:
        dict: A dictionary with fields: status (bool) and message (str or requests.Response)
    """ 
    try:
        logger.debug("GET request to %s with the following kwargs: %s", url, kwargs)
        response = requests.get(url, timeout=timeout, headers=headers, **kwargs)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        logger.error("GET request failed: %s", error)
        return {"status": False, "message": error}
    return {"status": True, "message": "Request successful", "response": response}


def post(url, data=None, json=None, timeout=30, headers=constants.Requests.DEFAULT_HEADERS.value, **kwargs):
    """Create a POST request to the given URL.

    Args:
        url (str): URL to make the request to.
        data (dict, optional): Data to include in the request. Defaults to None.
        json (dict, optional): JSON data to include in the request. Defaults to None.
        headers (dict, optional): Headers to include in the request. Defaults to None.
        timeout (int, optional): The timeout for the request. Defaults to 10.

    Returns:
        dict: A dictionary with fields: status (bool) and message (str or requests.Response)
    """
    try:
        logger.debug("POST request to %s with the following kwargs: %s", url, kwargs)
        response = requests.post(url, data=data, json=json, timeout=timeout, headers=headers, **kwargs)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        logger.error("POST request failed: %s", error)
        return {"status": False, "message": error, "response": response}
    return {"status": True, "message": "Request successful", "response": response}


def get_all_files_from_page(url, file_ext=None, **kwargs):
    """Get all file links from a page.

    Args:
        url (str): The URL to get the files from.
        file_ext (str, optional): The file extension to filter by. Defaults to None.

    Returns:
        dict: A dictionary with fields: status (bool) and message (str) and files (list(dict of fields: url(str), filename(str)))
    """
    logger.debug("Getting all files from %s with extension: %s", url, file_ext)
    response = get(url, **kwargs)
    if not response["status"]:
        return response
    response = response["response"]
    files = []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href').replace('"', '').strip("\\")
        if (file_ext is None) or (href.endswith(file_ext) and href not in [file["url"] for file in files]):
            result = urlparse(href)
            if all([result.scheme, result.netloc]):
                file_url = href
            else:
                file_url = urljoin(url, href)
                result = urlparse(file_url)
                if not all([result.scheme, result.netloc]):
                    continue
            files.append(file_url)
    return {"status": True, "message": "Files retrieved successfully", "files": files}


def download_file_with_progress(download_url, download_path, chunk_size=1024, progress_handler=ProgressHandler(), **kwargs):
    """Download a file from the given URL using a stream with a progress handler.

    Args:
        url (str): URL to download the file from.
        download_path (str): Path to save the downloaded file to.
        progress_handler (ProgressHandler): Progress handler to update the download progress.
        headers (dict): Headers to include in the request.
        chunk_size (int): The size of the chunks to download.

    Returns:
        dict: A dictionary with fields: status (bool), message (str) and download_path (str)
    """
    logger.debug("Downloading file from %s to %s with chunk size: %s", download_url, download_path, chunk_size)
    response = get(download_url, stream=True, **kwargs)
    if not response["status"]:
        return response
    response = response["response"]
    return download_through_stream(response, download_path, chunk_size, progress_handler)


def download_through_stream(response, download_path, chunk_size, progress_handler=ProgressHandler()):
    try:
        with open(download_path, 'wb') as f:
            downloaded_bytes = 0

            for chunk in response.iter_content(chunk_size=chunk_size):
                if progress_handler.should_cancel():
                    progress_handler.cancel()
                    return {
                        "status": False,
                        "message": "The download was cancelled by the user",
                        "download_path": download_path
                    }
                f.write(chunk)
                downloaded_bytes += len(chunk)

                progress_handler.report_progress(downloaded_bytes)

            progress_handler.report_success()
    except (FileNotFoundError, RequestException, OSError) as error:
        progress_handler.report_error(error)
        download_path.unlink()
        return {
            "status": False,
            "message": error,
            "download_path": None
        }
    return {
        "status": True,
        "message": "Download successful",
        "download_path": download_path
    }

def download_file(download_url, download_path, **kwargs):
    """Download a file from the given URL to the given path.

    Args:
        download_url (str): URL to download the file from.
        download_path (str): Path to save the downloaded file to.

    Returns:
        dict: A dictionary with fields: status (bool), message (str) and download_path (str)
    """
    logger.debug("Downloading file from %s to %s", download_url, download_path)
    response = get(download_url, **kwargs)
    if not response["status"]:
        return response
    response = response["response"]
    try:
        with open(download_path, "wb") as f:
            f.write(response.content)
        return {
            "status": True,
            "message": "Download successful",
            "download_path": download_path
        }
    except RequestException as error:
        download_path.unlink()
        return {
            "status": False,
            "message": error,
            "download_path": None
        }