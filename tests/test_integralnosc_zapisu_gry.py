# Test integralności save/load dla silnika gry
import os
import tempfile
from engine.save_manager import save_game, load_game
from engine.engine import GameEngine
from engine.player import Player
from core.ekonomia import EconomySystem

def test_save_load_integrity():
    # 1. Przygotuj silnik gry i graczy
    engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    # Inicjalizacja graczy (jak w main_alternative.py)
    players = [
        Player(1, "Polska", "Generał", 5),
        Player(2, "Polska", "Dowódca", 5),
        Player(3, "Polska", "Dowódca", 5),
        Player(4, "Niemcy", "Generał", 5),
        Player(5, "Niemcy", "Dowódca", 5),
        Player(6, "Niemcy", "Dowódca", 5),
    ]
    for p in players:
        if not hasattr(p, 'economy') or p.economy is None:
            p.economy = EconomySystem()
    engine.players = players
    engine.current_player_obj = players[0]

    tokens_before = [(t.id, getattr(t, 'q', None), getattr(t, 'r', None), getattr(t, 'currentMovePoints', None), getattr(t, 'currentFuel', None), getattr(t, 'combat_value', None)) for t in engine.tokens]
    players_before = [(p.id, p.nation, getattr(p, 'victory_points', 0), getattr(p, 'economy', None).economic_points if getattr(p, 'economy', None) else 0) for p in engine.players]
    turn_before = getattr(engine, 'turn', 1)
    current_player_id = getattr(engine, 'current_player_obj', engine.players[0]).id

    # 2. Zapisz grę do pliku tymczasowego
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        save_path = tmp.name
    save_game(save_path, engine, active_player=getattr(engine, 'current_player_obj', None))

    # 3. Wczytaj grę do nowego silnika
    engine2 = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    # Inicjalizacja graczy w nowym silniku
    players2 = [
        Player(1, "Polska", "Generał", 5),
        Player(2, "Polska", "Dowódca", 5),
        Player(3, "Polska", "Dowódca", 5),
        Player(4, "Niemcy", "Generał", 5),
        Player(5, "Niemcy", "Dowódca", 5),
        Player(6, "Niemcy", "Dowódca", 5),
    ]
    for p in players2:
        if not hasattr(p, 'economy') or p.economy is None:
            p.economy = EconomySystem()
    engine2.players = players2
    engine2.current_player_obj = players2[0]

    load_game(save_path, engine2)
    os.remove(save_path)

    # 4. Sprawdź żetony
    tokens_after = [(t.id, getattr(t, 'q', None), getattr(t, 'r', None), getattr(t, 'currentMovePoints', None), getattr(t, 'currentFuel', None), getattr(t, 'combat_value', None)) for t in engine2.tokens]
    assert tokens_before == tokens_after, "Stan żetonów nie zgadza się po wczytaniu!"

    # 5. Sprawdź graczy (VP, ekonomia)
    players_after = [(p.id, p.nation, getattr(p, 'victory_points', 0), getattr(p, 'economy', None).economic_points if getattr(p, 'economy', None) else 0) for p in engine2.players]
    assert players_before == players_after, "Stan graczy (VP, ekonomia) nie zgadza się po wczytaniu!"

    # 6. Sprawdź turę i aktywnego gracza
    assert getattr(engine2, 'turn', 1) == turn_before, "Numer tury nie zgadza się po wczytaniu!"
    assert getattr(engine2, 'current_player_obj', engine2.players[0]).id == current_player_id, "Aktywny gracz nie zgadza się po wczytaniu!"

    print("Test save/load przeszedł pomyślnie!")

if __name__ == "__main__":
    test_save_load_integrity()
