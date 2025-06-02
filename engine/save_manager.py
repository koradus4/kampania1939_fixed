import json
import os
from engine.token import Token

def _ensure_saves_dir(path):
    # Jeśli path nie zawiera katalogu, zapisz do 'saves/'
    dir_name = os.path.dirname(path)
    if not dir_name:
        dir_name = os.path.join(os.getcwd(), 'saves')
        os.makedirs(dir_name, exist_ok=True)
        path = os.path.join(dir_name, path)
    else:
        os.makedirs(dir_name, exist_ok=True)
    return path

def save_game(path, engine, active_player=None):
    """Zapisuje pełny stan gry do pliku JSON w katalogu 'saves/' jeśli nie podano innego."""
    path = _ensure_saves_dir(path)
    # Dodaj informację o aktywnym graczu (id, rola, nacja)
    if active_player is not None:
        current_player_obj = active_player
    else:
        current_player_obj = None
        if hasattr(engine, 'players') and hasattr(engine, 'current_player'):
            idx = getattr(engine, 'current_player', 0)
            if isinstance(idx, int) and 0 <= idx < len(engine.players):
                current_player_obj = engine.players[idx]
    state = {
        "tokens": [t.serialize() for t in engine.tokens],
        "turn": getattr(engine, 'turn', 1),
        "current_player": getattr(engine, 'current_player', 0),
        "players": [p.serialize() for p in getattr(engine, 'players', [])],
        "economy": [getattr(p, 'economy', None).__dict__ if getattr(p, 'economy', None) else None for p in getattr(engine, 'players', [])],
        "weather": getattr(engine, 'weather', None).__dict__ if hasattr(engine, 'weather') else None,
        "turn_manager": None,
        "active_player_info": {
            "id": getattr(current_player_obj, 'id', None),
            "role": getattr(current_player_obj, 'role', None),
            "nation": getattr(current_player_obj, 'nation', None)
        }
    }
    # Serializuj turn_manager, zamieniając Player na dict
    if hasattr(engine, 'turn_manager') and engine.turn_manager is not None:
        tm_dict = engine.turn_manager.__dict__.copy()
        if 'players' in tm_dict:
            tm_dict['players'] = [p.serialize() for p in tm_dict['players']]
        if 'game_engine' in tm_dict:
            tm_dict['game_engine'] = None  # nie serializujemy silnika
        if 'weather' in tm_dict and hasattr(tm_dict['weather'], '__dict__'):
            tm_dict['weather'] = tm_dict['weather'].__dict__
        state["turn_manager"] = tm_dict
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_game(path, engine):
    """Wczytuje pełny stan gry z pliku JSON z katalogu 'saves/' jeśli nie podano innego."""
    path = _ensure_saves_dir(path)
    import json
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)
    engine.tokens = [Token.from_dict(t) for t in state["tokens"]]
    engine.board.set_tokens(engine.tokens)
    engine.turn = state["turn"]
    engine.current_player = state["current_player"]
    if "players" in state:
        from engine.player import Player
        engine.players = []
        for p in state["players"]:
            player = Player(
                p.get('id'),
                p.get('nation'),
                p.get('role'),
                p.get('time_limit', 5),
                p.get('image_path'),
                None
            )
            if 'name' in p:
                player.name = p['name']
            if 'map_path' in p:
                player.map_path = p['map_path']
            engine.players.append(player)
    # Odtwórz ekonomię graczy
    for p, econ in zip(engine.players, state.get("economy", [])):
        if econ:
            from core.ekonomia import EconomySystem
            p.economy = EconomySystem()
            p.economy.__dict__.update(econ)
    if "weather" in state and hasattr(engine, 'weather'):
        from core.pogoda import Pogoda
        engine.weather = Pogoda()
        engine.weather.__dict__.update(state["weather"])
    if "turn_manager" in state and hasattr(engine, 'turn_manager'):
        from core.tura import TurnManager
        engine.turn_manager = TurnManager(engine.players, game_engine=engine)
        engine.turn_manager.__dict__.update(state["turn_manager"])
    # --- Nowość: zwróć info o aktywnym graczu ---
    return state.get("active_player_info", None)
