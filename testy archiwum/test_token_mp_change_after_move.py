import pytest
from engine.engine import GameEngine
from engine.action import MoveAction

@pytest.mark.integration
def test_token_move_points_are_modified():
    """Testuje czy po ruchu żetonu zmieniają się jego punkty ruchu (currentMovePoints)."""
    engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=123
    )
    # Wybierz żeton z punktami ruchu > 0
    token = next((t for t in engine.tokens if t.currentMovePoints > 0), None)
    assert token is not None, "Brak żetonu z punktami ruchu!"
    start_mp = token.currentMovePoints
    start_pos = (token.q, token.r)
    # Znajdź sąsiednie pole, na które można się ruszyć
    neighbors = engine.board.neighbors(*start_pos)
    dest = None
    for n in neighbors:
        tile = engine.board.get_tile(*n)
        if tile and tile.move_mod >= 0 and not engine.board.is_occupied(*n):
            dest = n
            break
    assert dest is not None, "Brak dostępnego sąsiedniego pola do ruchu!"
    # Wykonaj ruch
    move_action = MoveAction(token.id, dest[0], dest[1])
    result, msg = engine.execute_action(move_action)
    assert result, f"Ruch nie powiódł się: {msg}!"
    # Sprawdź, czy punkty ruchu się zmieniły
    assert token.currentMovePoints < start_mp, f"Punkty ruchu nie zostały zmodyfikowane po ruchu! (było: {start_mp}, jest: {token.currentMovePoints})"
