from gui.ekran_startowy import EkranStartowy
from core.tura import TurnManager
from model.gracz import Gracz
from gui.panel_generalapolska import PanelGeneralaPolska
from gui.panel_generalaniemcy import PanelGeneralaNiemcy
from gui.panel_dowodcypolska1 import PanelDowodcyPolska1
from gui.panel_dowodcypolska2 import PanelDowodcyPolska2
from gui.panel_dowodcyniemcy1 import PanelDowodcyNiemcy1
from gui.panel_dowodcyniemcy2 import PanelDowodcyNiemcy2
import tkinter as tk

# Funkcja główna
if __name__ == "__main__":
    # Ekran startowy
    root = tk.Tk()
    ekran_startowy = EkranStartowy(root)
    root.mainloop()

    # Pobranie wyborów graczy z ekranu startowego
    miejsca = ekran_startowy.miejsca  # Lista nacji w kolejności: Generał 1, Dowódca 1, Dowódca 2, Generał 2, Dowódca 1, Dowódca 2

    # Tworzenie obiektów graczy
    gracze = [
        Gracz(1, miejsca[0], "Generał"),
        Gracz(2, miejsca[1], "Dowódca"),
        Gracz(3, miejsca[2], "Dowódca"),
        Gracz(4, miejsca[3], "Generał"),
        Gracz(5, miejsca[4], "Dowódca"),
        Gracz(6, miejsca[5], "Dowódca"),
    ]

    # Inicjalizacja menedżera tur
    turn_manager = TurnManager(gracze)

    # Pętla tur
    while True:
        # Pobranie aktualnego gracza
        current_player = turn_manager.get_current_player()

        # Otwieranie odpowiedniego panelu z numerem tury
        if current_player.rola == "Generał" and current_player.nacja == "Polska":
            app = PanelGeneralaPolska(turn_number=turn_manager.current_turn)
        elif current_player.rola == "Generał" and current_player.nacja == "Niemcy":
            app = PanelGeneralaNiemcy(turn_number=turn_manager.current_turn)
        elif current_player.rola == "Dowódca" and current_player.nacja == "Polska":
            if current_player.numer in [2, 3]:
                app = PanelDowodcyPolska1(turn_number=turn_manager.current_turn) if current_player.numer == 2 else PanelDowodcyPolska2(turn_number=turn_manager.current_turn)
        elif current_player.rola == "Dowódca" and current_player.nacja == "Niemcy":
            if current_player.numer in [5, 6]:
                app = PanelDowodcyNiemcy1(turn_number=turn_manager.current_turn) if current_player.numer == 5 else PanelDowodcyNiemcy2(turn_number=turn_manager.current_turn)

        app.mainloop()  # Uruchomienie panelu

        # Przejście do następnej tury/podtury
        if turn_manager.next_turn():
            print("Zakończono pełną turę.")

        # Sprawdzenie warunku zakończenia gry
        if turn_manager.is_game_over():
            print("Gra zakończona! Osiągnięto maksymalną liczbę tur.")
            break