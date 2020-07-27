

import json

import xbmc
import xbmcaddon
import xbmcvfs


class SharedData:

    def __init__(self):
        self.folder = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode("utf-8")
        if not xbmcvfs.exists(self.folder):
            xbmcvfs.mkdir(self.folder)
        self.file_path = self.folder + "shared_data.json"
        with open(self.file_path, "w") as file:
            file.write("{}")

    def __getFileContent(self):
        try:
            with open(self.file_path) as file:
                file_content = file.read()
        except IOError:
            file_content = "{}"

        json_content = json.loads(file_content)
        return json_content

    def set(self, key, value):
        json_content = self.__getFileContent()

        # Simple "json-path"-like set algorithm
        keys = key.split('.')
        keys_length = len(keys)
        item = json_content
        for index, key in enumerate(keys):
            if key not in item:
                item[key] = {}

            if index + 1 < keys_length:
                if not isinstance(item[key], dict):
                    item[key] = {}
                item = item[key]
            else:
                item[key] = value

        file_content = json.dumps(json_content)
        with open(self.file_path, "w") as file:
            file.write(file_content)

    def get(self, key):
        json_content = self.__getFileContent()

        # Simple "json-path"-like get algorithm
        keys = key.split(".")
        item = json_content
        try:
            for key in keys:
                item = item.get(key, {})
        except:
            return None

        return item
