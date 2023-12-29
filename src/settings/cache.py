import os 
import json 
import time

class Cache:
    def __init__(self, master, settings, metadata):
        self.master = master
        self.settings = settings
        self.metadata = metadata
        if os.path.exists(os.path.join(os.getcwd(), "PORTABLE.txt")):
            self.cache_directory = os.path.join(os.getcwd(), "cache")
        else:
            self.cache_directory = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "cache")
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)
        self.index_file = os.path.join(self.cache_directory, "index.json")
        if not os.path.exists(self.index_file):
            self.create_index_file()
        else:
            with open(self.index_file, "r", encoding="utf-8") as file:
                try:
                    json.load(file)
                except json.JSONDecodeError:
                    self.create_index_file()

    def create_index_file(self):
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump({}, file)
            
    def add_to_index(self, key, data):
        if not os.path.exists(self.index_file):
            self.create_index_file()
        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)
        
        index[key] = {
            "data": data,
            "time": time.time()
        }
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump(index, file)
    
    def remove_from_index(self, key):
        if not os.path.exists(self.index_file):
            self.create_index_file()
        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)
        if key in index:
            if os.path.isfile(index[key]["data"]):
                os.remove(index[key]["data"])
            del index[key]
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump(index, file)
            
    def get_cached_data(self, key):
        if not os.path.exists(self.index_file):
            self.create_index_file()
            return None
        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)
        if key in index:
            if "[PATH]" in key and (not os.path.exists(index[key]["data"] or not os.path.isfile(index[key]["data"]))):
                self.remove_from_index(key)
                return None
            return index[key]
        else:
            return None
    
    def move_image_to_cache(self, name, image_path):
        if not os.path.isfile(image_path):
            return (False, "No such file: '{image_path}'")

        new_path = os.path.join(self.cache_directory, "images", os.path.basename(image_path))
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if os.path.exists(new_path):
            os.remove(new_path)
        try:
            os.rename(image_path, new_path)
        except OSError as e:
            return (False, f"Error moving file: {e}")

        self.add_to_index(name, new_path)
        
    def move_file_to_cache(self, name, file_path):
        if not os.path.isfile(file_path):
            return (False, f"No such file: '{file_path}'")

        new_path = os.path.join(self.cache_directory, "files", os.path.basename(file_path))
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if os.path.exists(new_path):
            os.remove(new_path)
        try:
            os.rename(file_path, new_path)
        except OSError as e:
            return (False, f"Error moving file: {e}")

        self.add_to_index(name, new_path)
        return True
        