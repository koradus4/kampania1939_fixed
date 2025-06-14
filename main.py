from gui.ekran_startowy import EkranStartowy
from core.tura import TurnManager
from engine.player import Player
from gui.panel_generala import PanelGenerala
from gui.panel_dowodcy import PanelDowodcy
from engine.engine import GameEngine, update_all_players_visibility, clear_temp_visibility
from gui.panel_gracza import PanelGracza
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
    czasy = game_data["czasy"]    # Inicjalizacja silnika gry (GameEngine jako źródło prawdy)
    game_engine = GameEngine(
        map_path="data/map_data.json",
        tokens_index_path="assets/tokens/index.json",
        tokens_start_path="assets/start_tokens.json",
        seed=42,
        read_only=True  # Zapobiega nadpisywaniu pliku mapy
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

    # --- UDOSTĘPNIJ LISTĘ GRACZY W GAME_ENGINE ---
    game_engine.players = players

    # --- AKTUALIZACJA WIDOCZNOŚCI NA START ---
    update_all_players_visibility(players, game_engine.tokens, game_engine.board)

    # Inicjalizacja menedżera tur
    turn_manager = TurnManager(players, game_engine=game_engine)

    # Pętla tur
    last_loaded_player_info = None  # Przechowuj info o aktywnym graczu po wczytaniu save
    just_loaded_save = False  # Flaga: czy właśnie wczytano save
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
        game_engine.current_player_obj = current_player  # <-- Ustaw aktualnego gracza dla panelu mapy

        # Otwieranie odpowiedniego panelu z numerem tury i czasem na turę
        if current_player.role == "Generał":
            app = PanelGenerala(turn_number=turn_manager.current_turn, ekonomia=current_player.economy, gracz=current_player, gracze=players, game_engine=game_engine)
        elif current_player.role == "Dowódca":
            app = PanelDowodcy(turn_number=turn_manager.current_turn, remaining_time=current_player.time_limit * 60, gracz=current_player, game_engine=game_engine)
        else:
            continue
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

        if hasattr(app, 'left_frame'):
            for child in app.left_frame.winfo_children():
                if isinstance(child, PanelGracza):
                    patch_on_load(child)

        # Aktualizacja pogody dla panelu
        if hasattr(app, 'update_weather'):
            app.update_weather(turn_manager.current_weather)

        # Aktualizacja raportu ekonomicznego tylko dla paneli generałów
        if isinstance(app, PanelGenerala):
            # Debug: bilans przed losowaniem
            start_points = current_player.economy.economic_points
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
            # --- Synchronizacja punktów ekonomicznych dowódcy z systemem ekonomii ---
            current_player.punkty_ekonomiczne = przydzielone_punkty

        try:
            app.mainloop()  # Uruchomienie panelu
        except Exception as e:
            print(f"Błąd: {e}")        # Przejście do następnej tury/podtury        # Przejście do kolejnego gracza i zwrócenie informacji czy zakończyła się pełna tura
        is_full_turn_end = turn_manager.next_turn()
          # --- ROZDZIEL PUNKTY Z KEY_POINTS tylko na koniec pełnej tury ---
        if is_full_turn_end:
            game_engine.process_key_points(players)
            
        # --- AKTUALIZUJ WIDOCZNOŚĆ NA KOŃCU KAŻDEJ TURY ---
        game_engine.update_all_players_visibility(players)
            
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
        just_loaded_save = False
        clear_temp_visibility(players)
        # --- KONIEC DODATKU ---

        # Sprawdzenie warunku zakończenia gry
        if hasattr(turn_manager, 'is_game_over') and turn_manager.is_game_over():
            break