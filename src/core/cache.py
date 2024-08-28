import json
import os
import shutil
import time
from pathlib import Path

from core.paths import Paths


class Cache:
    def __init__(self, paths: Paths):
        self.paths = paths
        self.current_cache_version = 2
        self.cache_directory = self.paths.cache_dir
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_directory / "index.json"

        if not self.is_index_file_valid():
            self.create_index_file()

    def is_index_file_valid(self):
        if not self.index_file.exists():
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
        self.index_file.parent.mkdir(exist_ok=True)
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump({"cache_version": self.current_cache_version}, file, indent=4)

    def get_data_from_cache(self, key):
        if not self.is_index_file_valid():
            self.create_index_file()
            return None
        with open(self.index_file, "r", encoding="utf-8") as file:
            index = json.load(file)
        data = index.get(key)
        if data is None:
            return None
        if not data["data"].is_file():
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
                json.dump(index, file, indent=4)
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
            json.dump(index, file, indent=4)

    def add_json_data_to_cache(self, key, data):
        if not self.is_index_file_valid():
            self.create_index_file()
        # create a new file with the data
        path = os.path.join(self.cache_directory, "files", f"{key}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # write the data to the file
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
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
