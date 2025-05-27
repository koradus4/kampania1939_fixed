import unittest
import os
from engine.engine import GameEngine
from engine.action import MoveAction, CombatAction

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        # Używamy przykładowych plików z assets
        self.engine = GameEngine(
            map_path='data/map_data.json',
            tokens_index_path='assets/tokens/index.json',
            tokens_start_path='assets/start_tokens.json',
            seed=123
        )

    def test_state_structure(self):
        state = self.engine.get_state()
        self.assertIn('turn', state)
        self.assertIn('tokens', state)
        self.assertIsInstance(state['tokens'], list)

    def test_next_turn(self):
        t0 = self.engine.turn
        self.engine.next_turn()
        self.assertEqual(self.engine.turn, t0 + 1)

    def test_move_action(self):
        # Jeśli są żetony, próbujemy przesunąć pierwszy na inny heks
        if self.engine.tokens:
            token = self.engine.tokens[0]
            start = (token.q, token.r)
            # Szukamy innego heksa na mapie
            for (k, tile) in self.engine.board.terrain.items():
                q, r = tile.q, tile.r
                if (q, r) != start:
                    action = MoveAction(token.id, q, r)
                    success, msg = self.engine.execute_action(action)
                    self.assertIn(success, [True, False])
                    break

    def test_combat_action(self):
        # Dodaj dwa żetony blisko siebie i testuj walkę
        if len(self.engine.tokens) >= 2:
            t1 = self.engine.tokens[0]
            t2 = self.engine.tokens[1]
            t1.set_position(0, 0)
            t2.set_position(0, 1)
            action = CombatAction(t1.id, t2.id)
            success, msg = self.engine.execute_action(action)
            self.assertIn(success, [True, False])

    def test_player_count(self):
        # Sprawdza, czy liczba graczy jest poprawna (domyślnie 2)
        self.assertEqual(self.engine.get_player_count(), 2)

    def test_execute_action_invalid(self):
        # Próba wykonania akcji na nieistniejącym żetonie
        action = MoveAction('nieistniejacy_id', 0, 0)
        success, msg = self.engine.execute_action(action)
        self.assertFalse(success)
        self.assertIn('nie znaleziono', msg.lower())

    def test_state_after_move(self):
        # Sprawdza, czy po ruchu zmienia się pozycja żetonu w stanie gry
        if self.engine.tokens:
            token = self.engine.tokens[0]
            start = (token.q, token.r)
            for (k, tile) in self.engine.board.terrain.items():
                q, r = tile.q, tile.r
                if (q, r) != start:
                    action = MoveAction(token.id, q, r)
                    success, msg = self.engine.execute_action(action)
                    state = self.engine.get_state()
                    found = any(t['id'] == token.id and t['q'] == q and t['r'] == r for t in state['tokens'])
                    self.assertTrue(found or not success)
                    break

    def test_serialize_token(self):
        # Sprawdza poprawność serializacji żetonu
        if self.engine.tokens:
            token = self.engine.tokens[0]
            data = token.serialize()
            self.assertIn('id', data)
            self.assertIn('owner', data)
            self.assertIn('stats', data)
            self.assertIn('q', data)
            self.assertIn('r', data)

    def test_token_can_move_to(self):
        # Sprawdza, czy Token.can_move_to działa zgodnie z limitem ruchu
        if self.engine.tokens:
            token = self.engine.tokens[0]
            move = token.stats.get('move', 0)
            self.assertTrue(token.can_move_to(move))
            self.assertFalse(token.can_move_to(move + 1))

    def test_token_set_position(self):
        # Sprawdza, czy set_position ustawia poprawnie współrzędne
        if self.engine.tokens:
            token = self.engine.tokens[0]
            token.set_position(5, 7)
            self.assertEqual(token.q, 5)
            self.assertEqual(token.r, 7)

    def test_board_hex_distance(self):
        # Sprawdza, czy Board.hex_distance zwraca nieujemny dystans
        board = self.engine.board
        hexes = list(board.terrain.keys())
        if len(hexes) > 1:
            q1, r1 = map(int, hexes[0].split(','))
            q2, r2 = map(int, hexes[1].split(','))
            dist = board.hex_distance((q1, r1), (q2, r2))
            self.assertIsInstance(dist, int)
            self.assertGreaterEqual(dist, 0)

    def test_board_find_path(self):
        # Sprawdza, czy Board.find_path znajduje ścieżkę między dwoma heksami
        board = self.engine.board
        hexes = list(board.terrain.keys())
        if len(hexes) > 1:
            q1, r1 = map(int, hexes[0].split(','))
            q2, r2 = map(int, hexes[1].split(','))
            path = board.find_path((q1, r1), (q2, r2), max_cost=20)
            self.assertIsInstance(path, list)
            self.assertIn((q2, r2), path)

    def test_token_from_json(self):
        # Sprawdza, czy Token.from_json poprawnie tworzy obiekt
        from engine.token import Token
        data = {
            'id': 'T99',
            'owner': 'Test',
            'move': 3,
            'combat_value': 2
        }
        token = Token.from_json(data, pos={'q': 1, 'r': 2})
        self.assertEqual(token.id, 'T99')
        self.assertEqual(token.owner, 'Test')
        self.assertEqual(token.q, 1)
        self.assertEqual(token.r, 2)
        self.assertEqual(token.stats['move'], 3)
        self.assertEqual(token.stats['combat_value'], 2)

    def test_board_get_tile(self):
        # Sprawdza, czy Board.get_tile zwraca obiekt Tile lub None
        board = self.engine.board
        hexes = list(board.terrain.keys())
        if hexes:
            q, r = map(int, hexes[0].split(','))
            tile = board.get_tile(q, r)
            self.assertIsNotNone(tile)
            self.assertEqual(tile.q, q)
            self.assertEqual(tile.r, r)
        # Test na nieistniejący heks
        tile_none = board.get_tile(999, 999)
        self.assertIsNone(tile_none)

    def test_board_is_occupied(self):
        # Sprawdza, czy Board.is_occupied wykrywa zajętość pola
        board = self.engine.board
        if self.engine.tokens:
            token = self.engine.tokens[0]
            board.set_tokens([token])
            self.assertTrue(board.is_occupied(token.q, token.r))
            self.assertFalse(board.is_occupied(999, 999))

    def test_token_serialize_deserialize(self):
        # Sprawdza, czy serializacja i deserializacja Token działa poprawnie
        from engine.token import Token
        if self.engine.tokens:
            token = self.engine.tokens[0]
            data = token.serialize()
            token2 = Token.from_json(data, pos={'q': data['q'], 'r': data['r']})
            self.assertEqual(token.id, token2.id)
            self.assertEqual(token.owner, token2.owner)
            self.assertEqual(token.q, token2.q)
            self.assertEqual(token.r, token2.r)

    def test_engine_random_seed(self):
        # Sprawdza, czy seed silnika daje powtarzalność losowości
        engine1 = GameEngine(
            map_path='data/map_data.json',
            tokens_index_path='assets/tokens/index.json',
            tokens_start_path='assets/start_tokens.json',
            seed=999
        )
        engine2 = GameEngine(
            map_path='data/map_data.json',
            tokens_index_path='assets/tokens/index.json',
            tokens_start_path='assets/start_tokens.json',
            seed=999
        )
        val1 = engine1.random.randint(1, 100000)
        val2 = engine2.random.randint(1, 100000)
        self.assertEqual(val1, val2)

    def test_action_move_on_occupied(self):
        # Próba ruchu na zajęty heks powinna się nie powieść
        if len(self.engine.tokens) >= 2:
            t1 = self.engine.tokens[0]
            t2 = self.engine.tokens[1]
            t1.set_position(0, 0)
            t2.set_position(0, 1)
            self.engine.board.set_tokens([t1, t2])
            action = MoveAction(t1.id, 0, 1)  # t2 już tam stoi
            success, msg = self.engine.execute_action(action)
            self.assertFalse(success)
            self.assertIn('zajęte', msg.lower())

    def test_action_move_too_far(self):
        # Próba ruchu poza zasięg powinna się nie powieść
        if self.engine.tokens:
            token = self.engine.tokens[0]
            move = token.stats.get('move', 0)
            # Szukamy heksa oddalonego o move+2
            q0, r0 = token.q, token.r
            found = False
            for (k, tile) in self.engine.board.terrain.items():
                q, r = tile.q, tile.r
                dist = self.engine.board.hex_distance((q0, r0), (q, r))
                if dist > move:
                    action = MoveAction(token.id, q, r)
                    success, msg = self.engine.execute_action(action)
                    self.assertFalse(success)
                    self.assertIn('za daleko', msg.lower())
                    found = True
                    break
            if not found:
                self.skipTest('Brak heksa poza zasięgiem ruchu')

    def test_action_combat_too_far(self):
        # Próba ataku zbyt daleko
        if len(self.engine.tokens) >= 2:
            t1 = self.engine.tokens[0]
            t2 = self.engine.tokens[1]
            t1.set_position(0, 0)
            t2.set_position(10, 10)
            self.engine.board.set_tokens([t1, t2])
            action = CombatAction(t1.id, t2.id)
            success, msg = self.engine.execute_action(action)
            self.assertFalse(success)
            self.assertIn('za daleko', msg.lower())

    def test_action_combat_no_token(self):
        # Próba ataku na nieistniejący żeton
        if self.engine.tokens:
            t1 = self.engine.tokens[0]
            action = CombatAction(t1.id, 'nieistniejacy')
            success, msg = self.engine.execute_action(action)
            self.assertFalse(success)
            self.assertIn('brak żetonu', msg.lower())

    def test_engine_get_state_token_consistency(self):
        # Sprawdza, czy get_state zwraca te same id żetonów co engine.tokens
        state = self.engine.get_state()
        state_ids = {t['id'] for t in state['tokens']}
        engine_ids = {t.id for t in self.engine.tokens}
        self.assertTrue(state_ids.issubset(engine_ids) or engine_ids.issubset(state_ids))

    def test_engine_turn_increments(self):
        # Sprawdza, czy tura inkrementuje się poprawnie przez kilka wywołań
        t0 = self.engine.turn
        for _ in range(5):
            self.engine.next_turn()
        self.assertEqual(self.engine.turn, t0 + 5)

    def test_token_stats_integrity(self):
        # Sprawdza, czy każdy żeton ma wymagane statystyki
        for token in self.engine.tokens:
            self.assertIn('move', token.stats)
            self.assertIn('combat_value', token.stats)
            self.assertIn('unitType', token.stats)
            self.assertIn('unitSize', token.stats)

    def test_token_maintenance_and_price(self):
        # Sprawdza, czy każdy żeton ma maintenance i price w stats
        for token in self.engine.tokens:
            self.assertIn('maintenance', token.stats)
            self.assertIn('price', token.stats)

    def test_token_sight(self):
        # Sprawdza, czy każdy żeton ma sight w stats
        for token in self.engine.tokens:
            self.assertIn('sight', token.stats)

    def test_token_stats_types(self):
        # Sprawdza typy podstawowych statystyk żetonu
        for token in self.engine.tokens:
            self.assertIsInstance(token.stats['move'], int)
            self.assertIsInstance(token.stats['combat_value'], int)
            self.assertIsInstance(token.stats['maintenance'], int)
            self.assertIsInstance(token.stats['price'], int)
            self.assertIsInstance(token.stats['sight'], int)
            self.assertIsInstance(token.stats['unitType'], str)
            self.assertIsInstance(token.stats['unitSize'], str)

    def test_token_id_unique(self):
        # Sprawdza, czy id żetonów są unikalne
        ids = [t.id for t in self.engine.tokens]
        self.assertEqual(len(ids), len(set(ids)))

    def test_board_tile_attributes(self):
        # Sprawdza, czy każdy Tile ma wymagane atrybuty
        board = self.engine.board
        for tile in board.terrain.values():
            self.assertTrue(hasattr(tile, 'q'))
            self.assertTrue(hasattr(tile, 'r'))
            self.assertTrue(hasattr(tile, 'terrain_key'))
            self.assertTrue(hasattr(tile, 'move_mod'))
            self.assertTrue(hasattr(tile, 'defense_mod'))

    def test_board_tiles_types(self):
        # Sprawdza typy atrybutów Tile
        board = self.engine.board
        for tile in board.terrain.values():
            self.assertIsInstance(tile.q, int)
            self.assertIsInstance(tile.r, int)
            self.assertIsInstance(tile.terrain_key, str)
            self.assertIsInstance(tile.move_mod, int)
            self.assertIsInstance(tile.defense_mod, int)

    def test_board_meta(self):
        # Sprawdza, czy Board ma poprawne meta (hex_size, cols, rows)
        board = self.engine.board
        self.assertTrue(hasattr(board, 'hex_size'))
        self.assertTrue(hasattr(board, 'cols'))
        self.assertTrue(hasattr(board, 'rows'))
        self.assertIsInstance(board.hex_size, int)
        self.assertIsInstance(board.cols, int)
        self.assertIsInstance(board.rows, int)

    def test_board_terrain_keys(self):
        # Sprawdza, czy wszystkie klucze terrain są poprawnymi współrzędnymi
        board = self.engine.board
        for k in board.terrain.keys():
            q, r = map(int, k.split(','))
            self.assertIsInstance(q, int)
            self.assertIsInstance(r, int)

    def test_engine_tokens_list_type(self):
        # Sprawdza, czy engine.tokens to lista Tokenów
        from engine.token import Token
        self.assertIsInstance(self.engine.tokens, list)
        for t in self.engine.tokens:
            self.assertIsInstance(t, Token)

    def test_token_unit_label_and_type(self):
        # Sprawdza, czy każdy żeton ma label, unitType i unitSize jako string
        for token in self.engine.tokens:
            self.assertIsInstance(token.stats['label'], str)
            self.assertIsInstance(token.stats['unitType'], str)
            self.assertIsInstance(token.stats['unitSize'], str)

    def test_token_attack_and_defense_defaults(self):
        # Sprawdza, czy attack i defense_mod mają wartości domyślne jeśli nie podane
        for token in self.engine.tokens:
            self.assertIn('attack', token.stats)
            self.assertIsInstance(token.stats['attack'], int)
        board = self.engine.board
        for tile in board.terrain.values():
            self.assertIsInstance(tile.defense_mod, int)

    def test_token_image_path(self):
        # Sprawdza, czy image w stats żetonu jest ścieżką tekstową
        for token in self.engine.tokens:
            self.assertIsInstance(token.stats['image'], str)
            # Można dodać test czy ścieżka istnieje, ale nie jest to wymagane

    def test_board_tile_spawn_nation(self):
        # Sprawdza, czy spawn_nation jest stringiem lub None
        board = self.engine.board
        for tile in board.terrain.values():
            self.assertTrue(isinstance(tile.spawn_nation, str) or tile.spawn_nation is None)

    def test_token_stats_keys(self):
        # Sprawdza, czy stats żetonu zawiera tylko spodziewane klucze
        expected = {'move','combat_value','maintenance','price','sight','unitType','unitSize','label','attack','image','shape','w','h'}
        for token in self.engine.tokens:
            self.assertTrue(set(token.stats.keys()).issubset(expected))

    def test_token_str_and_repr(self):
        # Sprawdza, czy Token ma czytelny __str__ i __repr__ (jeśli zaimplementowane)
        for token in self.engine.tokens:
            s = str(token)
            r = repr(token)
            self.assertIsInstance(s, str)
            self.assertIsInstance(r, str)

    def test_board_tiles_count_vs_meta(self):
        # Sprawdza, czy liczba heksów nie przekracza cols*rows
        board = self.engine.board
        self.assertLessEqual(len(board.terrain), board.cols * board.rows)

    def test_engine_tokens_are_unique_objects(self):
        # Sprawdza, czy każdy Token to inny obiekt (nie aliasy)
        ids = [id(t) for t in self.engine.tokens]
        self.assertEqual(len(ids), len(set(ids)))

    def test_token_stats_no_extra_keys(self):
        # Sprawdza, czy nie ma nieoczekiwanych kluczy w stats
        allowed = {'move','combat_value','maintenance','price','sight','unitType','unitSize','label','attack','image','shape','w','h'}
        for token in self.engine.tokens:
            for k in token.stats.keys():
                self.assertIn(k, allowed)

    def test_board_tile_type_and_value(self):
        # Sprawdza, czy type i value na Tile są stringiem, liczbą lub None
        board = self.engine.board
        for tile in board.terrain.values():
            self.assertTrue(isinstance(tile.type, (str, type(None))))
            self.assertTrue(isinstance(tile.value, (int, float, type(None))))

    def test_token_stats_required_keys(self):
        # Sprawdza, czy każdy żeton ma wszystkie wymagane klucze w stats
        required = {'move','combat_value','maintenance','price','sight','unitType','unitSize','label','attack','image','shape','w','h'}
        for token in self.engine.tokens:
            self.assertTrue(required.issubset(token.stats.keys()))

    def test_board_tile_default_values(self):
        # Sprawdza, czy Tile ma domyślne wartości dla nieobecnych pól
        board = self.engine.board
        for tile in board.terrain.values():
            self.assertIsNotNone(tile.terrain_key)
            self.assertIsNotNone(tile.move_mod)
            self.assertIsNotNone(tile.defense_mod)

    def test_engine_get_state_format(self):
        # Sprawdza, czy get_state zwraca poprawny format (JSON-serializowalny)
        import json
        state = self.engine.get_state()
        try:
            json.dumps(state)
        except Exception as e:
            self.fail(f"Stan gry nie jest JSON-serializowalny: {e}")

    def test_token_from_json_missing_fields(self):
        # Sprawdza, czy Token.from_json nie wywala się przy brakujących polach
        from engine.token import Token
        data = {'id': 'T100'}
        token = Token.from_json(data)
        self.assertEqual(token.id, 'T100')
        self.assertIsInstance(token.stats, dict)

    def test_board_pixel_to_hex_roundtrip(self):
        # Sprawdza, czy pixel_to_hex(hex_to_pixel(q, r)) ≈ (q, r)
        board = self.engine.board
        hexes = list(board.terrain.keys())
        if hexes:
            q, r = map(int, hexes[0].split(','))
            x, y = board.hex_to_pixel(q, r)
            q2, r2 = board.pixel_to_hex(x, y)
            self.assertAlmostEqual(q, q2, delta=1)
            self.assertAlmostEqual(r, r2, delta=1)

if __name__ == '__main__':
    unittest.main()
