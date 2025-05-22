from gui.ekran_startowy import EkranStartowy
from core.tura import TurnManager
from engine.player import Player
from gui.panel_generala import PanelGenerala
from gui.panel_dowodcy import PanelDowodcy
from engine.engine import GameEngine
import tkinter as tk

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

    # Inicjalizacja silnika gry (GameEngine jako źródło prawdy)
    game_engine = GameEngine(
        map_path="assets/mapa_dane.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )

    # Tworzenie obiektów graczy z uwzględnieniem czasu na turę i ścieżek do zdjęć
    players = [
        Player(1, miejsca[0], "Generał", czasy[0], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Juliusz Rómmel.png"),
        Player(2, miejsca[1], "Dowódca", czasy[1], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Tadeusz Kutrzeba.png"),
        Player(3, miejsca[2], "Dowódca", czasy[2], "c:/Users/klif/kampania1939_fixed/gui/images/Marszałek Polski Edward Rydz-Śmigły.png"),
        Player(4, miejsca[3], "Generał", czasy[3], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Fedor von Bock.png"),
        Player(5, miejsca[4], "Dowódca", czasy[4], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Walther von Reichenau.png"),
        Player(6, miejsca[5], "Dowódca", czasy[5], "c:/Users/klif/kampania1939_fixed/gui/images/Generał pułkownik Walther von Brauchitsch.png"),
    ]

    # Inicjalizacja menedżera tur
    turn_manager = TurnManager(players, game_engine=game_engine)

    # Pętla tur
    while True:
        # Pobranie aktualnego gracza
        current_player = turn_manager.get_current_player()

        # Otwieranie odpowiedniego panelu z numerem tury i czasem na turę
        if current_player.role == "Generał":
            app = PanelGenerala(turn_number=turn_manager.current_turn, ekonomia=current_player.economy, gracz=current_player, gracze=players, game_engine=game_engine)
        elif current_player.role == "Dowódca":
            app = PanelDowodcy(turn_number=turn_manager.current_turn, remaining_time=current_player.time_limit * 60, gracz=current_player, game_engine=game_engine)
        else:
            continue

        # Aktualizacja pogody dla panelu
        if hasattr(app, 'update_weather'):
            app.update_weather(turn_manager.current_weather)

        # Aktualizacja raportu ekonomicznego tylko dla paneli generałów
        if isinstance(app, PanelGenerala):
            current_player.economy.generate_economic_points()
            current_player.economy.add_special_points()
            app.update_economy()

            # Synchronizacja dostępnych punktów w sekcji suwaków
            available_points = current_player.economy.get_points()['economic_points']
            app.zarzadzanie_punktami(available_points)

        # Aktualizacja punktów ekonomicznych dla paneli dowódców
        if isinstance(app, PanelDowodcy):
            przydzielone_punkty = current_player.economy.get_points()['economic_points']
            app.update_economy(przydzielone_punkty)

        app.mainloop()  # Uruchomienie panelu

        # Przejście do następnej tury/podtury
        turn_manager.next_turn()

        # Sprawdzenie warunku zakończenia gry
        if turn_manager.is_game_over():
            break