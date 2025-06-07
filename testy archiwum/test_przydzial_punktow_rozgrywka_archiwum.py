import pytest
from gui.panel_generala import PanelGenerala
from engine.engine import GameEngine
from engine.player import Player
from core.ekonomia import EconomySystem

def test_przydzial_punktow_real_game():
    # Inicjalizacja silnika gry na realnych danych
    game_engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )
    # Tworzenie graczy
    general = Player(1, "Polska", "Generał", 5)
    dowodca2 = Player(2, "Polska", "Dowódca", 5)
    dowodca3 = Player(3, "Polska", "Dowódca", 5)
    general.economy = EconomySystem()
    dowodca2.economy = EconomySystem()
    dowodca3.economy = EconomySystem()
    general.economy.economic_points = 7
    players = [general, dowodca2, dowodca3]
    # PanelGenerala na prawdziwym silniku
    app = PanelGenerala(
        turn_number=1,
        ekonomia=general.economy,
        gracz=general,
        gracze=players,
        game_engine=game_engine
    )
    # Tura 1: przydzielamy 2 punkty
    app.toggle_support_sliders()
    getattr(app.zarzadzanie_punktami_widget, "2_slider").set(1)
    getattr(app.zarzadzanie_punktami_widget, "3_slider").set(1)
    app.toggle_support_sliders()
    assert general.economy.economic_points == 5
    # Nowa tura: dodajemy punkty
    general.economy.economic_points += 4
    app.zarzadzanie_punktami_widget.refresh_available_points(general.economy.economic_points)
    # Tura 2: przydzielamy 3 punkty
    app.toggle_support_sliders()
    getattr(app.zarzadzanie_punktami_widget, "2_slider").set(2)
    getattr(app.zarzadzanie_punktami_widget, "3_slider").set(1)
    app.toggle_support_sliders()
    assert general.economy.economic_points == 2
