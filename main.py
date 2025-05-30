from gui.ekran_startowy import EkranStartowy
from core.tura import TurnManager
from engine.player import Player
from gui.panel_generala import PanelGenerala
from gui.panel_dowodcy import PanelDowodcy
from engine.engine import GameEngine, update_all_players_visibility
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
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )

    # Tworzenie obiektów graczy z uwzględnieniem czasu na turę i ścieżek do zdjęć
    # Automatyczne przypisanie id dowódców zgodnie z ownerami żetonów
    # Polska: dowódcy id=2,3; Niemcy: dowódcy id=5,6
    # Ustal kolejność graczy na podstawie miejsc i ról, aby pierwszym był generał wybranej nacji
    # Szukamy indeksów dla każdej roli i nacji
    polska_gen = miejsca.index("Polska")
    polska_dow1 = miejsca.index("Polska", polska_gen+1)
    polska_dow2 = miejsca.index("Polska", polska_dow1+1)
    niemcy_gen = miejsca.index("Niemcy")
    niemcy_dow1 = miejsca.index("Niemcy", niemcy_gen+1)
    niemcy_dow2 = miejsca.index("Niemcy", niemcy_dow1+1)

    # Kolejność: najpierw generał tej nacji, która jest pierwsza w miejscach
    if niemcy_gen < polska_gen:
        players = [
            Player(4, "Niemcy", "Generał", czasy[niemcy_gen], "c:/Users/klif/kampania1939_fixed/gui/images/Generał pułkownik Walther von Brauchitsch.png"),
            Player(5, "Niemcy", "Dowódca", czasy[niemcy_dow1], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Fedor von Bock.png"),
            Player(6, "Niemcy", "Dowódca", czasy[niemcy_dow2], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Walther von Reichenau.png"),
            Player(1, "Polska", "Generał", czasy[polska_gen], "c:/Users/klif/kampania1939_fixed/gui/images/Marszałek Polski Edward Rydz-Śmigły.png"),
            Player(2, "Polska", "Dowódca", czasy[polska_dow1], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Juliusz Rómmel.png"),
            Player(3, "Polska", "Dowódca", czasy[polska_dow2], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Tadeusz Kutrzeba.png"),
        ]
    else:
        players = [
            Player(1, "Polska", "Generał", czasy[polska_gen], "c:/Users/klif/kampania1939_fixed/gui/images/Marszałek Polski Edward Rydz-Śmigły.png"),
            Player(2, "Polska", "Dowódca", czasy[polska_dow1], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Juliusz Rómmel.png"),
            Player(3, "Polska", "Dowódca", czasy[polska_dow2], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Tadeusz Kutrzeba.png"),
            Player(4, "Niemcy", "Generał", czasy[niemcy_gen], "c:/Users/klif/kampania1939_fixed/gui/images/Generał pułkownik Walther von Brauchitsch.png"),
            Player(5, "Niemcy", "Dowódca", czasy[niemcy_dow1], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Fedor von Bock.png"),
            Player(6, "Niemcy", "Dowódca", czasy[niemcy_dow2], "c:/Users/klif/kampania1939_fixed/gui/images/Generał Walther von Reichenau.png"),
        ]

    # Uzupełnij economy dla wszystkich graczy (Generał i Dowódca)
    from core.ekonomia import EconomySystem
    for p in players:
        if not hasattr(p, 'economy') or p.economy is None:
            p.economy = EconomySystem()

    # --- AKTUALIZACJA WIDOCZNOŚCI NA START ---
    update_all_players_visibility(players, game_engine.tokens, game_engine.board)

    # Inicjalizacja menedżera tur
    turn_manager = TurnManager(players, game_engine=game_engine)

    # Pętla tur
    while True:
        # Pobranie aktualnego gracza
        current_player = turn_manager.get_current_player()
        # --- AKTUALIZACJA WIDOCZNOŚCI PRZED PANELEM ---
        update_all_players_visibility(players, game_engine.tokens, game_engine.board)
        game_engine.current_player_obj = current_player  # <-- Ustaw aktualnego gracza dla panelu mapy
        # DEBUG: sprawdź czy current_player jest poprawnie ustawiany
        print(f"[DEBUG] main.py: current_player = {current_player}, id={getattr(current_player, 'id', None)}, role={getattr(current_player, 'role', None)}, nation={getattr(current_player, 'nation', None)}")
        print(f"[DEBUG] main.py: visible_tokens = {getattr(current_player, 'visible_tokens', None)}")

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
        # --- AKTUALIZACJA WIDOCZNOŚCI PO KAŻDEJ TURZE ---
        # (możesz zostawić, ale nie jest już konieczne, bo i tak jest na początku każdej tury)
        # update_all_players_visibility(players, game_engine.tokens, game_engine.board)

        # Sprawdzenie warunku zakończenia gry
        if turn_manager.is_game_over():
            break