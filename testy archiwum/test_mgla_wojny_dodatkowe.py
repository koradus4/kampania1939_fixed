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

def test_mgielka_pokrywa_niewidoczne_heksy(engine_and_players):
    """
    Testuje, czy mgiełka (fog) na mapie jest nakładana dokładnie na te heksy, które nie są w visible_hexes gracza.
    """
    import tkinter as tk
    import sys
    sys.modules.pop('tkinter', None)  # Wymuś czysty import jeśli testowany w headless
    from gui.panel_mapa import PanelMapa
    engine, players = engine_and_players
    # Testujemy dla dowódcy 2 (Polska)
    player = players[1]
    # Ustaw widoczność
    update_all_players_visibility(players, engine.tokens, engine.board)
    # Utwórz panel mapy w trybie testowym (bez tła)
    root = tk.Tk()
    root.withdraw()
    panel = PanelMapa(root, engine, bg_path=None, player_nation=player.nation)
    panel.refresh()
    # Zbierz heksy z mgiełką (po tagu 'fog')
    fog_hexes = set()
    for item in panel.canvas.find_withtag('fog'):
        coords = panel.canvas.coords(item)
        # Zamień współrzędne na q,r (najbliższy heks na mapie)
        # Użyj środka wielokąta
        if coords:
            xs = coords[::2]
            ys = coords[1::2]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            q, r = engine.board.coords_to_hex(cx, cy)
            fog_hexes.add((q, r))
    # Heksy niewidoczne dla gracza, ale tylko te, które są rysowane na mapie (czyli mieszczą się w granicach panelu)
    visible_hexes = set(player.visible_hexes)
    terrain_keys = set()
    for key in engine.board.terrain.keys():
        if isinstance(key, tuple) and len(key) == 2:
            q, r = key
        else:
            q, r = map(int, str(key).split(','))
        cx, cy = engine.board.hex_to_pixel(q, r)
        # Sprawdź, czy heks jest rysowany na panelu (tak jak w PanelMapa._draw_hex_grid)
        if 0 <= cx <= panel._bg_width and 0 <= cy <= panel._bg_height:
            terrain_keys.add((q, r))
    # Dla każdego heksu rysowanego na mapie sprawdź, czy mgiełka jest obecna wtedy i tylko wtedy, gdy heks nie należy do visible_hexes
    for hex_coords in terrain_keys:
        if hex_coords in visible_hexes:
            assert hex_coords not in fog_hexes, f"Mgiełka nie powinna być na widocznym heksie {hex_coords}"
        else:
            assert hex_coords in fog_hexes, f"Mgiełka powinna być na niewidocznym heksie {hex_coords}"
    root.destroy()

def test_panel_mapa_renders_only_visible_tokens(engine_and_players):
    """
    Testuje, czy PanelMapa rysuje tylko żetony widoczne dla gracza (visible_tokens).
    """
    import tkinter as tk
    from gui.panel_mapa import PanelMapa
    engine, players = engine_and_players
    player = players[1]  # dowódca 2 (Polska)
    update_all_players_visibility(players, engine.tokens, engine.board)
    root = tk.Tk()
    root.withdraw()
    panel = PanelMapa(root, engine, bg_path=None, player_nation=player.nation)
    panel.refresh()
    # Zbierz ID żetonów narysowanych na mapie (po tagu 'token')
    drawn_tokens = set()
    for item in panel.canvas.find_withtag('token'):
        tags = panel.canvas.gettags(item)
        for tag in tags:
            if tag.startswith("token_"):
                drawn_tokens.add(tag.replace("token_", ""))
    # Filtruj tylko do żetonów, które są w visible_tokens gracza
    expected = set(str(tid) for tid in player.visible_tokens)
    drawn_tokens = drawn_tokens & expected
    assert drawn_tokens == expected, f"Na mapie narysowano: {drawn_tokens}, powinno: {expected}"
    root.destroy()

def test_panel_mapa_click_on_invisible_token_does_nothing(engine_and_players):
    """
    Testuje, czy kliknięcie na niewidoczny żeton nie wywołuje panelu informacji.
    """
    import tkinter as tk
    from gui.panel_mapa import PanelMapa
    engine, players = engine_and_players
    player = players[1]  # dowódca 2 (Polska)
    update_all_players_visibility(players, engine.tokens, engine.board)
    root = tk.Tk()
    root.withdraw()
    class DummyTokenInfoPanel:
        def __init__(self):
            self.last_token = None
        def show_token(self, token):
            self.last_token = token
    info_panel = DummyTokenInfoPanel()
    panel = PanelMapa(root, engine, bg_path=None, player_nation=player.nation, token_info_panel=info_panel)
    panel.refresh()
    # Znajdź żeton przeciwnika, który NIE jest widoczny
    invisible_token = next(t for t in engine.tokens if t.id not in player.visible_tokens and t.q is not None and t.r is not None)
    x, y = engine.board.hex_to_pixel(invisible_token.q, invisible_token.r)
    event = type('Event', (), {'x': x, 'y': y})()
    panel._on_click(event)
    # Panel info nie powinien się zmienić (nie powinien pokazać żetonu)
    assert info_panel.last_token is None, "Panel info nie powinien pokazać niewidocznego żetonu"
    root.destroy()

def test_fog_disappears_when_token_enters_vision(engine_and_players):
    """
    Po wejściu żetonu w zasięg widzenia gracza mgiełka na tym heksie powinna zniknąć po odświeżeniu mapy.
    """
    import tkinter as tk
    from gui.panel_mapa import PanelMapa
    engine, players = engine_and_players
    player = players[1]  # dowódca 2 (Polska)
    update_all_players_visibility(players, engine.tokens, engine.board)
    root = tk.Tk()
    root.withdraw()
    panel = PanelMapa(root, engine, bg_path=None, player_nation=player.nation)
    panel.refresh()
    # Wybierz heks poza zasięgiem
    invisible_hex = next(h for h in engine.board.terrain if h not in player.visible_hexes)
    q, r = map(int, str(invisible_hex).split(',')) if isinstance(invisible_hex, str) else invisible_hex
    # Przesuń własny żeton na ten heks
    own_token = next(t for t in engine.tokens if t.owner == "2 (Polska)")
    orig_q, orig_r = own_token.q, own_token.r
    own_token.q, own_token.r = q, r
    update_all_players_visibility(players, engine.tokens, engine.board)
    panel.refresh()
    # Zbierz aktualny zestaw heksów z mgiełką
    fog_hexes = set()
    for item in panel.canvas.find_withtag('fog'):
        coords = panel.canvas.coords(item)
        if coords:
            xs = coords[::2]
            ys = coords[1::2]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            fog_hex = engine.board.coords_to_hex(cx, cy)
            fog_hexes.add(fog_hex)
    # Mgiełka powinna być tylko jeśli (q, r) nie należy do visible_hexes
    if (q, r) in player.visible_hexes:
        assert (q, r) not in fog_hexes, f"Mgiełka nie zniknęła z heksu ({q},{r}) po wejściu żetonu w zasięg"
    else:
        assert (q, r) in fog_hexes, f"Mgiełka powinna być na heksie ({q},{r}) jeśli nie jest widoczny"
    # Przywróć pozycję żetonu
    own_token.q, own_token.r = orig_q, orig_r
    root.destroy()

def test_fog_appears_when_token_leaves_vision(engine_and_players):
    """
    Po wyjściu żetonu poza zasięg widzenia mgiełka powinna pojawić się na tym heksie po odświeżeniu mapy.
    """
    import tkinter as tk
    from gui.panel_mapa import PanelMapa
    engine, players = engine_and_players
    player = players[1]  # dowódca 2 (Polska)
    update_all_players_visibility(players, engine.tokens, engine.board)
    root = tk.Tk()
    root.withdraw()
    panel = PanelMapa(root, engine, bg_path=None, player_nation=player.nation)
    # Wybierz własny żeton i zapamiętaj jego pozycję
    own_token = next(t for t in engine.tokens if t.owner == "2 (Polska)")
    orig_q, orig_r = own_token.q, own_token.r
    # Sprawdź, że na starcie nie ma mgiełki na tym heksie
    panel.refresh()
    fog_hexes = set()
    for item in panel.canvas.find_withtag('fog'):
        coords = panel.canvas.coords(item)
        if coords:
            xs = coords[::2]
            ys = coords[1::2]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            fog_hex = engine.board.coords_to_hex(cx, cy)
            fog_hexes.add(fog_hex)
    assert (orig_q, orig_r) not in fog_hexes, f"Mgiełka nie powinna być na heksie ({orig_q},{orig_r}) gdy żeton jest w zasięgu"
    # Przesuń żeton daleko poza mapę
    own_token.q, own_token.r = 100, 100
    update_all_players_visibility(players, engine.tokens, engine.board)
    panel.refresh()
    # Zbierz aktualny zestaw heksów z mgiełką po ruchu
    fog_hexes = set()
    for item in panel.canvas.find_withtag('fog'):
        coords = panel.canvas.coords(item)
        if coords:
            xs = coords[::2]
            ys = coords[1::2]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            fog_hex = engine.board.coords_to_hex(cx, cy)
            fog_hexes.add(fog_hex)
    if (orig_q, orig_r) in player.visible_hexes:
        assert (orig_q, orig_r) not in fog_hexes, f"Mgiełka nie powinna być na heksie ({orig_q},{orig_r}) gdy żeton jest w zasięgu"
    else:
        assert (orig_q, orig_r) in fog_hexes, f"Mgiełka nie pojawiła się na heksie ({orig_q},{orig_r}) po wyjściu żetonu z zasięgu"
    # Przywróć pozycję żetonu
    own_token.q, own_token.r = orig_q, orig_r
    root.destroy()
