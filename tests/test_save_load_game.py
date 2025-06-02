import pytest
import os
import tempfile
from engine.engine import GameEngine
from engine.save_manager import save_game, load_game
from engine.player import Player
from core.ekonomia import EconomySystem

def test_save_and_load_game(tmp_path):
    # Przygotuj silnik gry i graczy
    engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    players = [
        Player(1, "Polska", "Generał"),
        Player(2, "Polska", "Dowódca"),
        Player(4, "Niemcy", "Generał"),
        Player(5, "Niemcy", "Dowódca")
    ]
    for p in players:
        p.economy = EconomySystem()
        p.economy.economic_points = 10
    engine.players = players
    engine.turn = 3
    engine.current_player = 2
    # Zapisz grę
    save_path = tmp_path / "test_save.json"
    save_game(str(save_path), engine)
    assert os.path.exists(save_path)
    # Zmień stan silnika
    engine.turn = 1
    engine.current_player = 0
    for p in engine.players:
        p.economy.economic_points = 0
    # Wczytaj grę
    load_game(str(save_path), engine)
    assert engine.turn == 3
    assert engine.current_player == 2
    assert all(p.economy.economic_points == 10 for p in engine.players)
    assert len(engine.tokens) > 0
