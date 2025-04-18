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
import logging

# Dodanie debugowania do terminala
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

# Funkcja główna
if __name__ == "__main__":
    # Ekran startowy
    root = tk.Tk()
    ekran_startowy = EkranStartowy(root)
    root.mainloop()

    # Pobranie wyborów graczy z ekranu startowego
    game_data = ekran_startowy.get_game_data()
    miejsca = game_data["miejsca"]
    czasy = game_data["czasy"]

    # Tworzenie obiektów graczy z uwzględnieniem czasu na turę
    gracze = [
        Gracz(1, miejsca[0], "Generał", czasy[0]),
        Gracz(2, miejsca[1], "Dowódca", czasy[1]),
        Gracz(3, miejsca[2], "Dowódca", czasy[2]),
        Gracz(4, miejsca[3], "Generał", czasy[3]),
        Gracz(5, miejsca[4], "Dowódca", czasy[4]),
        Gracz(6, miejsca[5], "Dowódca", czasy[5]),
    ]

    # Inicjalizacja menedżera tur
    turn_manager = TurnManager(gracze)

    # Pętla tur
    while True:
        # Pobranie aktualnego gracza
        current_player = turn_manager.get_current_player()

        # Logowanie przed otwarciem panelu
        print(f"[DEBUG] Próba otwarcia panelu dla gracza: {current_player}")

        # Otwieranie odpowiedniego panelu z numerem tury i czasem na turę
        if current_player.rola == "Generał" and current_player.nacja == "Polska":
            print(f"[DEBUG] Przypisano PanelGeneralaPolska dla gracza {current_player.numer}")
            app = PanelGeneralaPolska(turn_number=turn_manager.current_turn, ekonomia=current_player.economy, gracz=current_player)
        elif current_player.rola == "Generał" and current_player.nacja == "Niemcy":
            print(f"[DEBUG] Przypisano PanelGeneralaNiemcy dla gracza {current_player.numer}")
            app = PanelGeneralaNiemcy(turn_number=turn_manager.current_turn, ekonomia=current_player.economy, gracz=current_player)
        elif current_player.rola == "Dowódca" and current_player.nacja == "Polska":
            if current_player.numer in [2, 5]:
                print(f"[DEBUG] Przypisano PanelDowodcyPolska1 dla gracza {current_player.numer}")
                app = PanelDowodcyPolska1(turn_number=turn_manager.current_turn, remaining_time=current_player.czas * 60)
            elif current_player.numer in [3, 6]:
                print(f"[DEBUG] Przypisano PanelDowodcyPolska2 dla gracza {current_player.numer}")
                app = PanelDowodcyPolska2(turn_number=turn_manager.current_turn, remaining_time=current_player.czas * 60)
        elif current_player.rola == "Dowódca" and current_player.nacja == "Niemcy":
            if current_player.numer in [2, 5]:
                print(f"[DEBUG] Przypisano PanelDowodcyNiemcy1 dla gracza {current_player.numer}")
                app = PanelDowodcyNiemcy1(turn_number=turn_manager.current_turn, remaining_time=current_player.czas * 60)
            elif current_player.numer in [3, 6]:
                print(f"[DEBUG] Przypisano PanelDowodcyNiemcy2 dla gracza {current_player.numer}")
                app = PanelDowodcyNiemcy2(turn_number=turn_manager.current_turn, remaining_time=current_player.czas * 60)
        else:
            print(f"[ERROR] Nie znaleziono odpowiedniego panelu dla gracza: {current_player}")
            continue

        # Logowanie po otwarciu panelu
        print(f"[DEBUG] Otworzono panel: {type(app).__name__} dla gracza: {current_player}")

        # Bezpieczne sprawdzenie, czy panel istnieje przed aktualizacją
        if app is not None and hasattr(app, 'is_active') and app.is_active:
            print(f"[DEBUG] Aktualizacja pogody dla panelu: {app}")
            app.update_weather(turn_manager.current_weather)

        # Aktualizacja pogody dla panelu
        if hasattr(app, 'update_weather'):
            print(f"[DEBUG] Wywołanie update_weather dla panelu: {type(app).__name__}")
            app.update_weather(turn_manager.current_weather)

        # Aktualizacja raportu ekonomicznego tylko dla paneli generałów
        if isinstance(app, (PanelGeneralaPolska, PanelGeneralaNiemcy)):
            current_player.economy.generate_economic_points()
            current_player.economy.add_special_points()
            app.update_economy()

        app.mainloop()  # Uruchomienie panelu

        # Logowanie szczegółów po każdej turze do terminala
        logging.info("=== Szczegóły tury ===")
        logging.info(f"Aktualny gracz: {current_player}")
        logging.info(f"Numer tury: {turn_manager.current_turn}")
        logging.info(f"Pogoda: {turn_manager.current_weather}")
        logging.info(f"Punkty ekonomiczne: {current_player.economy.get_points()['economic_points']}")
        logging.info(f"Punkty specjalne: {current_player.economy.get_points()['special_points']}")

        # Przejście do następnej tury/podtury
        if turn_manager.next_turn():
            print("Zakończono pełną turę.")

        # Sprawdzenie warunku zakończenia gry
        if turn_manager.is_game_over():
            print("Gra zakończona! Osiągnięto maksymalną liczbę tur.")
            break