import tkinter as tk
from gui.panel_gracza import PanelGracza
from engine.player import Player
from core.ekonomia import EconomySystem

def test_panel_gracza_vp_and_title():
    # Przygotuj graczy i silnik
    root = tk.Tk()
    player = Player(1, "Polska", "Generał", 5)
    player.victory_points = 1234  # testowa wartość VP
    player.economy = EconomySystem()
    # Dodaj drugiego gracza tej samej nacji, by sprawdzić sumowanie
    player2 = Player(2, "Polska", "Dowódca", 5)
    player2.victory_points = 4321
    player2.economy = EconomySystem()
    # Symuluj silnik z listą graczy
    class DummyEngine:
        players = [player, player2]
    engine = DummyEngine()

    panel = PanelGracza(root, "Test", "assets/mapa_globalna.jpg", engine, player=player)
    panel.pack()
    root.update_idletasks()

    # Sprawdź wartość VP (powinna być suma dla nacji: 1234 + 4321)
    vp_text = panel.vp_value_label.cget("text")
    assert vp_text == "5555", f"VP widget pokazuje {vp_text}, oczekiwano 5555"

    # Sprawdź tytuł
    title_text = panel.vp_label.cget("text")
    assert "nacja" in title_text.lower(), f"Tytuł widgetu: {title_text}"

    # Sprawdź, czy liczba nie jest ucięta (czy szerokość widgetu > 80)
    width = panel.overlay_frame.winfo_width()
    assert width >= 100, f"Overlay za wąski: {width}px"

    print("Test PanelGracza: VP, tytuł i overlay OK")
    root.destroy()

if __name__ == "__main__":
    test_panel_gracza_vp_and_title()
