import pytest
from engine.engine import GameEngine
from engine.action import MoveAction

@pytest.mark.integration
def test_token_move_mod_realdata():
    """Testuje czy ruch żetonu na realnej mapie odejmuje MP zgodnie z move_mod terenu (dłuższa trasa)."""
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
    # Znajdź trasę o długości co najmniej 3 pól (4 punkty: start + 3 kolejne)
    found_path = None
    for n1 in engine.board.neighbors(*start_pos):
        tile1 = engine.board.get_tile(*n1)
        if not tile1 or tile1.move_mod < 0 or engine.board.is_occupied(*n1):
            continue
        for n2 in engine.board.neighbors(*n1):
            tile2 = engine.board.get_tile(*n2)
            if not tile2 or tile2.move_mod < 0 or engine.board.is_occupied(*n2) or n2 == start_pos:
                continue
            for n3 in engine.board.neighbors(*n2):
                tile3 = engine.board.get_tile(*n3)
                if not tile3 or tile3.move_mod < 0 or engine.board.is_occupied(*n3) or n3 in (start_pos, n1):
                    continue
                found_path = [start_pos, n1, n2, n3]
                break
            if found_path:
                break
        if found_path:
            break
    assert found_path is not None, "Brak dostępnej trasy o długości 3 pól!"
    dest = found_path[-1]
    print(f"START: pozycja {start_pos}, MP = {start_mp}")
    # Wyznacz koszt trasy i wypisz debugi
    path_cost = 0
    mp_before = start_mp
    for i, step in enumerate(found_path[1:], 1):
        tile = engine.board.get_tile(*step)
        cost = max(1, tile.move_mod)
        print(f"KROK {i}: przechodzę na pole {step} (terrain: {tile.terrain_key}) | MP przed = {mp_before}, move_mod = {tile.move_mod}, odjęto = {cost}")
        path_cost += cost
        mp_before -= cost
    print(f"SUMA kosztów ruchu: {path_cost}")
    # Wykonaj ruch
    move_action = MoveAction(token.id, dest[0], dest[1])
    result, msg = engine.execute_action(move_action)
    print(f"PO RUCHU: pozycja {token.q, token.r}, MP = {token.currentMovePoints}")
    assert result, f"Ruch nie powiódł się: {msg}!"
    # Sprawdź, czy punkty ruchu odjęto zgodnie z sumą move_mod na trasie
    assert token.currentMovePoints == start_mp - path_cost, (
        f"MP po ruchu nie zgadza się z sumą move_mod! Było: {start_mp}, powinno być: {start_mp - path_cost}, jest: {token.currentMovePoints}, koszt trasy: {path_cost}, trasa: {found_path}")
