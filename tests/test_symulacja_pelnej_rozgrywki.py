import os
import tempfile
import unittest
from engine.save_manager import save_game, load_game
from engine.engine import GameEngine
from engine.player import Player
from core.ekonomia import EconomySystem

class TestSimulationFullGameplay(unittest.TestCase):
    def test_full_gameplay_simulation(self):
        # 1. Inicjalizacja silnika i graczy
        engine = GameEngine(
            map_path="data/map_data.json",
            tokens_index_path="assets/tokens/index.json",
            tokens_start_path="assets/start_tokens.json",
            seed=123
        )
        players = [
            Player(1, "Polska", "Generał", 5),
            Player(2, "Polska", "Dowódca", 5),
            Player(3, "Niemcy", "Generał", 5),
            Player(4, "Niemcy", "Dowódca", 5),
        ]
        for p in players:
            if not hasattr(p, 'economy') or p.economy is None:
                p.economy = EconomySystem()
            p.victory_points = 0
            p.economy.economic_points = 20
            p.economy.special_points = 2
        engine.players = players
        engine.current_player_obj = players[0]
        engine.turn = 1

        # 2. Symulacja ruchu żetonu (jeśli są żetony na mapie)
        if engine.tokens:
            token = engine.tokens[0]
            start_pos = (token.q, token.r)
            # Spróbuj przesunąć żeton o 1 pole (jeśli możliwe)
            if hasattr(engine.board, 'neighbors'):
                neighbors = engine.board.neighbors(token.q, token.r)
                if neighbors:
                    dest_q, dest_r = neighbors[0]
                    token.set_position(dest_q, dest_r)
                    token.currentMovePoints -= 1
            self.assertNotEqual((token.q, token.r), start_pos, "Żeton nie został przesunięty!")

        # 3. Symulacja walki i przyznania VP
        if len(engine.tokens) > 1:
            attacker = engine.tokens[0]
            defender = engine.tokens[1]
            # Prosta symulacja eliminacji
            defender_id = defender.id
            engine.tokens.remove(defender)
            players[0].victory_points += 5
            players[0].vp_history.append({"turn": engine.turn, "amount": 5, "reason": "eliminacja", "token_id": defender_id, "enemy": defender.owner if hasattr(defender, 'owner') else "?"})
            self.assertNotIn(defender, engine.tokens, "Obrońca nie został usunięty!")
            self.assertEqual(players[0].victory_points, 5, "Nie przyznano VP za eliminację!")

        # 4. Symulacja przydziału i wydania punktów ekonomicznych
        players[0].economy.economic_points -= 3
        self.assertEqual(players[0].economy.economic_points, 17, "Nieprawidłowy stan punktów ekonomicznych po wydaniu!")

        # 5. Zmiana tury i aktywnego gracza
        engine.turn += 1
        engine.current_player_obj = players[1]
        self.assertEqual(engine.turn, 2, "Numer tury nie został zaktualizowany!")
        self.assertEqual(engine.current_player_obj, players[1], "Nie zmieniono aktywnego gracza!")

        # 6. Save/Load w trakcie rozgrywki
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            save_path = tmp.name
        save_game(save_path, engine, active_player=engine.current_player_obj)
        # Nowy silnik
        engine2 = GameEngine(
            map_path="data/map_data.json",
            tokens_index_path="assets/tokens/index.json",
            tokens_start_path="assets/start_tokens.json",
            seed=123
        )
        players2 = [
            Player(1, "Polska", "Generał", 5),
            Player(2, "Polska", "Dowódca", 5),
            Player(3, "Niemcy", "Generał", 5),
            Player(4, "Niemcy", "Dowódca", 5),
        ]
        for p in players2:
            if not hasattr(p, 'economy') or p.economy is None:
                p.economy = EconomySystem()
        engine2.players = players2
        engine2.current_player_obj = players2[1]
        engine2.turn = 0
        load_game(save_path, engine2)
        os.remove(save_path)
        # Sprawdź integralność po wczytaniu
        self.assertEqual(engine2.turn, 2, "Numer tury nie zgadza się po wczytaniu!")
        self.assertEqual(engine2.current_player_obj.id, players[1].id, "Aktywny gracz nie zgadza się po wczytaniu!")
        # Sprawdzamy stan gracza z engine2.players, a nie players2!
        gracz_po = next((p for p in engine2.players if p.id == 1), None)
        self.assertIsNotNone(gracz_po, "Nie znaleziono gracza o id=1 po wczytaniu!")
        self.assertEqual(gracz_po.victory_points, 5, "VP nie zgadza się po wczytaniu!")
        self.assertEqual(gracz_po.economy.economic_points, 17, "Punkty ekonomiczne nie zgadzają się po wczytaniu!")
        # Sprawdź historię VP
        self.assertTrue(any(vp['amount'] == 5 for vp in gracz_po.vp_history), "Historia VP nie została zachowana!")

if __name__ == "__main__":
    unittest.main()
