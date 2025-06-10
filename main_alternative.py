from core.tura import TurnManager
from engine.player import Player
from gui.panel_generala import PanelGenerala
from gui.panel_dowodcy import PanelDowodcy
from core.ekonomia import EconomySystem
from engine.engine import GameEngine, update_all_players_visibility, clear_temp_visibility
from gui.panel_gracza import PanelGracza
from core.zwyciestwo import VictoryConditions

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
    # --- WARUNKI ZWYCIĘSTWA: 30 rund ---
    victory_conditions = VictoryConditions(max_turns=30)
    just_loaded_save = False  # Flaga: czy właśnie wczytano save
    # Pętla tur
    last_loaded_player_info = None  # Przechowuj info o aktywnym graczu po wczytaniu save
    while True:
        # Jeśli po wczytaniu save jest info o aktywnym graczu, przełącz na niego
        if last_loaded_player_info:
            found = None
            for p in players:
                if (str(p.id) == str(last_loaded_player_info.get('id')) and
                    p.role == last_loaded_player_info.get('role') and
                    p.nation == last_loaded_player_info.get('nation')):
                    found = p
                    break
            if found:
                current_player = found
                turn_manager.current_player_index = players.index(found)
            last_loaded_player_info = None
        else:
            current_player = turn_manager.get_current_player()
        update_all_players_visibility(players, game_engine.tokens, game_engine.board)
        if current_player.role == "Generał":
            app = PanelGenerala(turn_number=turn_manager.current_turn, ekonomia=current_player.economy, gracz=current_player, gracze=players, game_engine=game_engine)
        elif current_player.role == "Dowódca":
            app = PanelDowodcy(turn_number=turn_manager.current_turn, remaining_time=current_player.time_limit * 60, gracz=current_player, game_engine=game_engine)
        # Patch: podmień funkcję on_load w PanelGracza, by ustawiać last_loaded_player_info
        def patch_on_load(panel_gracza):
            def new_on_load():
                import os
                from tkinter import filedialog, messagebox
                saves_dir = os.path.join(os.getcwd(), 'saves')
                os.makedirs(saves_dir, exist_ok=True)
                path = filedialog.askopenfilename(
                    filetypes=[('Plik zapisu', '*.json')],
                    initialdir=saves_dir
                )
                if path:
                    try:
                        from engine.save_manager import load_game
                        global last_loaded_player_info
                        global just_loaded_save
                        last_loaded_player_info = load_game(path, game_engine)
                        just_loaded_save = True
                        if hasattr(panel_gracza.master, 'panel_mapa'):
                            panel_gracza.master.panel_mapa.refresh()
                        if last_loaded_player_info:
                            msg = f"Gra została wczytana!\nAktywny gracz: {last_loaded_player_info.get('role','?')} {last_loaded_player_info.get('id','?')} ({last_loaded_player_info.get('nation','?')})"
                            messagebox.showinfo("Wczytanie gry", msg)
                        else:
                            messagebox.showinfo("Wczytanie gry", "Gra została wczytana!")
                        panel_gracza.winfo_toplevel().destroy()  # Zamknij całe okno, nie tylko ramkę
                    except Exception as e:
                        messagebox.showerror("Błąd wczytywania", str(e))
            panel_gracza.on_load = new_on_load
            if hasattr(panel_gracza, 'btn_load'):
                panel_gracza.btn_load.config(command=panel_gracza.on_load)

        # DEBUG: sprawdź dzieci left_frame
        if hasattr(app, 'left_frame'):
            for child in app.left_frame.winfo_children():
                if isinstance(child, PanelGracza):
                    patch_on_load(child)

        # --- USTAW AKTUALNEGO GRACZA W SILNIKU (DLA PANEL_MAPA) ---
        game_engine.current_player_obj = current_player

        # Aktualizacja pogody dla panelu
        if hasattr(app, 'update_weather'):
            app.update_weather(turn_manager.current_weather)
        # Aktualizacja punktów ekonomicznych dla paneli generałów
        if isinstance(app, PanelGenerala):
            # Debug: bilans przed losowaniem
            start_points = current_player.economy.economic_points
            current_player.economy.generate_economic_points()
            current_player.economy.add_special_points()
            # Debug: bilans po losowaniu
            print(f"[EKONOMIA][GENERAŁ] Stan punktów po losowaniu: {current_player.economy.economic_points}")
            available_points = current_player.economy.get_points()['economic_points']
            app.update_economy(available_points)  # Przekazanie dostępnych punktów ekonomicznych

            # Synchronizacja dostępnych punktów w sekcji suwaków
            app.zarzadzanie_punktami(available_points)

        # Aktualizacja punktów ekonomicznych dla paneli dowódców
        if isinstance(app, PanelDowodcy):
            przydzielone_punkty = current_player.economy.get_points()['economic_points']
            print(f"[EKONOMIA][DOWÓDCA] Dowódca {current_player.id} ({current_player.nation}) - punkty na start tury: {przydzielone_punkty}")
            app.update_economy(przydzielone_punkty)  # Aktualizacja interfejsu dowódcy
            # --- Synchronizacja punktów ekonomicznych dowódcy z systemem ekonomii ---
            current_player.punkty_ekonomiczne = przydzielone_punkty

        try:
            app.mainloop()  # Uruchomienie panelu
        except Exception as e:
            print(f"Błąd: {e}")

        # Przejście do następnej tury/podtury
        # --- DEBUG: podsumowanie przekazania punktów dowódcom ---
        if isinstance(app, PanelGenerala):
            if hasattr(app, 'zarzadzanie_punktami_widget'):
                widget = app.zarzadzanie_punktami_widget
                print("[EKONOMIA][PRZEKAZANIE] Podsumowanie przekazania punktów dowódcom:")
                for commander_id, given in widget.commander_points.items():
                    dow = next((p for p in players if p.id == commander_id), None)
                    if dow:
                        start = getattr(dow, 'punkty_ekonomiczne', 0)
                        end = dow.economy.economic_points
                        spent = start - end if start > end else 0
                        print(f"  Dowódca {dow.id} ({dow.nation}): otrzymał {given} pkt, wydał {spent}, bilans: przed={start}, po={end}")
        turn_manager.next_turn()
        # --- ROZDZIEL PUNKTY Z KEY_POINTS ---
        game_engine.process_key_points(players)
        # --- SPRAWDZENIE KOŃCA GRY ---
        if victory_conditions.check_game_over(turn_manager.current_turn):
            print(victory_conditions.get_victory_message())
            print("=== PODSUMOWANIE ===")
            for p in players:
                vp = getattr(p, "victory_points", 0)
                print(f"{p.nation} {p.role} (id={p.id}): {vp} punktów zwycięstwa")
            print("====================")
            break
        # Reset blokady trybu ruchu na początku każdej tury, ale NIE po wczytaniu save
        if not just_loaded_save:
            for t in game_engine.tokens:
                t.movement_mode_locked = False
        # --- DODANE: wymuszenie aktualnej referencji gracza po wczytaniu save ---
        if just_loaded_save:
            # Po wczytaniu save'a zsynchronizuj listę players i current_player z game_engine
            players = game_engine.players
            clear_temp_visibility(game_engine.players)
            update_all_players_visibility(game_engine.players, game_engine.tokens, game_engine.board)
            # Znajdź aktualnego gracza po wczytaniu save
            found = None
            for p in game_engine.players:
                if (str(p.id) == str(last_loaded_player_info.get('id')) and
                    p.role == last_loaded_player_info.get('role') and
                    p.nation == last_loaded_player_info.get('nation')):
                    found = p
                    break
            if found:
                game_engine.current_player_obj = found
                current_player = found
            # Usunięto próbę synchronizacji panelu mapy, bo okno mogło być już zniszczone
        just_loaded_save = False
        clear_temp_visibility(players)
        # --- KONIEC DODATKU ---