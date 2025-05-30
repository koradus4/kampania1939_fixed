import pytest
from core.ekonomia import EconomySystem
from engine.player import Player
from gui.zarzadzanie_punktami_ekonomicznymi import ZarzadzaniePunktamiEkonomicznymi
import tkinter as tk

def test_przekazywanie_punktow_ekonomicznych_real_data():
    # Przygotowanie realnych danych
    root = tk.Tk()
    root.withdraw()  # Ukryj okno główne
    ekonomia = EconomySystem()
    ekonomia.economic_points = 10
    dowodcy = [Player(2, "Polska", "Dowódca", 5, ""), Player(3, "Polska", "Dowódca", 5, "")]
    for d in dowodcy:
        d.economy = EconomySystem()
    przekazane = {}
    def on_points_change(val):
        przekazane['ostatnia'] = val
    panel = ZarzadzaniePunktamiEkonomicznymi(
        root,
        available_points=ekonomia.economic_points,
        commanders=[d.id for d in dowodcy],
        on_points_change=on_points_change
    )
    # Symulacja przydziału punktów przez GUI (ustawienie suwaków)
    getattr(panel, f"{dowodcy[0].id}_slider").set(4)
    panel.update_points(dowodcy[0].id, 4)
    getattr(panel, f"{dowodcy[1].id}_slider").set(3)
    panel.update_points(dowodcy[1].id, 3)
    panel.accept_final_points()
    # Przekazanie punktów do dowódców
    dowodcy[0].economy.economic_points += panel.commander_points[dowodcy[0].id]
    dowodcy[1].economy.economic_points += panel.commander_points[dowodcy[1].id]
    ekonomia.subtract_points(sum(panel.commander_points.values()))
    # Assercje
    assert panel.commander_points[dowodcy[0].id] == 4
    assert panel.commander_points[dowodcy[1].id] == 3
    assert dowodcy[0].economy.economic_points == 4
    assert dowodcy[1].economy.economic_points == 3
    assert ekonomia.economic_points == 3
    assert przekazane['ostatnia'] == 3
    root.destroy()
