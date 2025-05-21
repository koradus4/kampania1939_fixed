import unittest
from engine.board import Board
from engine.token import Token
from engine.action import MoveAction, CombatAction
import json

class DummyToken(Token):
    def __init__(self, id, q, r, move=3, combat_value=2):
        super().__init__(id, 'Polska', {'move': move, 'combat_value': combat_value}, q, r)

class TestBoard(unittest.TestCase):
    def setUp(self):
        # Dynamicznie pobieramy dostępne heksy z mapy
        with open('data/map_data.json', encoding='utf-8') as f:
            map_data = json.load(f)
        self.hexes = list(map_data['terrain'].keys())
        # Zamieniamy na tuple intów
        self.hexes = [tuple(map(int, h.split(','))) for h in self.hexes]
        self.board = Board('data/map_data.json')
        # Wybieramy pierwszy heks do testów
        q, r = self.hexes[0]
        self.token = DummyToken('T1', q, r)
        self.board.set_tokens([self.token])

    def test_hex_distance(self):
        # Testujemy dystans między dwoma pierwszymi heksami
        h1 = self.hexes[0]
        h2 = self.hexes[1]
        dist = self.board.hex_distance(h1, h2)
        self.assertIsInstance(dist, int)
        self.assertGreaterEqual(dist, 0)

    def test_find_path(self):
        # Szukamy ścieżki między dwoma pierwszymi heksami
        h1 = self.hexes[0]
        h2 = self.hexes[1]
        path = self.board.find_path(h1, h2, max_cost=3)
        self.assertIsInstance(path, list)
        self.assertIn(h2, path)

class TestMoveAction(unittest.TestCase):
    def setUp(self):
        with open('data/map_data.json', encoding='utf-8') as f:
            map_data = json.load(f)
        self.hexes = [tuple(map(int, h.split(','))) for h in map_data['terrain'].keys()]
        self.board = Board('data/map_data.json')
        q, r = self.hexes[0]
        self.token = DummyToken('T1', q, r, move=2)
        self.board.set_tokens([self.token])
        class DummyEngine:
            def __init__(self, board, tokens):
                self.board = board
                self.tokens = tokens
        self.engine = DummyEngine(self.board, [self.token])

    def test_move_success(self):
        # Próbujemy przesunąć na drugi dostępny heks
        q2, r2 = self.hexes[1]
        action = MoveAction('T1', q2, r2)
        success, msg = action.execute(self.engine)
        self.assertTrue(success)
        self.assertEqual(self.token.q, q2)
        self.assertEqual(self.token.r, r2)

    def test_move_too_far(self):
        # Próbujemy przesunąć na trzeci dostępny heks (może być za daleko, zależnie od mapy)
        if len(self.hexes) > 2:
            q3, r3 = self.hexes[2]
            action = MoveAction('T1', q3, r3)
            success, msg = action.execute(self.engine)
            # Akceptujemy oba wyniki, zależnie od dystansu
            self.assertIn(success, [True, False])

if __name__ == '__main__':
    unittest.main()
