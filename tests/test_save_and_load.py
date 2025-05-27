import pytest
from engine.engine import GameEngine
from engine.save_manager import save_state, load_state
from engine.token import Token
import os

class DummyEngine:
    def __init__(self):
        self.turn_number = 5
        self.current_player = "3 (Polska)"
        self.tokens = [
            Token(id="T1", owner="3 (Polska)", stats={"move": 10}, q=8, r=0),
            Token(id="T2", owner="3 (Polska)", stats={"move": 8}, q=9, r=0)
        ]
        self.board = type("Board", (), {"terrain": {}})()
        self.logs = [
            {"actor": "3 (Polska)", "action": "move", "from": [8,0], "to": [9,0]}
        ]

def test_save_and_load(tmp_path):
    engine = DummyEngine()
    save_state(engine, tmp_path)
    loaded = load_state(os.path.join(tmp_path, "latest.json"))
    assert loaded["turn_number"] == engine.turn_number
    assert len(loaded["tokens"]) == len(engine.tokens)
    assert loaded["tokens"][0]["id"] == engine.tokens[0].id
    assert loaded["tokens"][0]["q"] == engine.tokens[0].q
    assert loaded["tokens"][0]["stats"]["move"] == engine.tokens[0].stats["move"]
