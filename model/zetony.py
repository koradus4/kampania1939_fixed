import os
import json
from pathlib import Path

class ZetonyMapy:
    def __init__(self, index_path=None, start_tokens_path=None):
        if index_path is None:
            index_path = os.path.join(os.path.dirname(__file__), '../assets/tokens/index.json')
        if start_tokens_path is None:
            start_tokens_path = os.path.join(os.path.dirname(__file__), '../assets/start_tokens.json')
        self.zetony_def = self._load_index(index_path)
        self.start_tokens = self._load_start_tokens(start_tokens_path)

    def _load_index(self, path):
        if not os.path.exists(path):
            print(f"[WARN] Brak pliku index.json: {path}. Lista żetonów będzie pusta.")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Jeśli lista, zamień na dict po id
            if isinstance(data, list):
                return {t["id"]: t for t in data if "id" in t}
            return data

    def _load_start_tokens(self, path):
        if not os.path.exists(path):
            print(f"[INFO] Brak pliku start_tokens.json: {path}. Brak startowych żetonów.")
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_token_data(self, token_id):
        return self.zetony_def.get(token_id)

    def get_tokens_on_map(self):
        return self.start_tokens
