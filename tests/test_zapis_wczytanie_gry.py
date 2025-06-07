import pytest
import os
import tempfile
from engine.engine import GameEngine
from engine.save_manager import save_game, load_game
from engine.player import Player
from core.ekonomia import EconomySystem
from core.pogoda import Pogoda
from core.tura import TurnManager

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
        p.economy.special_points = 2
    engine.players = players
    engine.turn = 3
    engine.current_player = 2
    # Dodaj pogodę i menedżera tur
    engine.weather = Pogoda()
    engine.weather.temperatura = 17
    engine.weather.zachmurzenie = "Bezchmurnie"
    engine.weather.opady = "Bezdeszczowo"
    engine.turn_manager = TurnManager(players, game_engine=engine)
    engine.turn_manager.current_turn = 7
    engine.turn_manager.current_player_index = 1
    # Ustaw żetonom niestandardowe wartości
    for t in engine.tokens:
        t.q = 5
        t.r = 7
        t.maxMovePoints = 12
        t.currentMovePoints = 8
        t.movement_mode = "march"
        break  # tylko pierwszy żeton
    # Zapisz grę
    save_path = tmp_path / "test_save.json"
    save_game(str(save_path), engine)
    assert os.path.exists(save_path)
    # Zmień stan silnika
    engine.turn = 1
    engine.current_player = 0
    for p in engine.players:
        p.economy.economic_points = 0
        p.economy.special_points = 0
    if hasattr(engine, 'weather'):
        engine.weather.temperatura = -99
    if hasattr(engine, 'turn_manager'):
        engine.turn_manager.current_turn = 0
        engine.turn_manager.current_player_index = 0
    for t in engine.tokens:
        t.q = 0
        t.r = 0
        t.maxMovePoints = 1
        t.currentMovePoints = 1
        t.movement_mode = "combat"
        break
    # Wczytaj grę
    load_game(str(save_path), engine)
    # --- Sprawdzenia ---
    assert engine.turn == 3
    assert engine.current_player == 2
    assert all(p.economy.economic_points == 10 for p in engine.players)
    assert all(p.economy.special_points == 2 for p in engine.players)
    assert len(engine.tokens) > 0
    # Pogoda
    if hasattr(engine, 'weather'):
        assert engine.weather.temperatura == 17
        assert engine.weather.zachmurzenie == "Bezchmurnie"
        assert engine.weather.opady == "Bezdeszczowo"
    # Menedżer tur
    if hasattr(engine, 'turn_manager'):
        assert engine.turn_manager.current_turn == 7
        assert engine.turn_manager.current_player_index == 1
    # Żetony (pierwszy)
    t = engine.tokens[0]
    assert t.q == 5 and t.r == 7
    assert t.maxMovePoints == 12
    assert t.currentMovePoints == 8
    assert t.movement_mode == "march"

def test_save_and_load_after_modification(tmp_path):
    # Test: modyfikacja stanu, zapis, odczyt i weryfikacja
    engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    players = [
        Player(1, "Polska", "Generał"),
        Player(2, "Polska", "Dowódca")
    ]
    for p in players:
        p.economy = EconomySystem()
        p.economy.economic_points = 99
        p.economy.special_points = 7
    engine.players = players
    engine.turn = 11
    engine.current_player = 1
    engine.weather = Pogoda()
    engine.weather.temperatura = -3
    engine.weather.zachmurzenie = "Duże zachmurzenie"
    engine.weather.opady = "Intensywne opady"
    # Zmień żeton
    t = engine.tokens[0]
    t.q = 9
    t.r = 2
    t.maxMovePoints = 20
    t.currentMovePoints = 15
    t.movement_mode = "recon"
    # Zapisz i odczytaj
    save_path = tmp_path / "test_save2.json"
    save_game(str(save_path), engine)
    t.q = 0; t.r = 0; t.maxMovePoints = 1; t.currentMovePoints = 1; t.movement_mode = "combat"
    engine.turn = 0
    engine.current_player = 0
    for p in engine.players:
        p.economy.economic_points = 0
        p.economy.special_points = 0
    engine.weather.temperatura = 0
    engine.weather.zachmurzenie = ""
    engine.weather.opady = ""
    load_game(str(save_path), engine)
    # Sprawdź
    assert engine.turn == 11
    assert engine.current_player == 1
    assert all(p.economy.economic_points == 99 for p in engine.players)
    assert all(p.economy.special_points == 7 for p in engine.players)
    t = engine.tokens[0]
    assert t.q == 9 and t.r == 2
    assert t.maxMovePoints == 20
    assert t.currentMovePoints == 15
    assert t.movement_mode == "recon"
    assert engine.weather.temperatura == -3
    assert engine.weather.zachmurzenie == "Duże zachmurzenie"
    assert engine.weather.opady == "Intensywne opady"
