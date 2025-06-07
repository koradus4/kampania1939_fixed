import pytest
from gui.panel_generala import PanelGenerala
from core.ekonomia import EconomySystem
from engine.player import Player

class DummyGameEngine:
    pass

def test_wielokrotne_przydzielanie_punktow():
    # Przygotowanie gracza generała i dowódców
    general = Player(1, "Polska", "Generał", 5, "img.png")
    dowodca2 = Player(2, "Polska", "Dowódca", 5, "img.png")
    dowodca3 = Player(3, "Polska", "Dowódca", 5, "img.png")
    general.economy = EconomySystem()
    general.economy.economic_points = 7  # Ustawiamy pulę na początku tury
    players = [general, dowodca2, dowodca3]
    
    # Tworzymy panel generała (bez uruchamiania mainloop)
    app = PanelGenerala(
        turn_number=1,
        ekonomia=general.economy,
        gracz=general,
        gracze=players,
        game_engine=DummyGameEngine()
    )
    # Otwieramy suwaki i przydzielamy 2 punkty
    app.toggle_support_sliders()
    app.zarzadzanie_punktami_widget.commander_points = {2: 1, 3: 1}
    app.toggle_support_sliders()  # Akceptacja
    assert general.economy.economic_points == 5
    # Otwieramy ponownie suwaki i przydzielamy 4 punkty
    app.toggle_support_sliders()
    app.zarzadzanie_punktami_widget.commander_points = {2: 2, 3: 2}
    app.toggle_support_sliders()  # Akceptacja
    # Oczekujemy, że punkty spadną poniżej zera (błąd!)
    assert general.economy.economic_points < 0, "Panel pozwala przekazać więcej punktów niż miał generał!"
