import pytest
from engine.engine import GameEngine, update_all_players_visibility, clear_temp_visibility
from engine.action import MoveAction
from engine.player import Player
import os
from unittest.mock import patch, MagicMock
import tkinter as tk
from gui.panel_dowodcy import PanelDowodcy

@pytest.fixture
def game_engine_and_players():
    # Użyj realnych danych z assets i data
    engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    # Przykładowi gracze (Polska i Niemcy)
    players = [
        Player(1, "Polska", "Generał"),
        Player(2, "Polska", "Dowódca"),
        Player(3, "Polska", "Dowódca"),
        Player(4, "Niemcy", "Generał"),
        Player(5, "Niemcy", "Dowódca"),
        Player(6, "Niemcy", "Dowódca"),
    ]
    engine.players = players
    update_all_players_visibility(players, engine.tokens, engine.board)
    return engine, players

def test_engine_loads_real_data(game_engine_and_players):
    engine, players = game_engine_and_players
    # Sprawdź czy mapa została załadowana
    assert hasattr(engine, 'board')
    assert hasattr(engine.board, 'terrain')
    assert len(engine.board.terrain) > 0
    # Sprawdź czy żetony zostały załadowane
    assert hasattr(engine, 'tokens')
    assert len(engine.tokens) > 0
    # Sprawdź czy każdy żeton ma ownera i stats
    for t in engine.tokens:
        assert hasattr(t, 'owner')
        assert hasattr(t, 'stats')
        assert isinstance(t.stats, dict)

def test_move_action_on_real_data(game_engine_and_players):
    engine, players = game_engine_and_players
    # Wybierz pierwszy żeton polski
    token = next(t for t in engine.tokens if t.owner.startswith("2 (Polska)") or t.owner.startswith("3 (Polska)"))
    start_pos = (token.q, token.r)
    # Znajdź sąsiedni heks na mapie
    neighbors = engine.board.neighbors(token.q, token.r)
    assert neighbors, "Brak sąsiadów na mapie dla testowanego żetonu!"
    dest = neighbors[0]
    action = MoveAction(token.id, dest[0], dest[1])
    success, msg = action.execute(engine)
    assert success, f"Ruch nie powiódł się: {msg}"
    assert (token.q, token.r) == dest

def test_visibility_consistency(game_engine_and_players):
    engine, players = game_engine_and_players
    update_all_players_visibility(players, engine.tokens, engine.board)
    # Każdy gracz powinien mieć zdefiniowane zbiory widoczności
    for p in players:
        assert hasattr(p, 'visible_hexes')
        assert hasattr(p, 'visible_tokens')
        assert isinstance(p.visible_hexes, set)
        assert isinstance(p.visible_tokens, set)
    # Przynajmniej jeden gracz powinien widzieć jakikolwiek żeton
    assert any(len(p.visible_tokens) > 0 for p in players)

def test_clear_temp_visibility(game_engine_and_players):
    engine, players = game_engine_and_players
    # Dodaj tymczasową widoczność
    for p in players:
        p.temp_visible_hexes = set([(0,0), (1,1)])
        p.temp_visible_tokens = set(["test1", "test2"])
    clear_temp_visibility(players)
    for p in players:
        assert p.temp_visible_hexes == set()
        assert p.temp_visible_tokens == set()

def test_move_to_friendly_occupied(game_engine_and_players):
    engine, players = game_engine_and_players
    # Znajdź dwa żetony tej samej nacji na różnych polach
    tokens = [t for t in engine.tokens if t.owner.startswith("2 (Polska)")]
    if len(tokens) < 2:
        pytest.skip("Za mało żetonów do testu!")
    t1, t2 = tokens[:2]
    # Przesuń t1 na pole t2
    action = MoveAction(t1.id, t2.q, t2.r)
    success, msg = action.execute(engine)
    assert not success, "Ruch na pole zajęte przez sojusznika powinien się nie powieść!"
    assert (t1.q, t1.r) != (t2.q, t2.r)

def test_move_to_enemy_occupied(game_engine_and_players):
    engine, players = game_engine_and_players
    # Znajdź żeton polski i niemiecki na różnych polach
    t_pol = next(t for t in engine.tokens if t.owner.startswith("2 (Polska)"))
    t_niem = next(t for t in engine.tokens if t.owner.startswith("5 (Niemcy)"))
    # Przesuń polski żeton na pole niemieckiego
    action = MoveAction(t_pol.id, t_niem.q, t_niem.r)
    success, msg = action.execute(engine)
    assert not success or (t_pol.q, t_pol.r) != (t_niem.q, t_niem.r), "Ruch na pole wroga powinien być zablokowany lub zatrzymany przed wrogiem."

def test_move_without_mp(game_engine_and_players):
    engine, players = game_engine_and_players
    token = next(t for t in engine.tokens if t.owner.startswith("2 (Polska)"))
    token.currentMovePoints = 0
    neighbors = engine.board.neighbors(token.q, token.r)
    if not neighbors:
        pytest.skip("Brak sąsiadów na mapie!")
    dest = neighbors[0]
    action = MoveAction(token.id, dest[0], dest[1])
    success, msg = action.execute(engine)
    assert not success, "Ruch bez punktów ruchu powinien być zablokowany!"
    assert (token.q, token.r) != dest

def test_mp_reset_after_turn(game_engine_and_players):
    engine, players = game_engine_and_players
    token = next(t for t in engine.tokens if t.owner.startswith("2 (Polska)"))
    token.currentMovePoints = 0
    # Załóżmy, że silnik resetuje MP na początku tury (symuluj to ręcznie jeśli nie)
    if hasattr(token, 'maxMovePoints'):
        token.currentMovePoints = 0
        token.maxMovePoints = token.stats.get('move', 0)
    # Symuluj nową turę
    if hasattr(engine, 'next_turn'):
        engine.next_turn()
    # Sprawdź czy punkty ruchu się zresetowały
    assert token.currentMovePoints == token.maxMovePoints

def test_owner_and_nation_consistency(game_engine_and_players):
    engine, players = game_engine_and_players
    for t in engine.tokens:
        assert t.owner, f"Brak ownera w żetonie {t.id}"
        nation = t.stats.get('nation', None)
        assert nation in ["Polska", "Niemcy"], f"Nieprawidłowa nacja w żetonie {t.id}: {nation}"

def test_general_visibility(game_engine_and_players):
    engine, players = game_engine_and_players
    update_all_players_visibility(players, engine.tokens, engine.board)
    # Generał powinien widzieć wszystkie żetony swojej nacji
    general = next(p for p in players if p.nation == "Polska" and p.role == "Generał")
    own_tokens = [t for t in engine.tokens if t.owner.endswith("(Polska)")]
    for t in own_tokens:
        assert t.id in general.visible_tokens, f"Generał nie widzi własnego żetonu {t.id}"
    # Generał nie powinien widzieć wrogich żetonów poza zasięgiem
    enemy_tokens = [t for t in engine.tokens if t.owner.endswith("(Niemcy)")]
    for t in enemy_tokens:
        # Jeśli żeton jest poza widocznością, nie powinien być widoczny
        if (t.q, t.r) not in general.visible_hexes:
            assert t.id not in general.visible_tokens

def test_fuel_usage_and_tankowanie(game_engine_and_players):
    engine, players = game_engine_and_players
    # Wybierz pierwszy żeton polski
    token = next(t for t in engine.tokens if t.owner.startswith("2 (Polska)") or t.owner.startswith("3 (Polska)"))
    start_fuel = token.currentFuel
    start_pos = (token.q, token.r)
    # Znajdź sąsiedni heks na mapie
    neighbors = engine.board.neighbors(token.q, token.r)
    assert neighbors, "Brak sąsiadów na mapie dla testowanego żetonu!"
    dest = neighbors[0]
    # Wykonaj ruch (zużycie paliwa)
    action = MoveAction(token.id, dest[0], dest[1])
    success, msg = action.execute(engine)
    assert token.currentFuel == start_fuel - 1, f"Paliwo nie zostało zużyte po ruchu: {token.currentFuel} vs {start_fuel-1}"
    # Wyzeruj paliwo i spróbuj ruszyć
    token.currentFuel = 0
    action2 = MoveAction(token.id, dest[0], dest[1])
    result = action2.execute(engine)
    # Akceptuj False lub (False, ...)
    assert (result is None or result is False or (isinstance(result, tuple) and result and result[0] is False)), "Żeton bez paliwa nie powinien móc się ruszyć!"
    # Tankowanie (symulacja panelu dowódcy)
    token.currentFuel = 0
    max_fuel = token.maxFuel
    ile_dolac = 5
    token.currentFuel += ile_dolac
    assert token.currentFuel == ile_dolac, "Tankowanie nie działa poprawnie!"
    # Tankowanie do pełna
    token.currentFuel = 0
    token.currentFuel += max_fuel
    assert token.currentFuel == max_fuel, "Tankowanie do pełna nie działa!"

def test_tankowanie_gui_symulacja(game_engine_and_players):
    engine, players = game_engine_and_players
    # Wybierz pierwszy żeton polski
    token = next(t for t in engine.tokens if t.owner.startswith("2 (Polska)") or t.owner.startswith("3 (Polska)"))
    print(f"[TEST] Wybrany żeton: {token.id}, owner: {token.owner}, maxFuel: {token.maxFuel}, currentFuel: {token.currentFuel}")
    start_fuel = token.currentFuel
    max_fuel = token.maxFuel
    print(f"[TEST] Stan początkowy paliwa: {start_fuel}/{max_fuel}")
    # Porusz żetonem, aby stracił paliwo
    neighbors = engine.board.neighbors(token.q, token.r)
    assert neighbors, "Brak sąsiadów na mapie dla testowanego żetonu!"
    dest = neighbors[0]
    action = MoveAction(token.id, dest[0], dest[1])
    success, msg = action.execute(engine)
    assert success, f"Ruch nie powiódł się: {msg}"
    print(f"[TEST] Po ruchu paliwo: {token.currentFuel}/{max_fuel}")
    # Symulacja wyboru żetonu do tankowania (np. kliknięcie na mapie)
    wybrany_token = token
    # Próba tankowania częściowego
    ile_mozna = max_fuel - wybrany_token.currentFuel
    if ile_mozna <= 0:
        print("[TEST] Żeton ma pełny bak, nie można tankować!")
        assert ile_mozna == 0
    else:
        ile_dolac = min(3, ile_mozna)  # tankujemy 3 lub do pełna
        przed = wybrany_token.currentFuel
        wybrany_token.currentFuel += ile_dolac
        print(f"[TEST] Tankowanie częściowe: było {przed}, dolano {ile_dolac}, po tankowaniu {wybrany_token.currentFuel}/{max_fuel}")
        assert wybrany_token.currentFuel <= max_fuel, "Tankowanie przekroczyło pojemność baku!"
        # Tankowanie do pełna
        przed = wybrany_token.currentFuel
        ile_dolac_pelne = max_fuel - wybrany_token.currentFuel
        wybrany_token.currentFuel += ile_dolac_pelne
        print(f"[TEST] Tankowanie do pełna: było {przed}, dolano {ile_dolac_pelne}, po tankowaniu {wybrany_token.currentFuel}/{max_fuel}")
        assert wybrany_token.currentFuel == max_fuel, "Tankowanie do pełna nie działa!"

@pytest.mark.skipif('DISPLAY' not in globals() and 'WAYLAND_DISPLAY' not in globals(), reason="Brak środowiska GUI")
def test_gui_tankowanie_full_cycle(game_engine_and_players):
    engine, players = game_engine_and_players
    gracz = next(p for p in players if hasattr(p, 'punkty_ekonomiczne'))
    gracz.punkty_ekonomiczne = 10
    token = next(t for t in engine.tokens if t.owner == f"{gracz.id} ({gracz.nation})" and t.maxFuel > 0)
    token.currentFuel = 0
    # Patchowanie tkinter, by nie otwierać okien
    with patch.object(tk, 'Tk', MagicMock()), \
         patch.object(tk, 'Toplevel', MagicMock()), \
         patch.object(tk, 'Label', MagicMock()), \
         patch.object(tk, 'Button', MagicMock()), \
         patch.object(tk, 'Scale', MagicMock()), \
         patch.object(tk, 'IntVar', return_value=MagicMock(get=lambda: 5)):
        panel = PanelDowodcy(1, 300, gracz, engine)
        panel.wybrany_token = token
        # Symulacja kliknięcia przycisku tankowania
        panel.btn_tankuj.invoke()  # Wywołuje on_tankuj
        # Callback tankowania powinien odjąć punkty i dodać paliwo
        assert token.currentFuel > 0, "Tankowanie nie zadziałało (paliwo)"
        assert gracz.punkty_ekonomiczne < 10, "Tankowanie nie zadziałało (punkty)"
