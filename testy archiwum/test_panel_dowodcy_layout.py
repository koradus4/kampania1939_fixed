import unittest
import tkinter as tk
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from gui.panel_dowodcy import PanelDowodcy

class DummyGameEngine:
    board = MagicMock()

class TestPanelDowodcyLayout(unittest.TestCase):
    def setUp(self):
        # Patch PanelMapa i PanelGracza, aby nie wymagały realnych zależności
        patcher1 = patch('gui.panel_dowodcy.PanelMapa', MagicMock())
        patcher2 = patch('gui.panel_dowodcy.PanelGracza', MagicMock())
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        patcher1.start()
        patcher2.start()
        gracz = SimpleNamespace(id=1, nation="Polska", name="Test", image_path="", punkty_ekonomiczne=10)
        self.panel = PanelDowodcy(
            turn_number=1,
            remaining_time=60,
            gracz=gracz,
            game_engine=DummyGameEngine()
        )

    def test_btn_tankuj_above_weather_panel(self):
        # Pobierz listę dzieci left_frame od dołu (BOTTOM)
        children = list(self.panel.left_frame.pack_slaves())
        # Ostatni powinien być weather_panel, przedostatni btn_tankuj
        self.assertIs(children[-1], self.panel.weather_panel)
        self.assertIs(children[-2], self.panel.btn_tankuj)

    def test_weather_panel_above_btn_tankuj(self):
        # Pobierz listę dzieci left_frame od dołu (BOTTOM)
        children = list(self.panel.left_frame.pack_slaves())
        # Ostatni powinien być btn_tankuj, przedostatni weather_panel
        self.assertIs(children[-1], self.panel.btn_tankuj)
        self.assertIs(children[-2], self.panel.weather_panel)

if __name__ == "__main__":
    unittest.main()
