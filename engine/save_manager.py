import os
import json
import base64
from pathlib import Path
from engine.token import Token
from engine.player import Player

def _ensure_saves_dir(path):
    dir_name = os.path.dirname(path)
    if not dir_name:
        os.makedirs('saves', exist_ok=True)
        path = os.path.join('saves', path)
    else:
        os.makedirs(dir_name, exist_ok=True)
    return path

def save_game(path, engine, active_player=None):
    path = _ensure_saves_dir(path)
    def player_to_dict(p):
        return p.serialize()

    # Serializuj żetony z pełnymi danymi dla nowych żetonów
    tokens_data = []
    for token in engine.tokens:
        token_data = token.serialize()
        
        # Jeśli to nowy żeton, zapisz pełne dane + obraz
        if "nowy_" in token.id:
            json_path = Path(f"assets/tokens/aktualne/{token.id}.json")
            png_path = Path(f"assets/tokens/aktualne/{token.id}.png")
            
            # Wczytaj pełne dane JSON
            if json_path.exists():
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        token_data['full_data'] = json.load(f)
                except Exception as e:
                    print(f"[WARN] Nie udało się wczytać {json_path}: {e}")
            
            # Zakoduj obraz do base64
            if png_path.exists():
                try:
                    with open(png_path, 'rb') as f:
                        token_data['image_data'] = base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    print(f"[WARN] Nie udało się zakodować {png_path}: {e}")
        
        tokens_data.append(token_data)

    state = {
        "tokens": tokens_data,
        "players": [player_to_dict(p) for p in getattr(engine, 'players', [])],
        "turn": getattr(engine, 'turn', 1),
        # ZAPISUJEMY current_player jako id aktywnego gracza
        "current_player": getattr(engine, 'current_player_obj', getattr(engine, 'current_player', None)).id if hasattr(engine, 'current_player_obj') and getattr(engine, 'current_player_obj', None) else getattr(engine, 'current_player', 0),
        "weather": getattr(engine, 'weather', None).__dict__ if hasattr(engine, 'weather') and getattr(engine, 'weather', None) else None,
        "turn_manager": getattr(engine, 'turn_manager', None).__dict__ if hasattr(engine, 'turn_manager') and getattr(engine, 'turn_manager', None) else None,
        "active_player_info": {
            "id": getattr(active_player, 'id', None),
            "role": getattr(active_player, 'role', None),
            "nation": getattr(active_player, 'nation', None)
        },
        # Dodajemy key_points_state do zapisu
        "key_points_state": getattr(engine, 'key_points_state', {})
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # Wyczyść folder aktualne po zapisie
    cleanup_aktualne_folder()

def cleanup_aktualne_folder():
    """Usuwa nowe żetony z folderu aktualne po zapisie"""
    aktualne_path = Path("assets/tokens/aktualne")
    if aktualne_path.exists():
        for file_path in aktualne_path.iterdir():
            if file_path.name.startswith("nowy_"):
                try:
                    file_path.unlink()
                    print(f"[INFO] Usunięto: {file_path}")
                except Exception as e:
                    print(f"[WARN] Nie udało się usunąć {file_path}: {e}")

def load_game(path, engine):
    import types
    from core.ekonomia import EconomySystem
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)    # Odtwórz żetony
    engine.tokens = []
    aktualne_path = Path("assets/tokens/aktualne")
    aktualne_path.mkdir(parents=True, exist_ok=True)
    
    for tdata in state["tokens"]:
        from engine.token import Token
        token = Token.from_dict(tdata)
        engine.tokens.append(token)
        
        # Jeśli to nowy żeton z pełnymi danymi, odtwórz pliki
        if "nowy_" in token.id and "full_data" in tdata:
            json_path = aktualne_path / f"{token.id}.json"
            png_path = aktualne_path / f"{token.id}.png"
            
            # Zapisz JSON
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(tdata['full_data'], f, indent=2, ensure_ascii=False)
                print(f"[INFO] Odtworzono: {json_path}")
            except Exception as e:
                print(f"[WARN] Nie udało się odtworzyć {json_path}: {e}")
            
            # Zapisz obraz
            if "image_data" in tdata:
                try:
                    image_bytes = base64.b64decode(tdata['image_data'])
                    with open(png_path, 'wb') as f:
                        f.write(image_bytes)
                    print(f"[INFO] Odtworzono: {png_path}")
                except Exception as e:
                    print(f"[WARN] Nie udało się odtworzyć {png_path}: {e}")
    # Odtwórz graczy
    engine.players = []
    for pdata in state["players"]:
        player = Player(pdata["id"], pdata["nation"], pdata["role"], pdata.get("time_limit", 5), pdata.get("image_path"), None)
        # NIE nadpisuj __dict__ w całości, tylko ustaw kluczowe atrybuty:
        # (aby nie nadpisać np. referencji do economy)
        player.victory_points = pdata.get("victory_points", 0)
        player.vp_history = pdata.get("vp_history", [])
        # Odtwórz economy jako obiekt EconomySystem
        if "economy" in pdata and isinstance(pdata["economy"], dict):
            econ = EconomySystem()
            econ.__dict__.update(pdata["economy"])
            player.economy = econ
        # Zamień listy na sety tupli (odtwarzanie widoczności)
        for key in ["visible_hexes", "visible_tokens", "temp_visible_hexes", "temp_visible_tokens"]:
            if key in pdata and isinstance(pdata[key], list):
                setattr(player, key, set(tuple(x) if isinstance(x, list) else x for x in pdata[key]))
        engine.players.append(player)
    # Odtwórz inne stany
    if "turn" in state:
        engine.turn = state["turn"]
    if "current_player" in state:
        # Ustaw current_player jako id oraz current_player_obj jako obiekt gracza o tym id
        engine.current_player = state["current_player"]
        engine.current_player_obj = next((p for p in engine.players if getattr(p, 'id', None) == engine.current_player), None)
    # Odtwórz stan key_points
    if "key_points_state" in state and isinstance(state["key_points_state"], dict):
        engine.key_points_state = state["key_points_state"]
        print("[INFO] Wczytano stan punktów specjalnych (key_points) z zapisu gry")
    if "weather" in state and state["weather"]:
        if hasattr(engine, "weather") and engine.weather:
            engine.weather.__dict__.update(state["weather"])
        else:
            engine.weather = types.SimpleNamespace(**state["weather"])
    if "turn_manager" in state and state["turn_manager"]:
        if hasattr(engine, "turn_manager") and engine.turn_manager:
            engine.turn_manager.__dict__.update(state["turn_manager"])
        else:
            engine.turn_manager = types.SimpleNamespace(**state["turn_manager"])
    # Po wczytaniu przelicz widoczność
    # from engine.engine import update_all_players_visibility
    # update_all_players_visibility(engine.players, engine.tokens, engine.board)
    # Zwróć info o aktywnym graczu (do synchronizacji GUI)
    return state.get("active_player_info", None)
