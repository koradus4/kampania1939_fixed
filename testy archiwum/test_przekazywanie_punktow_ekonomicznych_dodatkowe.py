import pytest
from core.ekonomia import EconomySystem
from engine.player import Player
from gui.zarzadzanie_punktami_ekonomicznymi import ZarzadzaniePunktamiEkonomicznymi
import tkinter as tk

def test_brak_przekroczenia_puli():
    root = tk.Tk()
    root.withdraw()
    ekonomia = EconomySystem()
    ekonomia.economic_points = 5
    dowodcy = [Player(2, "Polska", "Dowódca", 5, ""), Player(3, "Polska", "Dowódca", 5, "")]
    for d in dowodcy:
        d.economy = EconomySystem()
    panel = ZarzadzaniePunktamiEkonomicznymi(
        root,
        available_points=ekonomia.economic_points,
        commanders=[d.id for d in dowodcy]
    )
    # Przekroczenie puli: najpierw 3, potem 4 (razem 7, za dużo)
    panel.update_points(dowodcy[0].id, 3)
    panel.update_points(dowodcy[1].id, 4)
    # Drugi suwak powinien wrócić do 0
    assert panel.commander_points[dowodcy[0].id] == 3
    assert panel.commander_points[dowodcy[1].id] == 0
    root.destroy()

def test_reset_suwakow_po_refresh():
    root = tk.Tk()
    root.withdraw()
    ekonomia = EconomySystem()
    ekonomia.economic_points = 8
    dowodcy = [Player(2, "Polska", "Dowódca", 5, ""), Player(3, "Polska", "Dowódca", 5, "")]
    for d in dowodcy:
        d.economy = EconomySystem()
    panel = ZarzadzaniePunktamiEkonomicznymi(
        root,
        available_points=ekonomia.economic_points,
        commanders=[d.id for d in dowodcy]
    )
    panel.update_points(dowodcy[0].id, 5)
    panel.update_points(dowodcy[1].id, 2)
    # Zmiana dostępnej puli na 4 (mniej niż suma)
    panel.refresh_available_points(4)
    # Suwaki powinny mieć ograniczony zakres
    assert panel.available_points == 4
    assert getattr(panel, f"{dowodcy[0].id}_slider").cget('to') == 4
    assert getattr(panel, f"{dowodcy[1].id}_slider").cget('to') == 4
    root.destroy()

def test_accept_final_points_ustawia_commander_points():
    root = tk.Tk()
    root.withdraw()
    ekonomia = EconomySystem()
    ekonomia.economic_points = 6
    dowodcy = [Player(2, "Polska", "Dowódca", 5, ""), Player(3, "Polska", "Dowódca", 5, "")]
    for d in dowodcy:
        d.economy = EconomySystem()
    panel = ZarzadzaniePunktamiEkonomicznymi(
        root,
        available_points=ekonomia.economic_points,
        commanders=[d.id for d in dowodcy]
    )
    getattr(panel, f"{dowodcy[0].id}_slider").set(2)
    panel.update_points(dowodcy[0].id, 2)
    getattr(panel, f"{dowodcy[1].id}_slider").set(4)
    panel.update_points(dowodcy[1].id, 4)
    panel.accept_final_points()
    assert panel.commander_points[dowodcy[0].id] == 2
    assert panel.commander_points[dowodcy[1].id] == 4
    root.destroy()
