import tkinter as tk
from gui.panel_gracza import PanelGracza
from engine.player import Player
from core.ekonomia import EconomySystem

def test_panel_gracza_full_gui():
    # Przygotuj graczy i silnik
    root = tk.Tk()
    player = Player(1, "Polska", "Generał", 5)
    player.victory_points = 1234
    player.economy = EconomySystem()
    player.economy.economic_points = 77
    player.economy.special_points = 5
    player.visible_tokens = {"A", "B"}
    player.visible_hexes = {(1, 2), (3, 4)}
    player.temp_visible_tokens = {"C"}
    player.temp_visible_hexes = {(5, 6)}
    player.vp_history = [
        {"turn": 1, "amount": 100, "reason": "eliminacja", "token_id": "A", "enemy": "Niemcy"},
        {"turn": 2, "amount": 200, "reason": "eliminacja", "token_id": "B", "enemy": "Niemcy"},
    ]
    # Dodaj drugiego gracza tej samej nacji
    player2 = Player(2, "Polska", "Dowódca", 5)
    player2.victory_points = 4321
    player2.economy = EconomySystem()
    player2.economy.economic_points = 33
    player2.economy.special_points = 2
    # Dodaj gracza innej nacji
    player3 = Player(4, "Niemcy", "Generał", 5)
    player3.victory_points = 999
    player3.economy = EconomySystem()
    player3.economy.economic_points = 11
    player3.economy.special_points = 1
    # Symuluj silnik z listą graczy
    class DummyEngine:
        players = [player, player2, player3]
    engine = DummyEngine()

    panel = PanelGracza(root, "Test", "assets/mapa_globalna.jpg", engine, player=player)
    panel.pack()
    root.update_idletasks()

    # Sprawdź sumę VP dla nacji
    vp_text = panel.vp_value_label.cget("text")
    assert vp_text == str(1234 + 4321), f"VP widget pokazuje {vp_text}, oczekiwano {1234+4321}"

    # Sprawdź tytuł
    title_text = panel.vp_label.cget("text")
    assert "nacja" in title_text.lower(), f"Tytuł widgetu: {title_text}"

    # Sprawdź szerokość overlay
    width = panel.overlay_frame.winfo_width()
    assert width >= 100, f"Overlay za wąski: {width}px"

    # Sprawdź, czy pole VP jest białe
    vp_bg = panel.vp_value_box.cget("bg")
    assert vp_bg == "white", f"Tło VP powinno być białe, jest {vp_bg}"

    # Sprawdź, czy widget nie zgłasza błędów przy update_vp
    try:
        panel.update_vp()
    except Exception as e:
        assert False, f"update_vp zgłosił wyjątek: {e}"

    # Sprawdź, czy PanelGracza jest na liście instancji
    from gui.panel_gracza import PanelGracza as PG
    assert panel in PG._instances, "PanelGracza nie jest zarejestrowany w _instances!"

    # Sprawdź, czy destroy usuwa z listy instancji
    panel.destroy()
    assert panel not in PG._instances, "PanelGracza nie został usunięty z _instances po destroy()!"

    print("Test PanelGracza FULL: suma VP, overlay, tytuł, rejestracja, update, destroy OK")
    root.destroy()

if __name__ == "__main__":
    test_panel_gracza_full_gui()
