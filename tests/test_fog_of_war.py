import pytest
from engine.board import Board
from engine.token import load_tokens
from engine.player import Player
from engine.engine import update_all_players_visibility

MAP_PATH = 'data/map_data.json'
TOKENS_INDEX_PATH = 'assets/tokens/index.json'
TOKENS_START_PATH = 'assets/start_tokens.json'

@pytest.fixture
def real_game_data():
    board = Board(MAP_PATH)
    tokens = load_tokens(TOKENS_INDEX_PATH, TOKENS_START_PATH)
    return board, tokens

@pytest.fixture
def players():
    # Dowódca 2 (Polska), Generał (Polska), Dowódca 5 (Niemcy), Generał (Niemcy)
    p2 = Player(2, 'Polska', 'Dowódca')
    g_pl = Player(0, 'Polska', 'Generał')
    p5 = Player(5, 'Niemcy', 'Dowódca')
    g_de = Player(0, 'Niemcy', 'Generał')
    return [p2, g_pl, p5, g_de]

def test_dowodca_2_widocznosc(real_game_data, players):
    board, tokens = real_game_data
    p2 = players[0]
    update_all_players_visibility(players, tokens, board)
    # Dowódca 2 powinien widzieć tylko swoje żetony
    own_tokens = [t for t in tokens if t.owner == '2 (Polska)']
    own_ids = set(t.id for t in own_tokens)
    assert p2.visible_tokens == own_ids, f"Dowódca 2 widzi: {p2.visible_tokens}, powinien: {own_ids}"
    # Każdy żeton powinien być widoczny na swoim heksie
    for t in own_tokens:
        assert (t.q, t.r) in p2.visible_hexes, f"Heks ({t.q},{t.r}) żetonu {t.id} nie jest widoczny dla dowódcy 2"

def test_generala_polska_widocznosc(real_game_data, players):
    board, tokens = real_game_data
    g_pl = players[1]
    p2 = players[0]
    update_all_players_visibility(players, tokens, board)
    # Generał Polski powinien widzieć sumę widoczności wszystkich polskich dowódców
    # (w tym przypadku tylko dowódca 2, bo tylko taki jest w teście)
    expected_tokens = set(p2.visible_tokens)
    expected_hexes = set(p2.visible_hexes)
    assert g_pl.visible_tokens == expected_tokens, f"Generał Polski widzi: {g_pl.visible_tokens}, powinien: {expected_tokens}"
    assert g_pl.visible_hexes == expected_hexes, f"Generał Polski widzi heksy: {g_pl.visible_hexes}, powinien: {expected_hexes}"

def test_dowodca_5_niemcy_widocznosc(real_game_data, players):
    board, tokens = real_game_data
    p5 = players[2]
    update_all_players_visibility(players, tokens, board)
    own_tokens = [t for t in tokens if t.owner == '5 (Niemcy)']
    own_ids = set(t.id for t in own_tokens)
    assert p5.visible_tokens == own_ids, f"Dowódca 5 widzi: {p5.visible_tokens}, powinien: {own_ids}"
    for t in own_tokens:
        assert (t.q, t.r) in p5.visible_hexes, f"Heks ({t.q},{t.r}) żetonu {t.id} nie jest widoczny dla dowódcy 5"

def test_generala_niemcy_widocznosc(real_game_data, players):
    board, tokens = real_game_data
    g_de = players[3]
    p5 = players[2]
    update_all_players_visibility(players, tokens, board)
    expected_tokens = set(p5.visible_tokens)
    expected_hexes = set(p5.visible_hexes)
    assert g_de.visible_tokens == expected_tokens, f"Generał Niemiec widzi: {g_de.visible_tokens}, powinien: {expected_tokens}"
    assert g_de.visible_hexes == expected_hexes, f"Generał Niemiec widzi heksy: {g_de.visible_hexes}, powinien: {expected_hexes}"

def test_diag_visible_tokens_and_hexes(real_game_data, players):
    board, tokens = real_game_data
    update_all_players_visibility(players, tokens, board)
    for player in players:
        print(f"Gracz {player.id} ({player.nation}, {player.role}):")
        print(f"  Widoczne żetony: {sorted(player.visible_tokens)}")
        print(f"  Widoczne heksy: {sorted(player.visible_hexes)}")
    any_visible = any(len(p.visible_tokens) > 0 for p in players)
    assert any_visible, "Żaden gracz nie widzi żadnego żetonu! Sprawdź logikę widoczności lub przekazywanie danych do GUI."
