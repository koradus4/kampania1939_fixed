import json
from pathlib import Path

class ZetonyMapy:
    def __init__(self, index_path=None, start_path=None):
        if index_path is None:
            index_path = Path("assets") / "tokens" / "index.json"
        if start_path is None:
            start_path = Path("assets") / "start_tokens.json"
        self.zetony_def = self._load_index(index_path)
        self.zetony_on_map = self._load_start(start_path)

    def _load_index(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return {z["id"]: z for z in json.load(f)}

    def _load_start(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_token_data(self, token_id):
        return self.zetony_def.get(token_id)

    def get_tokens_on_map(self):
        return self.zetony_on_map
