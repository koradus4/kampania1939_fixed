import pytest
from engine.engine import GameEngine
from engine.action import MoveAction

@pytest.fixture
def game_engine():
    return GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=123
    )

def test_block_move_to_move_mod_minus1(game_engine):
    # Znajdź dowolny żeton i pole z move_mod == -1
    token = next(t for t in game_engine.tokens if hasattr(t, 'q') and hasattr(t, 'r'))
    # Szukamy pola nieprzekraczalnego na mapie
    found = False
    for tile in game_engine.board.terrain.values():
        if tile.move_mod == -1:
            dest_q, dest_r = tile.q, tile.r
            found = True
            break
    assert found, "Brak pola z move_mod == -1 na mapie testowej!"
    # Próbujemy wykonać ruch na to pole
    action = MoveAction(token.id, dest_q, dest_r)
    success, msg = action.execute(game_engine)
    assert not success, f"Ruch na pole z move_mod == -1 powinien być zablokowany! Komunikat: {msg}"
    assert "move_mod" in msg or "nieprzekraczalne" in msg
