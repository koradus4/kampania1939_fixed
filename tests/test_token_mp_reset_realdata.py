import pytest
from engine.engine import GameEngine
from core.tura import TurnManager
from engine.player import Player
import os
import json

@pytest.mark.integration
def test_token_move_and_mp_reset():
    # Przygotowanie silnika gry na realnych danych
    map_path = "data/map_data.json"
    tokens_index_path = "assets/tokens/index.json"
    tokens_start_path = "assets/start_tokens.json"
    engine = GameEngine(
        map_path=map_path,
        tokens_index_path=tokens_index_path,
        tokens_start_path=tokens_start_path,
        seed=123
    )
    # Zakładamy, że na mapie są żetony i mapa jest poprawna
    assert len(engine.tokens) > 0, "Brak żetonów na mapie!"
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
    # Wykonaj ruch przez execute_action + MoveAction
    from engine.action import MoveAction
    move_action = MoveAction(token.id, dest[0], dest[1])
    result, msg = engine.execute_action(move_action)
    assert result, f"Ruch nie powiódł się: {msg}!"
    assert (token.q, token.r) == dest, "Żeton nie zmienił pozycji!"
    assert token.currentMovePoints < start_mp, "Punkty ruchu nie zostały odjęte!"
    # Symuluj reset tury
    engine.next_turn()  # Resetuje punkty ruchu wszystkich żetonów
    # Punkty ruchu powinny się zresetować
    token_after = next(t for t in engine.tokens if t.id == token.id)
    assert token_after.currentMovePoints == token_after.maxMovePoints, "Punkty ruchu nie zostały zresetowane na nową turę!"
    # (Opcjonalnie) sprawdź, czy po kilku turach reset działa
