import os
import json
from pathlib import Path

def check_tokens(asset_root):
    errors = []
    # Wczytaj index.json
    index_path = asset_root / "tokens/index.json"
    if not index_path.exists():
        print(f"Brak pliku: {index_path}")
        return
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)
    # Wczytaj start_tokens.json
    start_path = asset_root / "start_tokens.json"
    if not start_path.exists():
        print(f"Brak pliku: {start_path}")
        return
    with open(start_path, encoding="utf-8") as f:
        start_tokens = json.load(f)
    # Sprawdź każdy żeton ze start_tokens
    for token in start_tokens:
        token_id = token["id"]
        # Szukaj w index.json
        token_data = None
        if isinstance(index, dict):
            token_data = index.get(token_id)
        else:
            for t in index:
                if t.get("id") == token_id:
                    token_data = t
                    break
        if not token_data:
            errors.append(f"Brak definicji {token_id} w index.json")
            continue
        # Sprawdź ścieżkę do obrazka
        img_path = token_data.get("image")
        if not img_path:
            # Spróbuj domyślnej ścieżki
            nation = token_data.get("nation", "")
            img_path = f"assets/tokens/{nation}/{token_id}/token.png"
        img_file = Path(img_path)
        if not img_file.is_absolute():
            img_file = asset_root.parent / img_path
        if not img_file.exists():
            errors.append(f"Brak pliku PNG: {img_file}")
    # Podsumowanie
    if errors:
        print("\nBŁĘDY SPÓJNOŚCI ŻETONÓW:")
        for e in errors:
            print("-", e)
    else:
        print("Wszystkie żetony startowe mają pliki PNG i definicje w index.json!")

if __name__ == "__main__":
    asset_root = Path(__file__).parent.parent / "assets"
    check_tokens(asset_root)
