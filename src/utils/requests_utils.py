import json
import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

DEFAULT_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
                  'Accept-Encoding': 'identity'}
class Release:
    def __init__(self) -> None:
        self.name = None
        self.download_url = None
        self.size = None 
        self.version = None
                
class File:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename
def get_headers(token=None):
    headers = DEFAULT_HEADER
    if token:
        headers["Accept"]= "application/vnd.github+json"
        headers["Authorization"] = f"BEARER {token}"
        headers["X-GitHub-Api-Version"]="2022-11-28"
        
    return headers
    
def create_get_connection(url, **kwargs):
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        return (False, error)
    return (True, response)

def get_all_releases(api_url, headers):
    response = create_get_connection(api_url, headers=headers, timeout=20)
    if not all(response): return (False, response[1])
    response = response[1]
    releases = json.loads(response.text)
    return (True, releases)

def get_assets_from_latest_release(api_url, headers):
    response = create_get_connection(api_url, headers=headers, timeout=20)
    if not all(response): return (False, response[1])
    response = response[1]
    try:
        release_info = json.loads(response.text)[0]
        assets = release_info['assets']
        return (True, assets)
    except KeyError:
        return (False, "You have most likely been rate limited by GitHub")
    
def get_release_from_assets(assets, query, wildcard=False):
    matching_assets = []
    for asset in assets:
        if wildcard:
            pattern = query.replace("{}", ".*")
            if re.match(pattern, asset["name"]) and "debugsymbols" not in asset["name"]:
                matching_assets.append(asset)
                break

        elif query in asset["name"]:
            matching_assets.append(asset)
            break
    release = Release()
    asset = matching_assets[0]
    release.download_url = asset["browser_download_url"]
    release.size = asset["size"]
    release.name = asset["name"]
    return release

    
def get_resources_release(file, headers=None):
    if headers is None:
        headers = DEFAULT_HEADER
    assets_result = get_assets_from_latest_release('https://api.github.com/repos/Viren070/Emulator-Manager-Resources/releases', headers)
    if not all(assets_result): return (False, assets_result[1])
    assets = assets_result[1]
    if file == "Dolphin":
        query="Dolphin"
    elif file == "Firmware":
        query = "Alpha"
    elif file == "Keys":
        query = "Beta"
    else:
        raise ValueError(f"Incorrect file, accepts Dolphin, Firmware or Keys but got {file}")
    
    release = get_release_from_assets(assets, query)
    return (True, release)
    
def get_file_links_from_page(url, file_ext=None, headers=DEFAULT_HEADER):

    response_result = create_get_connection(url, headers=headers, timeout=30)
    if not all(response_result):
        return response_result
    response = response_result[1]
    files = []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if (file_ext is None) or (href.endswith(file_ext) and href not in [file.url for file in files]):
            filename=re.sub('<[^>]+>', '', str(link)).replace("&amp;", "&")
            result=urlparse(href)
            if all([result.scheme, result.netloc]):
                file_url = href
            else:
                file_url = urljoin(url,href)
                result = urlparse(file_url)
                if not all([result.scheme, result.netloc]):
                    continue
            files.append(File(file_url, filename))
    return (True, files)
    
            
