"""
Moduł pomocniczy do ładowania danych (mapy, żetonów).
"""
import os
import json
from typing import Tuple, List, Dict, Any
from tkinter import messagebox
from model import mapa


def load_map_data(json_path: str) -> Dict[str, Any]:
    """
    Wczytuje dane mapy z pliku JSON i zwraca słownik z kluczami:
    - hex_centers: słownik pozycji środków heksów (współrzędne)
    - hex_data: słownik danych poszczególnych heksów (teren, obiekty, jednostki)
    - terrain_types: słownik typów terenu (jeśli zdefiniowano)
    - hex_defaults: domyślne modyfikatory dla heksów (np. obrona, ruch)
    - config: konfiguracja siatki mapy (np. hex_size, grid_cols, grid_rows)
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Nie znaleziono pliku danych mapy: {json_path}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Problem podczas wczytywania pliku mapy: {e}")

    result = {
        "hex_centers": {},
        "hex_data": {},
        "terrain_types": {},
        "hex_defaults": {"defense_mod": 0, "move_mod": 0},
        "config": {}
    }

    # Wczytaj dane z pliku JSON
    result["hex_defaults"] = map_data.get("defaults", {}).get("hex", result["hex_defaults"])
    result["hex_data"] = map_data.get("hex_data", {})
    result["terrain_types"] = map_data.get("terrain_types", {})
    result["config"] = map_data.get("config", {})

    # Konwersja współrzędnych heksów na tuple
    for hex_id, coords in map_data.get("hex_centers", {}).items():
        result["hex_centers"][hex_id] = tuple(coords) if isinstance(coords, list) else coords

    # Generowanie pozycji heksów, jeśli brak danych
    if not result["hex_centers"]:
        result["hex_centers"] = mapa.generate_hex_positions(result["config"])

    return result


def load_tokens_from_folder(tokens_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Wczytuje żetony z podanego folderu i jego podfolderów.
    Zwraca krotkę (polish_tokens, german_tokens), gdzie każda jest listą słowników z informacjami o żetonach.
    """
    polish_tokens = []
    german_tokens = []

    if not os.path.exists(tokens_path):
        os.makedirs(tokens_path, exist_ok=True)
        messagebox.showinfo("Brak żetonów", f"Utworzono pusty folder żetonów: {tokens_path}. Dodaj pliki żetonów przed rozpoczęciem gry.")
        return polish_tokens, german_tokens

    # Upewnij się, że podfoldery dla każdej nacji istnieją
    _ensure_subfolders_exist(tokens_path, ["polskie", "niemieckie"])

    print(f"[INFO] Skanowanie folderu żetonów: {tokens_path}")
    for dirpath, _, filenames in os.walk(tokens_path):
        if dirpath == tokens_path:
            continue  # Pomijamy główny katalog

        token_obj = _process_token_folder(dirpath, filenames)
        if not token_obj:
            continue

        # Przypisz żeton do odpowiedniej nacji
        nation = token_obj.get("nation", "")
        if nation == "polskie":
            polish_tokens.append(token_obj)
        elif nation == "niemieckie":
            german_tokens.append(token_obj)

    if not polish_tokens and not german_tokens:
        messagebox.showwarning("Brak żetonów", "Foldery z żetonami są puste. Dodaj pliki żetonów i spróbuj ponownie.")
    else:
        print(f"[INFO] Wczytano {len(polish_tokens)} polskich i {len(german_tokens)} niemieckich żetonów.")

    return polish_tokens, german_tokens


def _ensure_subfolders_exist(base_path: str, subfolders: List[str]) -> None:
    """Tworzy podfoldery w bazowym katalogu, jeśli nie istnieją."""
    for folder in subfolders:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)


def _process_token_folder(dirpath: str, filenames: List[str]) -> Dict[str, Any]:
    """
    Przetwarza folder z żetonami, wczytując dane o żetonie.
    Zwraca słownik z informacjami o żetonie lub None, jeśli nie znaleziono danych.
    """
    png_files = [f for f in filenames if f.lower().endswith('.png')]
    if not png_files:
        return {}

    token_name = os.path.basename(dirpath)
    token_path = os.path.join(dirpath, png_files[0])
    token_data_path = os.path.join(dirpath, "token_data.json")
    token_data = _load_json_file(token_data_path)

    nation = _determine_nation(token_name, dirpath, token_data)
    if not nation:
        print(f"[UWAGA] Nie rozpoznano nacji żetonu: {token_name} (pominięto)")
        return {}

    print(f"[INFO] Załadowano żeton: {token_name} (nacja: {nation})")
    return {
        "name": token_name,
        "path": token_path,
        "data": token_data,
        "nation": nation
    }


def _load_json_file(file_path: str) -> Dict[str, Any]:
    """Wczytuje dane z pliku JSON, jeśli istnieje, w przeciwnym razie zwraca pusty słownik."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[BŁĄD] Błąd wczytywania pliku JSON: {file_path}: {e}")
        return {}


def _determine_nation(token_name: str, dirpath: str, token_data: Dict[str, Any]) -> str:
    """
    Określa nację żetonu na podstawie nazwy, ścieżki lub danych z pliku JSON.
    """
    nation = token_data.get("nation", "")
    if "Polska" in token_name or "polska" in token_name or nation == "Polska" or "polskie" in dirpath.lower():
        return "polskie"
    elif "Niemcy" in token_name or "niemcy" in token_name or nation == "Niemcy" or "niemieckie" in dirpath.lower():
        return "niemieckie"
    return ""
