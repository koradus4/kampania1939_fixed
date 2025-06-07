import pytest
from gui.panel_generala import PanelGenerala
from core.ekonomia import EconomySystem
from engine.player import Player

class DummyGameEngine:
    pass

def test_przydzial_punktow_nowa_tura():
    # Przygotowanie gracza generała i dowódców
    general = Player(1, "Polska", "Generał", 5, "img.png")
    dowodca2 = Player(2, "Polska", "Dowódca", 5, "img.png")
    dowodca3 = Player(3, "Polska", "Dowódca", 5, "img.png")
    general.economy = EconomySystem()
    general.economy.economic_points = 7  # Pula na początek tury 1
    players = [general, dowodca2, dowodca3]
    app = PanelGenerala(
        turn_number=1,
        ekonomia=general.economy,
        gracz=general,
        gracze=players,
        game_engine=DummyGameEngine()
    )
    # Tura 1: przydzielamy 2 punkty
    app.toggle_support_sliders()
    app.zarzadzanie_punktami_widget.commander_points = {2: 1, 3: 1}
    app.toggle_support_sliders()  # Akceptacja
    assert general.economy.economic_points == 5
    # Symulujemy nową turę: dodajemy nowe punkty
    general.economy.economic_points += 4  # np. nowa pula w nowej turze
    app.zarzadzanie_punktami_widget.refresh_available_points(general.economy.economic_points)
    # Tura 2: przydzielamy 3 punkty
    app.toggle_support_sliders()
    app.zarzadzanie_punktami_widget.commander_points = {2: 2, 3: 1}
    app.toggle_support_sliders()  # Akceptacja
    # Sprawdzamy, czy suma punktów po rozdysponowaniu jest poprawna
    assert general.economy.economic_points == 2, f"Po dwóch turach powinno zostać 2 punkty, jest {general.economy.economic_points}"
