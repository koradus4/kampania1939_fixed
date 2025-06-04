import os
import json
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
        d = p.__dict__.copy()
        # Serializuj economy jako dict, nie jako obiekt
        if hasattr(p, "economy") and p.economy is not None:
            if hasattr(p.economy, "__dict__"):
                d["economy"] = p.economy.__dict__.copy()
            else:
                d["economy"] = p.economy
        # Zamień sety na listy (JSON nie obsługuje setów)
        for key in ["visible_hexes", "visible_tokens", "temp_visible_hexes", "temp_visible_tokens"]:
            if key in d and isinstance(d[key], set):
                d[key] = [list(x) if isinstance(x, tuple) else x for x in d[key]]
        return d

    state = {
        "tokens": [t.serialize() for t in engine.tokens],
        "players": [player_to_dict(p) for p in getattr(engine, 'players', [])],
        "turn": getattr(engine, 'turn', 1),
        "current_player": getattr(engine, 'current_player', 0),
        "weather": getattr(engine, 'weather', None).__dict__ if hasattr(engine, 'weather') and getattr(engine, 'weather', None) else None,
        "turn_manager": getattr(engine, 'turn_manager', None).__dict__ if hasattr(engine, 'turn_manager') and getattr(engine, 'turn_manager', None) else None,
        "active_player_info": {
            "id": getattr(active_player, 'id', None),
            "role": getattr(active_player, 'role', None),
            "nation": getattr(active_player, 'nation', None)
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_game(path, engine):
    import types
    from core.ekonomia import EconomySystem
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)
    # Odtwórz żetony
    engine.tokens = []
    for tdata in state["tokens"]:
        from engine.token import Token
        token = Token.from_dict(tdata)
        engine.tokens.append(token)
    # Odtwórz graczy
    engine.players = []
    for pdata in state["players"]:
        player = Player(pdata["id"], pdata["nation"], pdata["role"], pdata.get("time_limit", 5), pdata.get("image_path"), None)
        player.__dict__.update(pdata)
        # Odtwórz economy jako obiekt EconomySystem
        if "economy" in pdata and isinstance(pdata["economy"], dict):
            econ = EconomySystem()
            econ.__dict__.update(pdata["economy"])
            player.economy = econ
        # Zamień listy na sety tupli (odtwarzanie widoczności)
        for key in ["visible_hexes", "visible_tokens", "temp_visible_hexes", "temp_visible_tokens"]:
            if key in player.__dict__ and isinstance(player.__dict__[key], list):
                player.__dict__[key] = set(tuple(x) if isinstance(x, list) else x for x in player.__dict__[key])
        engine.players.append(player)
    # Odtwórz inne stany
    if "turn" in state:
        engine.turn = state["turn"]
    if "current_player" in state:
        engine.current_player = state["current_player"]
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
    from engine.engine import update_all_players_visibility
    update_all_players_visibility(engine.players, engine.tokens, engine.board)
    # Zwróć info o aktywnym graczu (do synchronizacji GUI)
    return state.get("active_player_info", None)
