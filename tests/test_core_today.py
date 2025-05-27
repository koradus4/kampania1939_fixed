import sys
import os
import tempfile
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.token import Token
from engine.save_manager import save_state, load_state
from engine.board import Board
from engine.action import MoveAction
from engine.engine import GameEngine
import unittest

class DummyEngine:
    def __init__(self, tokens, turn_number=1, current_player=0):
        self.tokens = tokens
        self.turn_number = turn_number
        self.current_player = current_player
        self.board = None  # plansza nie jest serializowana w testach

class TestTokenSerialization(unittest.TestCase):
    def test_token_serialize_and_from_dict(self):
        stats = {'move': 5, 'combat_value': 2}
        token = Token(id="T1", owner="A", stats=stats, q=2, r=3)
        data = token.serialize()
        token2 = Token.from_dict(data)
        self.assertEqual(token.id, token2.id)
        self.assertEqual(token.owner, token2.owner)
        self.assertEqual(token.q, token2.q)
        self.assertEqual(token.r, token2.r)
        self.assertEqual(token.stats, token2.stats)

class TestSaveLoad(unittest.TestCase):
    def test_save_and_load_state(self):
        stats = {'move': 5, 'combat_value': 2}
        token = Token(id="T1", owner="A", stats=stats, q=2, r=3)
        engine = DummyEngine([token])
        fd, path = tempfile.mkstemp()
        os.close(fd)
        try:
            save_state(engine, os.path.dirname(path))
            loaded = load_state(os.path.join(os.path.dirname(path), 'latest.json'))
            self.assertEqual(len(loaded['tokens']), 1)
            self.assertEqual(loaded['tokens'][0]['q'], 2)
        finally:
            os.remove(os.path.join(os.path.dirname(path), 'latest.json'))
            if os.path.exists(path):
                os.remove(path)

class TestMoveAction(unittest.TestCase):
    def test_move_action_execute(self):
        map_data = {"meta": {"hex_size": 10, "cols": 2, "rows": 2}, "terrain": {"0,0": {}, "1,0": {}}}
        fd, map_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(map_data, f)
        board = Board(map_path)
        stats = {'move': 5, 'combat_value': 2}
        token = Token(id="T1", owner="A", stats=stats, q=0, r=0)
        board.tokens = [token]
        class SimpleEngine:
            def __init__(self, board, tokens):
                self.board = board
                self.tokens = tokens
        engine = SimpleEngine(board, [token])
        action = MoveAction("T1", 1, 0)  # ruch na istniejący heks
        success, msg = action.execute(engine)
        self.assertTrue(success)
        self.assertEqual(token.q, 1)
        self.assertEqual(token.r, 0)
        os.remove(map_path)

class TestEngineTurnSave(unittest.TestCase):
    def test_end_turn_triggers_save(self):
        # Tworzymy tymczasowy katalog na snapshot
        import tempfile
        tmp_dir = tempfile.mkdtemp()
        # Minimalne pliki mapy i tokenów
        map_data = {"meta": {"hex_size": 10, "cols": 2, "rows": 2}, "terrain": {"0,0": {}, "1,0": {}}}
        fd, map_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(map_data, f)
        index_data = [{"id": "T1", "move": 5, "combat_value": 2}]
        start_data = [{"id": "T1", "q": 0, "r": 0}]
        fd2, index_path = tempfile.mkstemp(suffix='.json')
        os.close(fd2)
        fd3, start_path = tempfile.mkstemp(suffix='.json')
        os.close(fd3)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f)
        with open(start_path, 'w', encoding='utf-8') as f:
            json.dump(start_data, f)
        engine = GameEngine(map_path=map_path, tokens_index_path=index_path, tokens_start_path=start_path)
        try:
            engine.end_turn = lambda: __import__('engine.save_manager').save_manager.save_state(engine, tmp_dir)
            engine.end_turn()
            snapshot_path = os.path.join(tmp_dir, 'latest.json')
            loaded = load_state(snapshot_path)
            self.assertIsNotNone(loaded)
        finally:
            os.remove(map_path)
            os.remove(index_path)
            os.remove(start_path)
            import shutil
            shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    unittest.main()
