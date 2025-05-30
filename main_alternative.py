from core.tura import TurnManager
from engine.player import Player
from gui.panel_generala import PanelGenerala
from gui.panel_dowodcy import PanelDowodcy
from core.ekonomia import EconomySystem
from engine.engine import GameEngine, update_all_players_visibility, clear_temp_visibility

# Funkcja główna
if __name__ == "__main__":
    # Automatyczne ustawienia graczy
    miejsca = ["Polska", "Polska", "Polska", "Niemcy", "Niemcy", "Niemcy"]
    czasy = [5, 5, 5, 5, 5, 5]  # Czas na turę w minutach

    # Inicjalizacja silnika gry (GameEngine jako źródło prawdy)
    game_engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42
    )

    # Automatyczne przypisanie id dowódców zgodnie z ownerami żetonów
    # Polska: dowódcy id=2,3; Niemcy: dowódcy id=5,6
    # Ustal kolejność graczy na podstawie miejsc i ról, aby pierwszym był generał wybranej nacji
    polska_gen = miejsca.index("Polska")
    polska_dow1 = miejsca.index("Polska", polska_gen+1)
    polska_dow2 = miejsca.index("Polska", polska_dow1+1)
    niemcy_gen = miejsca.index("Niemcy")
    niemcy_dow1 = miejsca.index("Niemcy", niemcy_gen+1)
    niemcy_dow2 = miejsca.index("Niemcy", niemcy_dow1+1)

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
    for p in players:
        if not hasattr(p, 'economy') or p.economy is None:
            p.economy = EconomySystem()

    # --- UDOSTĘPNIJ LISTĘ GRACZY W GAME_ENGINE ---
    game_engine.players = players

    # --- AKTUALIZACJA WIDOCZNOŚCI NA START ---
    update_all_players_visibility(players, game_engine.tokens, game_engine.board)

    # --- SYNCHRONIZACJA PUNKTÓW EKONOMICZNYCH DOWÓDCÓW Z SYSTEMEM EKONOMII ---
    for p in players:
        if hasattr(p, 'punkty_ekonomiczne'):
            p.punkty_ekonomiczne = p.economy.get_points()['economic_points']

    # Inicjalizacja menedżera tur
    turn_manager = TurnManager(players, game_engine=game_engine)

    # Pętla tur
    while True:
        # Pobranie aktualnego gracza
        current_player = turn_manager.get_current_player()
        # --- AKTUALIZACJA WIDOCZNOŚCI PRZED PANELEM ---
        update_all_players_visibility(players, game_engine.tokens, game_engine.board)

        # Otwieranie odpowiedniego panelu z numerem tury i czasem na turę
        if current_player.role == "Generał":
            app = PanelGenerala(turn_number=turn_manager.current_turn, ekonomia=current_player.economy, gracz=current_player, gracze=players, game_engine=game_engine)
        elif current_player.role == "Dowódca":
            app = PanelDowodcy(turn_number=turn_manager.current_turn, remaining_time=current_player.time_limit * 60, gracz=current_player, game_engine=game_engine)

        # Aktualizacja pogody dla panelu
        if hasattr(app, 'update_weather'):
            app.update_weather(turn_manager.current_weather)

        # Aktualizacja punktów ekonomicznych dla paneli generałów
        if isinstance(app, PanelGenerala):
            current_player.economy.generate_economic_points()
            current_player.economy.add_special_points()
            available_points = current_player.economy.get_points()['economic_points']
            app.update_economy(available_points)  # Przekazanie dostępnych punktów ekonomicznych

            # Synchronizacja dostępnych punktów w sekcji suwaków
            app.zarzadzanie_punktami(available_points)

        # Aktualizacja punktów ekonomicznych dla paneli dowódców
        if isinstance(app, PanelDowodcy):
            przydzielone_punkty = current_player.economy.get_points()['economic_points']
            app.update_economy(przydzielone_punkty)  # Aktualizacja interfejsu dowódcy
            # --- Synchronizacja punktów ekonomicznych dowódcy z systemem ekonomii ---
            current_player.punkty_ekonomiczne = przydzielone_punkty

        try:
            app.mainloop()  # Uruchomienie panelu
        except Exception as e:
            print(f"Błąd: {e}")

        # Przejście do następnej tury/podtury
        turn_manager.next_turn()
        # Wyczyść tymczasową widoczność po zakończeniu tury
        clear_temp_visibility(players)
        # Debug: sprawdź owner i nation po wczytaniu żetonów
        # for t in game_engine.tokens:
        #     print(f"[DEBUG] Załadowano żeton {t.id}: owner='{t.owner}', nation='{t.stats.get('nation','')}'")