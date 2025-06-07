import os
import tempfile
import unittest
from engine.save_manager import save_game, load_game
from engine.engine import GameEngine
from engine.player import Player
from core.ekonomia import EconomySystem

class TestGameFullIntegrity(unittest.TestCase):
    def test_game_full_integrity(self):
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
            p.victory_points = 100 * p.id
            p.economy.economic_points = 10 * p.id
            p.economy.special_points = p.id
            p.visible_tokens = {f"T{p.id}"}
            p.visible_hexes = {(p.id, p.id)}
            p.temp_visible_tokens = {f"TT{p.id}"}
            p.temp_visible_hexes = {(p.id+1, p.id+1)}
            p.vp_history = [
                {"turn": 1, "amount": 10 * p.id, "reason": "eliminacja", "token_id": f"T{p.id}", "enemy": "Niemcy"}
            ]
        engine.players = players
        engine.current_player_obj = players[2]
        engine.turn = 7

        tokens_before = [(t.id, getattr(t, 'q', None), getattr(t, 'r', None), getattr(t, 'currentMovePoints', None), getattr(t, 'currentFuel', None), getattr(t, 'combat_value', None)) for t in engine.tokens]
        players_before = [
            (p.id, p.nation, p.role, getattr(p, 'victory_points', 0),
             getattr(p, 'economy', None).economic_points if getattr(p, 'economy', None) else 0,
             getattr(p, 'economy', None).special_points if getattr(p, 'economy', None) else 0,
             set(getattr(p, 'visible_tokens', set())),
             set(getattr(p, 'temp_visible_tokens', set())),
             set(getattr(p, 'visible_hexes', set())),
             set(getattr(p, 'temp_visible_hexes', set())),
             list(getattr(p, 'vp_history', []))
            ) for p in engine.players]
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
        engine2.current_player_obj = players2[2]
        engine2.turn = 1  # zostanie nadpisane przez load_game

        load_game(save_path, engine2)
        os.remove(save_path)

        # 4. Sprawdź żetony
        tokens_after = [(t.id, getattr(t, 'q', None), getattr(t, 'r', None), getattr(t, 'currentMovePoints', None), getattr(t, 'currentFuel', None), getattr(t, 'combat_value', None)) for t in engine2.tokens]
        self.assertEqual(tokens_before, tokens_after, "Stan żetonów nie zgadza się po wczytaniu!")

        # 5. Sprawdź graczy (pełny stan)
        players_after = [
            (p.id, p.nation, p.role, getattr(p, 'victory_points', 0),
             getattr(p, 'economy', None).economic_points if getattr(p, 'economy', None) else 0,
             getattr(p, 'economy', None).special_points if getattr(p, 'economy', None) else 0,
             set(getattr(p, 'visible_tokens', set())),
             set(getattr(p, 'temp_visible_tokens', set())),
             set(getattr(p, 'visible_hexes', set())),
             set(getattr(p, 'temp_visible_hexes', set())),
             list(getattr(p, 'vp_history', []))
            ) for p in engine2.players]
        if players_before != players_after:
            print("\n--- RÓŻNICE W STANIE GRACZY PO WCZYTANIU ---")
            for i, (pb, pa) in enumerate(zip(players_before, players_after)):
                if pb != pa:
                    print(f"Gracz {i+1} (id={pb[0]}):")
                    for idx, (b, a) in enumerate(zip(pb, pa)):
                        if b != a:
                            print(f"  Pole {idx}: przed={b!r}, po={a!r}")
            print("--- KONIEC RÓŻNIC ---\n")
        self.assertEqual(players_before, players_after, "Stan graczy (pełny) nie zgadza się po wczytaniu!")

        # 6. Sprawdź turę i aktywnego gracza
        self.assertEqual(getattr(engine2, 'turn', 1), turn_before, "Numer tury nie zgadza się po wczytaniu!")
        self.assertEqual(getattr(engine2, 'current_player_obj', engine2.players[2]).id, current_player_id, "Aktywny gracz nie zgadza się po wczytaniu!")

        print("Test GAME FULL: save/load integralność WSZYSTKIEGO OK!")
