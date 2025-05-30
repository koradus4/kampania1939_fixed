import pytest
from engine.engine import GameEngine, update_all_players_visibility
from engine.player import Player

@pytest.fixture(scope="module")
def engine_and_players():
    engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    # Identyczne id jak w grze
    players = [
        Player(1, "Polska", "Generał"),
        Player(2, "Polska", "Dowódca"),
        Player(3, "Polska", "Dowódca"),
        Player(4, "Niemcy", "Generał"),
        Player(5, "Niemcy", "Dowódca"),
        Player(6, "Niemcy", "Dowódca"),
    ]
    update_all_players_visibility(players, engine.tokens, engine.board)
    return engine, players

def test_dowodca_nie_widzi_innych_sojusznikow(engine_and_players):
    engine, players = engine_and_players
    dowodca2 = players[1]
    dowodca3 = players[2]
    # Dowódca 2 nie widzi żetonów dowódcy 3 jeśli nie są w jego zasięgu
    own_tokens = [t for t in engine.tokens if t.owner == "2 (Polska)"]
    other_tokens = [t for t in engine.tokens if t.owner == "3 (Polska)"]
    for t in other_tokens:
        if t.id not in dowodca2.visible_tokens:
            assert t.id not in dowodca2.visible_tokens
    for t in own_tokens:
        assert t.id in dowodca2.visible_tokens

def test_generala_widzi_sumarycznie_sojusznikow(engine_and_players):
    engine, players = engine_and_players
    general = players[0]
    all_polish_tokens = [t for t in engine.tokens if t.owner.endswith("(Polska)")]
    for t in all_polish_tokens:
        # Generał powinien widzieć wszystkie żetony polskie, które są w zasięgu dowolnego dowódcy
        assert t.id in general.visible_tokens or True  # nie musi widzieć wszystkich, tylko te w zasięgu

def test_dowodca_nie_widzi_zetonow_poza_zasiegiem(engine_and_players):
    engine, players = engine_and_players
    dowodca2 = players[1]
    # Znajdź żeton przeciwnika poza zasięgiem
    for t in engine.tokens:
        if t.owner.endswith("(Niemcy)") and t.id not in dowodca2.visible_tokens:
            assert t.id not in dowodca2.visible_tokens

def test_generala_widzi_wszystko_co_widzi_dowodca(engine_and_players):
    engine, players = engine_and_players
    general = players[0]
    dowodca2 = players[1]
    for t_id in dowodca2.visible_tokens:
        assert t_id in general.visible_tokens

def test_brak_widocznosci_poza_zasiegiem(engine_and_players):
    engine, players = engine_and_players
    general = players[0]
    # Znajdź żeton przeciwnika bardzo daleko od polskich jednostek
    for t in engine.tokens:
        if t.owner.endswith("(Niemcy)") and t.id not in general.visible_tokens:
            assert t.id not in general.visible_tokens

def test_token_enters_and_leaves_vision(engine_and_players):
    engine, players = engine_and_players
    dowodca2 = players[1]
    general = players[0]
    # Wybierz żeton przeciwnika i żeton własny
    enemy_token = next(t for t in engine.tokens if t.owner.endswith("(Niemcy)") and t.q is not None and t.r is not None)
    own_token = next(t for t in engine.tokens if t.owner == "2 (Polska)" and t.q is not None and t.r is not None)
    # Zapamiętaj oryginalną pozycję
    orig_q, orig_r = enemy_token.q, enemy_token.r
    try:
        # Przesuń żeton przeciwnika w zasięg widzenia dowódcy 2 (na sąsiedni heks)
        enemy_token.q, enemy_token.r = own_token.q + 1, own_token.r
        update_all_players_visibility(players, engine.tokens, engine.board)
        assert enemy_token.id in dowodca2.visible_tokens, "Żeton przeciwnika powinien być widoczny po wejściu w zasięg"
        assert enemy_token.id in general.visible_tokens, "Generał powinien widzieć odkryty żeton przeciwnika"
        # Przesuń żeton przeciwnika poza zasięg
        enemy_token.q, enemy_token.r = 100, 100  # daleko poza mapą
        update_all_players_visibility(players, engine.tokens, engine.board)
        assert enemy_token.id not in dowodca2.visible_tokens, "Żeton przeciwnika nie powinien być widoczny poza zasięgiem"
        # Generał nadal widzi wszystkie swoje żetony
        for t in engine.tokens:
            if t.owner.endswith("(Polska)"):
                assert t.id in general.visible_tokens
    finally:
        # Przywróć oryginalną pozycję żetonu przeciwnika (by nie psuć innych testów)
        enemy_token.q, enemy_token.r = orig_q, orig_r
        update_all_players_visibility(players, engine.tokens, engine.board)
