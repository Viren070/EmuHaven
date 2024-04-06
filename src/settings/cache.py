import json
import os
import shutil
import time


class Cache:
    def __init__(self, master, settings, metadata):
        self.master = master
        self.settings = settings
        self.metadata = metadata
        self.current_cache_version = 2
        if os.path.exists(os.path.join(os.getcwd(), "PORTABLE.txt")):
            self.cache_directory = os.path.join(os.getcwd(), "portable", "cache")
        else:
            self.cache_directory = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "cache")
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)
        self.index_file = os.path.join(self.cache_directory, "index.json")
        
        if not self.is_index_file_valid():
            self.create_index_file()

    def is_index_file_valid(self):
        if not os.path.exists(self.index_file):
            return False
        with open(self.index_file, "r", encoding="utf-8") as file:
            try:
                contents = json.load(file)
                if contents.get("cache_version") != self.current_cache_version:
                    return False
                
            except json.JSONDecodeError:
                return False
        return True

    def create_index_file(self):
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump({"cache_version": 2}, file)

    def get_data_from_cache(self, key):
        if not self.is_index_file_valid():
            self.create_index_file()
            return None
        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)
        data = index.get(key)
        if data is None:
            return None
        if not os.path.isfile(data["data"]):
            self.remove_from_index(key)
            return None
        return data

    def add_to_index(self, key, data):
        if not self.is_index_file_valid():
            self.create_index_file()

        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)

        index[key] = {
            "data": data,
            "time": time.time()
        }
        try:
            with open(self.index_file, "w", encoding="utf-8") as file:
                json.dump(index, file)
        except Exception as error:
            return (False, error)
        return (True, data)

    def remove_from_index(self, key, delete_data=True):
        if not self.is_index_file_valid():
            self.create_index_file()
            return None
        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)
        if key in index:
            if os.path.isfile(str(index[key]["data"])) and delete_data:
                os.remove(index[key]["data"])
            del index[key]
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump(index, file)

    def add_json_data_to_cache(self, key, data):
        if not self.is_index_file_valid():
            self.create_index_file()
        # create a new file with the data
        path = os.path.join(self.cache_directory, "files", f"{key}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # write the data to the file
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)
        # add the path to the index file
        self.add_to_index(key, path)

    def get_json_data_from_cache(self, key):
        if not self.is_index_file_valid():
            self.create_index_file()
            return None
        # get the path from the index file
        data = self.get_data_from_cache(key)
        if data is None:
            return None
        # read the data from the file
        with open(data["data"], "r", encoding="utf-8") as file:
            return {"data": json.load(file), "time": data["time"]}
        
    def add_custom_file_to_cache(self, key, file_path): 
        if not self.is_index_file_valid():
            self.create_index_file()
        # declare variable to store the path of the new file
        new_dir = os.path.join(self.cache_directory, "files")
        os.makedirs(new_dir, exist_ok=True)
        path = os.path.join(new_dir, os.path.basename(file_path))
        try:
            shutil.move(file_path, path)
        except OSError as error:
            return (False, error)
        # add this path to the index file with given key
        return self.add_to_index(key, path)

   