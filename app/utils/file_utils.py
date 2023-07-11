import os
import json

from config import Config

class FileUtils:

    def get_file_str(filename):
        file_path = os.path.join(Config().get_inner_config_path(), filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data