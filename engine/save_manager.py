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

def save_game(path, engine):
    """Zapisuje pełny stan gry do pliku JSON w katalogu 'saves/' jeśli nie podano innego."""
    path = _ensure_saves_dir(path)
    state = {
        "tokens": [t.serialize() for t in engine.tokens],
        "turn": getattr(engine, 'turn', 1),
        "current_player": getattr(engine, 'current_player', 0),
        "players": [p.serialize() for p in getattr(engine, 'players', [])],
        "economy": [getattr(p, 'economy', None).__dict__ if getattr(p, 'economy', None) else None for p in getattr(engine, 'players', [])],
        "weather": getattr(engine, 'weather', None).__dict__ if hasattr(engine, 'weather') else None,
        "turn_manager": getattr(engine, 'turn_manager', None).__dict__ if hasattr(engine, 'turn_manager') else None,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_game(path, engine):
    """Wczytuje pełny stan gry z pliku JSON z katalogu 'saves/' jeśli nie podano innego."""
    path = _ensure_saves_dir(path)
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
            # Ustaw dodatkowe atrybuty jeśli są w serializacji
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
    # Dodaj tu kolejne elementy jeśli będą serializowane (np. historia)
