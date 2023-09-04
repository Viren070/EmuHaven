import os 
import requests 

TOKEN_FILE = os.path.join(os.getenv("APPDATA"), "Emulator Manager", ".token") 
CLIENT_ID = "Iv1.f1a084535d67fabb"

def get_headers(token=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
             
        }
        if token:
            headers["Accept"]= "application/vnd.github+json"
            headers["Authorization"] = f"BEARER {token}"
            headers["X-GitHub-Api-Version"]="2022-11-28"
            print("returning headers with token")
            
        return headers
    

    
def delete_token_file():
    if not os.path.exists(TOKEN_FILE):
        return (True,"File does not exist ")
    try:
        os.remove(TOKEN_FILE)
        return (True, "File deleted")
    except Exception as error:
        return (False, error)
        
def get_rate_limit_status(token):
    url = "https://api.github.com/rate_limit"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"BEARER {token}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["resources"]["core"]["remaining"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        

def request_token(device_code):
        data = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
        headers = {"Accept": "application/json"}

        response = requests.post("https://github.com/login/oauth/access_token", data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    
def request_device_code():
    data = {"client_id": CLIENT_ID}
    headers = {"Accept": "application/json"}

    response = requests.post("https://github.com/login/device/code", data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def write_token_to_file(token):
    
    if not os.path.exists(os.path.dirname(TOKEN_FILE)):
        os.makedirs(os.path.dirname(TOKEN_FILE))
    with open(TOKEN_FILE, "w") as f:
        f.write(token)