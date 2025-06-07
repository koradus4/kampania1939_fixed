# test_token_move_mod.py
# Sprawdza, czy modyfikatory ruchu (np. przez las, rzekę) działają poprawnie
from engine.board import Board
from engine.token import Token
from engine.action import MoveAction
from engine.player import Player
from engine.engine import GameEngine, update_all_players_visibility
import os

def test_move_mod_cost():
    # Przygotuj planszę z 3 heksami o różnych kosztach ruchu
    map_data = {
        "meta": {"hex_size": 40, "cols": 3, "rows": 1},
        "terrain": {
            "0,0": {"terrain_key": "pole", "move_mod": 0, "defense_mod": 0},
            "1,0": {"terrain_key": "rzeka", "move_mod": 2, "defense_mod": 1},
            "2,0": {"terrain_key": "las", "move_mod": 3, "defense_mod": 2}
        }
    }
    # Zapisz tymczasowy plik mapy
    map_path = "test_map.json"
    import json
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(map_data, f)
    # Stwórz silnik gry
    engine = GameEngine(map_path, tokens_index_path="assets/tokens/index.json", tokens_start_path="assets/start_tokens.json")
    # Stwórz żeton z 10 MP
    stats = {"move": 10, "combat_value": 5, "maintenance": 10, "sight": 1, "nation": "Polska"}
    token = Token(id="T1", owner="1 (Polska)", stats=stats, q=0, r=0)
    engine.tokens = [token]
    engine.board.set_tokens(engine.tokens)
    # Stwórz gracza
    player = Player(1, "Polska", "Dowódca")
    engine.players = [player]
    update_all_players_visibility(engine.players, engine.tokens, engine.board)
    # Ruch: z (0,0) na (2,0) przez (1,0)
    action = MoveAction(token.id, 2, 0)
    success, msg = action.execute(engine)
    # Koszt powinien wynosić: (0,0)->(1,0): move_mod=2, (1,0)->(2,0): move_mod=3, razem 2+3=5
    # Ale zawsze minimum 1 na pole, więc (0,0)->(1,0): max(1,2)=2, (1,0)->(2,0): max(1,3)=3
    # Razem 2+3=5
    assert success, f"Ruch nie powiódł się: {msg}"
    assert token.q == 2 and token.r == 0, f"Żeton nie dotarł na pole docelowe: ({token.q},{token.r})"
    assert token.currentMovePoints == 5, f"Pozostałe MP powinny wynosić 5, jest {token.currentMovePoints}"
    # Sprzątanie
    os.remove(map_path)

if __name__ == "__main__":
    test_move_mod_cost()
    print("Test przeszedł pomyślnie!")
