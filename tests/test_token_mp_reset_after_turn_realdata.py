import pytest
from engine.engine import GameEngine
from core.tura import TurnManager
from engine.player import Player

@pytest.mark.integration
def test_token_mp_reset_after_turn_realdata():
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
    # Wykonaj ruch (odejmie punkty ruchu)
    from engine.action import MoveAction
    start_pos = (token.q, token.r)
    neighbors = engine.board.neighbors(*start_pos)
    dest = None
    for n in neighbors:
        tile = engine.board.get_tile(*n)
        if tile and tile.move_mod >= 0 and not engine.board.is_occupied(*n):
            dest = n
            break
    assert dest is not None, "Brak dostępnego sąsiedniego pola do ruchu!"
    move_action = MoveAction(token.id, dest[0], dest[1])
    result, msg = engine.execute_action(move_action)
    assert result, f"Ruch nie powiódł się: {msg}!"
    assert token.currentMovePoints < start_mp, "Punkty ruchu nie zostały odjęte!"
    # Symuluj przejście pełnej tury przez TurnManager (dla wszystkich graczy)
    players = [Player(1, "Polska", "Generał", 5, ""), Player(2, "Polska", "Dowódca", 5, "")]
    turn_manager = TurnManager(players, game_engine=engine)
    for _ in range(len(players)):
        turn_manager.next_turn()  # przejście przez wszystkich graczy
    token_after = next(t for t in engine.tokens if t.id == token.id)
    assert token_after.currentMovePoints == token_after.maxMovePoints, "Punkty ruchu nie zostały zresetowane po pełnej turze przez TurnManager!"
