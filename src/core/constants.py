from enum import Enum


class App(Enum):
    NAME = "EmuVault"
    AUTHOR = "Viren070"
    VERSION = "0.14.0"
    SETTINGS_VERSION = 5
    CACHE_VERSION = 2
    GH_OWNER = "Viren070"
    GH_REPO = "Emulator-Manager"
    DISCORD = "https://discord.viren070.me"
    KOFI = "https://ko-fi.com/viren070"
    VALID_COLOUR_THEMES = ["blue", "dark-blue", "green"]
    VALID_APPEARANCE_MODES = ["dark", "light"]


class GitHubOAuth(Enum):
    GH_CLIENT_ID = "Iv1.f1a084535d67fabb"
    GH_LOGIN_URL = "https://github.com/login/"
    TOKEN_REQUEST_URL = GH_LOGIN_URL + "oauth/access_token"
    DEVICE_CODE_REQUEST_URL = GH_LOGIN_URL + "device/code"


class GitHub(Enum):
    API_URL = "https://api.github.com/"
    API_RELEASES = API_URL + "repos/{owner}/{repo}/releases"
    API_LATEST_RELEASE = API_RELEASES + "/latest"
    API_CONTENTS = API_URL + "repos/{owner}/{repo}/contents/{path}"
    API_RATE_LIMIT = API_URL + "rate_limit"
    API_USER = API_URL + "user"


class Myrient(Enum):
    BASE_URL = "https://myrient.erista.me/files/"


class Dolphin(Enum):
    RELEASE_LIST_URL = "https://dolphin-emu.org/download/list/{}/1/"
    DEVELOPMENT_WINDOWS_X64_REGEX = r"dolphin-master-\d+-\d+-x64\.7z"
    DEVELOPMENT_WINDOWS_ARM64_REGEX = r"dolphin-master-\d+-\d+-ARM64\.7z"
    RELEASE_WINDOWS_X64_REGEX = r"dolphin-\d+-x64\.7z"
    RELEASE_WINDOWS_ARM64_REGEX = r"dolphin-\d+-ARM64\.7z"
    MYRIENT_GAMECUBE_PATH = ""
    MYRIENT_WII_PATH = "Redump/Nintendo - Wii - NKit RVZ [zstd-19-128k]/"
    GAME_FILE_EXTENSIONS = [".wbfs", ".iso", ".rvz", ".gcm", ".gcz", ".ciso"]


class Xenia(Enum):
    GH_RELEASE_REPO_OWNER = "xenia-project"
    GH_RELEASE_REPO_NAME = "release-builds-windows"
    GH_RELEASE_ASSET_REGEX = r"xenia_master.zip"
    GH_CANARY_RELEASE_REPO_OWNER = "xenia-canary"
    GH_CANARY_RELEASE_REPO_NAME = "xenia-canary"
    GH_CANARY_RELEASE_ASSET_REGEX = r"xenia_canary.zip"
    MYRIENT_XBOX_360_PATH = "Redump/Microsoft - Xbox 360"
    MYRIENT_XBOX_360_DIGITAL_PATH = "No-Intro/Microsoft - Xbox 360 (Digital)/"


class Switch(Enum):
    FIRMWARE_KEYS_GH_REPO_OWNER = "NXResources"
    FIRMWARE_KEYS_GH_REPO_NAME = "NX_FK"
    SAVES_GH_REPO_OWNER = "NXResources"
    SAVES_GH_REPO_NAME = "NX_Saves"
    TITLEDB_GH_REPO_OWNER = "NXResources"
    TITLEDB_GH_REPO_NAME = "NX_TitleDB"
    GAMES_URLS = []


class Yuzu(Enum):
    GH_RELEASE_REPO_OWNER = "yuzu-emu"
    GH_RELEASE_REPO_NAME = "yuzu"
    GH_RELEASE_WINDOWS_ASSET_REGEX = r"yuzu-windows-msvc-.*\.zip"


class Ryujinx(Enum):
    GH_RELEASE_REPO_OWNER = "Ryujinx"
    GH_RELEASE_REPO_NAME = "release-channel-master"
    GH_RELEASE_WINDOWS_ASSET_REGEX = r'ryujinx-\d+\.\d+\.\d+-win_x64\.zip'


class Requests(Enum):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    DEFAULT_HEADERS = {
        "User-Agent": USER_AGENT
    }
    GH_HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "identity",
        "Accept": "application/vnd.github+json",
        "Authorization": "BEARER {GH_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
