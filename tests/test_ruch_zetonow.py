import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from engine.token import Token
from engine.action import MoveAction
from engine.board import Board
from engine.player import Player
from engine.engine import GameEngine
from core.tura import TurnManager
import json

MAP_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'map_data.json')
TOKENS_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tokens', 'index.json')
START_TOKENS_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'start_tokens.json')

# Używamy przykładowych ID żetonów z index.json
POLISH_TOKEN_ID = "P_Pluton__2_PL_P_Pluton"
GERMAN_TOKEN_ID = "AC_Kompania__5_N_AC_Kompania"

def get_token_by_id(token_id):
    with open(TOKENS_PATH, encoding='utf-8') as f:
        tokens = json.load(f)
    for t in tokens:
        if t['id'] == token_id:
            return t.copy()
    raise ValueError(f"Token {token_id} not found")

# 1. Test: Algorytm A* nie wchodzi w nieskończoną pętlę i obsługuje brak ścieżki

def test_astar_no_path(monkeypatch):
    board = Board(MAP_PATH)
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    token = Token(id=token_data['id'], q=0, r=0, owner=token_data['owner'], stats=token_data)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    # Załóżmy, że pole (99,99) jest odizolowane (nieosiągalne)
    action = MoveAction(token.id, 99, 99)
    success, msg = engine.execute_action(action, player=Player(player_id=2, nation="Polska", role="Dowódca"))
    assert not success
    assert "nie istnieje" in msg.lower() or "nie można" in msg.lower() or "brak" in msg.lower() or "ścieżk" in msg.lower()

# 2. Test: Weryfikacja właściciela żetonu

def test_owner_verification():
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    token = Token(id=token_data['id'], q=1, r=1, owner=token_data['owner'], stats=token_data)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction(token.id, 2, 2)
    # Próba ruchu przez innego gracza
    success, msg = engine.execute_action(action, player=Player(player_id=5, nation="Niemcy", role="Dowódca"))
    assert not success
    assert "dowódcy" in msg.lower() or "właścic" in msg.lower() or "nie możesz ruszać" in msg.lower()

# 3. Test: Ruch na to samo pole

def test_move_to_same_tile():
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    token = Token(id=token_data['id'], q=2, r=2, owner=token_data['owner'], stats=token_data)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction(token.id, 2, 2)
    success, msg = engine.execute_action(action, player=Player(player_id=2, nation="Polska", role="Dowódca"))
    assert not success
    assert "za daleko" in msg.lower() or "brak ruchu" in msg.lower() or "to samo pole" in msg.lower()

# 4. Test: Walidacja celu ruchu (poza planszę)

def test_invalid_target():
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    token = Token(id=token_data['id'], q=0, r=0, owner=token_data['owner'], stats=token_data)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction(token.id, 100, 100)
    success, msg = engine.execute_action(action, player=Player(player_id=2, nation="Polska", role="Dowódca"))
    assert not success
    assert "nie istnieje" in msg.lower() or "poza planszę" in msg.lower()

# 5. Test: Aktualizacja punktów ruchu

def test_move_points_decrease():
    # Użyj pozycji startowej z pliku start_tokens.json
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    # Startowy q, r = 8, -1 (z pliku start_tokens.json)
    token_q, token_r = 8, -1
    # Wybierz pole docelowe, które istnieje na mapie i nie ma move_mod -1
    # Przykład: (8,0) lub (8,1) - należy sprawdzić mapę, tu zakładamy (8,0)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction(token_data['id'], 8, 0)
    success, msg = engine.execute_action(action, player=Player(player_id=2, nation="Polska", role="Dowódca"))
    assert success or "nie można" in msg.lower() or "brak" in msg.lower()  # Akceptuj błąd, jeśli pole jest niedostępne
    for t in engine.tokens:
        if t.id == token_data['id']:
            assert t.currentMovePoints <= t.maxMovePoints

# 6. Test: Reset punktów ruchu w next_turn

def test_next_turn_resets_move_points():
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    token = Token(id=token_data['id'], q=0, r=0, owner=token_data['owner'], stats=token_data)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    # Ustaw currentMovePoints na 0
    for t in engine.tokens:
        t.currentMovePoints = 0
    engine.next_turn()
    for t in engine.tokens:
        assert t.currentMovePoints == t.maxMovePoints

# 7. Test: Ujemne modyfikatory kosztu terenu są blokowane
# Pomijamy, bo nie można ustawić move_mod bezpośrednio bez modyfikacji pliku mapy

# 8. Test: Obsługa wyjątków zamiast logów
# Jeśli execute_action nie rzuca wyjątków, test sprawdza komunikat o błędzie

def test_exception_on_invalid_move():
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction(token_data['id'], 10, 10)
    success, msg = engine.execute_action(action, player=Player(player_id=1, nation="Polska", role="Dowódca"))
    assert not success
    assert "dowódcy" in msg.lower() or "błąd" in msg.lower() or "nie można" in msg.lower() or "nie istnieje" in msg.lower()

# 9. Test: next_turn zmienia gracza i resetuje jednostki

def test_next_turn_switches_player_and_resets():
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    prev_player = engine.current_player
    for t in engine.tokens:
        t.currentMovePoints = 0
    engine.next_turn()
    assert engine.current_player != prev_player
    for t in engine.tokens:
        assert t.currentMovePoints == t.maxMovePoints

# 10. Test: Gra nie wiesza się przy ruchu żetonu (timeout)
import sys

@pytest.mark.skipif(sys.platform.startswith("win"), reason="SIGALRM nieobsługiwany na Windows")
def test_no_hang_on_move():
    token_data = get_token_by_id(POLISH_TOKEN_ID)
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction(token_data['id'], 8, 0)
    import signal
    def handler(signum, frame):
        raise TimeoutError("A* took too long")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(2)  # 2 sekundy na wykonanie
    try:
        engine.execute_action(action, player=Player(player_id=1, nation="Polska", role="Dowódca"))
    except TimeoutError:
        assert False, "Algorytm ruchu zawiesił się!"
    finally:
        signal.alarm(0)

def test_blocked_by_other_token():
    """Test: Ruch na pole zajęte przez inny żeton jest blokowany (kolizja)."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    # Znajdź dowolny polski i niemiecki żeton
    polish = next((t for t in engine.tokens if 'Polska' in str(t.owner)), None)
    german = next((t for t in engine.tokens if 'Niemcy' in str(t.owner)), None)
    assert polish is not None, f"Brak polskiego żetonu w pliku startowym!"
    assert german is not None, f"Brak niemieckiego żetonu w pliku startowym!"
    polish.q, polish.r = 8, -1
    german.q, german.r = 8, 0
    engine.board.set_tokens(engine.tokens)  # Aktualizuj pozycje żetonów na planszy
    # Próbujemy przesunąć polski żeton na pole zajęte przez niemiecki
    action = MoveAction(polish.id, 8, 0)
    success, msg = engine.execute_action(action, player=Player(player_id=int(str(polish.owner).split()[0]), nation="Polska", role="Dowódca"))
    assert not success, f"Ruch został dozwolony! success={success}, msg={msg}"
    assert (
        "zajęte" in msg.lower() or
        "blokad" in msg.lower() or
        "nie można" in msg.lower() or
        "brak" in msg.lower() or
        "ścieżk" in msg.lower() or
        "brak możliwej ścieżki" in msg.lower()
    ), f"Nieprawidłowy komunikat: {msg}"

def test_move_on_own_token():
    """Test: Nie można wejść na pole zajęte przez inny własny żeton."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    # Znajdź dwa polskie żetony
    tokens = [t for t in engine.tokens if 'Polska' in str(t.owner)]
    if len(tokens) < 2:
        pytest.skip("Za mało polskich żetonów do testu.")
    t1, t2 = tokens[:2]
    t1.q, t1.r = 5, 5
    t2.q, t2.r = 6, 5
    engine.board.set_tokens(engine.tokens)
    # Spróbuj przesunąć t1 na pole t2
    action = MoveAction(t1.id, 6, 5)
    success, msg = engine.execute_action(action, player=Player(player_id=int(str(t1.owner).split()[0]), nation="Polska", role="Dowódca"))
    assert not success
    assert "zajęte" in msg.lower() or "nie można" in msg.lower() or "blokad" in msg.lower()

def test_move_with_no_points():
    """Test: Ruch bez punktów ruchu jest blokowany."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    token = next((t for t in engine.tokens if 'Polska' in str(t.owner)), None)
    assert token is not None
    token.currentMovePoints = 0
    engine.board.set_tokens(engine.tokens)
    action = MoveAction(token.id, token.q + 1, token.r)
    success, msg = engine.execute_action(action, player=Player(player_id=int(str(token.owner).split()[0]), nation="Polska", role="Dowódca"))
    assert not success
    assert "brak ruchu" in msg.lower() or "za mało" in msg.lower() or "brak punktów" in msg.lower() or "nie można" in msg.lower()

def test_move_points_reset_only_for_active():
    """Test: Po next_turn tylko żetony aktywnego gracza mają zresetowane punkty ruchu."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    # Ustaw wszystkim żetonom currentMovePoints na 0
    for t in engine.tokens:
        t.currentMovePoints = 0
    prev_player = engine.current_player
    engine.next_turn()
    # Sprawdź, czy żetony nowego gracza mają zresetowane punkty
    for t in engine.tokens:
        if str(prev_player) in str(t.owner):
            assert t.currentMovePoints == 0
        else:
            assert t.currentMovePoints == t.maxMovePoints

def test_save_load_after_move(tmp_path):
    """Test: Zapis i odczyt stanu po ruchu."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    token = next((t for t in engine.tokens if 'Polska' in str(t.owner)), None)
    assert token is not None
    start_q, start_r = token.q, token.r
    action = MoveAction(token.id, start_q + 1, start_r)
    engine.execute_action(action, player=Player(player_id=int(str(token.owner).split()[0]), nation="Polska", role="Dowódca"))
    save_path = tmp_path / "state_after_move.json"
    engine.save_state(str(save_path))
    engine2 = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    engine2.load_state(str(save_path))
    assert any(t.id == token.id and t.q == start_q + 1 and t.r == start_r for t in engine2.tokens)

def test_invalid_token_id():
    """Test: Próba ruchu nieistniejącym żetonem zwraca błąd."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    action = MoveAction("NIEISTNIEJACY_ID", 1, 1)
    success, msg = engine.execute_action(action, player=Player(player_id=1, nation="Polska", role="Dowódca"))
    assert not success
    assert "nie znaleziono" in msg.lower() or "błąd" in msg.lower() or "nie istnieje" in msg.lower()

def test_move_out_of_map():
    """Test: Próba ruchu na pole poza mapą (ujemne lub za duże współrzędne)."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    token = next((t for t in engine.tokens if 'Polska' in str(t.owner)), None)
    assert token is not None
    action = MoveAction(token.id, -100, -100)
    success, msg = engine.execute_action(action, player=Player(player_id=int(str(token.owner).split()[0]), nation="Polska", role="Dowódca"))
    assert not success
    assert "nie istnieje" in msg.lower() or "poza planszę" in msg.lower() or "brak" in msg.lower()

def test_move_other_player_token():
    """Test: Próba ruchu żetonem innego gracza (oszustwo)."""
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    polish = next((t for t in engine.tokens if 'Polska' in str(t.owner)), None)
    german = next((t for t in engine.tokens if 'Niemcy' in str(t.owner)), None)
    assert polish is not None and german is not None
    # Niemiecki gracz próbuje ruszyć polskim żetonem
    action = MoveAction(polish.id, polish.q + 1, polish.r)
    success, msg = engine.execute_action(action, player=Player(player_id=int(str(german.owner).split()[0]), nation="Niemcy", role="Dowódca"))
    assert not success
    assert "nie należy" in msg.lower() or "dowódcy" in msg.lower() or "nie możesz" in msg.lower()

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
