import json
import os

placed_tokens = []

def save_state():
    # utwórz katalog, jeśli nie istnieje
    os.makedirs(os.path.dirname("save/placed_tokens.json"), exist_ok=True)
    with open("save/placed_tokens.json", "w", encoding="utf-8") as f:
        json.dump(placed_tokens, f, ensure_ascii=False, indent=2)

def load_state():
    import os, json
    state_path = "save/placed_tokens.json"
    # upewnij się, że katalog istnieje
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    # jeśli plik nie istnieje lub jest pusty, zwróć pustą listę
    if not os.path.exists(state_path) or os.path.getsize(state_path) == 0:
        return []
    try:
        return json.load(open(state_path, encoding="utf-8"))
    except json.JSONDecodeError:
        return []
