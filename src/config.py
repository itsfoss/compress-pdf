import os
import sys
import shutil
import json


configFile = os.environ.get("HOME") + "/.config/compress-pdf/config.json"

class Config:

    def __init__(self):
        self.data = dict()
        try:
            with open(configFile, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                "rememberDir": False,
                "lastDir": os.environ.get("HOME"),
                "outputDir": "src",
                "defaultCompressionLevel": None,
                "showFullPath": False
            }
        
        for key, value in self.data.items():
            setattr(self, key, value)

        
    def save(self):
        try:
            with open(configFile, 'w') as f:
                f.write(json.dumps(self.data))
        except Exception:
            pass