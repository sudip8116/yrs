import json
from .path_manager import PathManager


class VarManager:
    path = "save-data"

    @staticmethod
    def init():
        PathManager.create_path(VarManager.path)

    @staticmethod
    def set(key: str, value):
        with open(PathManager.get_path(f"{VarManager.path}/{key}.json"), "w") as f:
            f.write(json.dumps(value))

    @staticmethod
    def get(key: str, default=None):
        f_path = PathManager.get_path(f"{VarManager.path}/{key}.json")
        if not PathManager.exists_path(f_path):
            return default
        with open(f_path, "r") as f:
            try:
                return json.loads(f.read())
            except:
                return default
