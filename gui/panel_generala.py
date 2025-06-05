import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_ekonomiczny import PanelEkonomiczny
from gui.panel_gracza import PanelGracza
from gui.zarzadzanie_punktami_ekonomicznymi import ZarzadzaniePunktamiEkonomicznymi
from engine.board import Board
from gui.panel_mapa import PanelMapa
from gui.token_info_panel import TokenInfoPanel

class PanelGenerala:
    def __init__(self, turn_number, ekonomia, gracz, gracze, game_engine):
        self.turn_number = turn_number
        self.ekonomia = ekonomia
        self.gracz = gracz
        self.gracze = gracze
        self.game_engine = game_engine

        # Tworzenie głównego okna
        self.root = tk.Tk()
        self.root.title(f"Panel Generała - {self.gracz.nation}")
        self.root.state("zoomed")

        # Wyświetlanie numeru tury
        self.turn_label = tk.Label(self.root, text=f"Tura: {self.turn_number}", font=("Arial", 14), bg="lightgray")
        self.turn_label.pack(pady=5)

        # Główna ramka podziału
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel (przyciski)
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="olive")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)

        # Panel gracza
        panel_gracza = PanelGracza(self.left_frame, self.gracz.name, self.gracz.image_path, self.game_engine, player=self.gracz)
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Przycisk zmiany tury (timer) NAD sekcję charakterystyki żetonu
        minutes = self.gracz.time_limit
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {minutes}:00", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 8), fill=tk.BOTH, expand=False)
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Panel informacyjny o żetonie
        self.token_info_panel = TokenInfoPanel(self.left_frame, height=120)
        self.token_info_panel.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie sekcji raportu ekonomicznego
        self.economy_panel = PanelEkonomiczny(self.left_frame)
        self.economy_panel.pack_forget()
        self.economy_panel.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH, expand=False)
        self.economy_panel.config(width=300)  # Ustawia stałą szerokość panelu ekonomicznego na 300 pikseli

        # Panel pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack_forget()
        self.weather_panel.pack(side=tk.BOTTOM, pady=1, fill=tk.BOTH, expand=False)

        # Przycisk 'punkty ekonomiczne' tuż nad panelem pogodowym (1px odstępu)
        self.points_frame = tk.Label(self.left_frame, text="Punkty ekonomiczne: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(side=tk.BOTTOM, pady=(0, 1), fill=tk.BOTH, expand=False)
        self.points_frame.bind("<Button-1>", self.toggle_support_sliders)
        self._support_sliders_visible = False  # Stan toggle

        # Inicjalizacja suwaków wsparcia dowódców
        commanders = [gracz for gracz in self.gracze if gracz.nation == self.gracz.nation and gracz.role == "Dowódca"]
        self.zarzadzanie_punktami_widget = ZarzadzaniePunktamiEkonomicznymi(
            self.left_frame,
            available_points=self.ekonomia.get_points()['economic_points'],
            commanders=[dowodca.id for dowodca in commanders],
            on_points_change=self._update_points_label_in_sliders
        )
        self.zarzadzanie_punktami_widget.pack_forget()  # Ukrycie suwaków na początku

        # Prawy panel (mapa)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # PanelMapa korzysta z silnika gry
        # Przekazujemy obiekt gracza do silnika, by umożliwić filtrowanie widoczności
        game_engine.current_player_obj = self.gracz
        self.panel_mapa = PanelMapa(
            parent=self.map_frame,
            game_engine=game_engine,
            bg_path="assets/mapa_globalna.jpg",
            player_nation=self.gracz.nation,
            width=800, height=600,
            token_info_panel=self.token_info_panel
        )
        self.panel_mapa.pack(fill="both", expand=True)
        # Dodaj obsługę podglądu żetonu prawym przyciskiem myszy (tylko dla generała)
        self.panel_mapa.canvas.bind("<Button-3>", self._on_right_click_token)

        # Przeliczenie czasu z minut na sekundy i zapisanie w zmiennej remaining_time
        self.remaining_time = self.gracz.time_limit * 60

        # Uruchomienie timera
        self.update_timer()

        # Przycisk VP
        btn_vp = tk.Button(self.left_frame, text="Punkty zwycięstwa (VP)", font=("Arial", 12, "bold"), bg="#6B8E23", fg="gold", relief=tk.RAISED, borderwidth=3, command=self.show_vp_window)
        btn_vp.pack(pady=(8, 2), fill=tk.X)

    def update_weather(self, weather_report):
        self.weather_panel.update_weather(weather_report)

    def update_economy(self, points=None):
        """Aktualizuje sekcję raportu ekonomicznego w panelu."""
        if points is None:
            points = self.ekonomia.get_points()['economic_points']
        special_points = self.ekonomia.get_points()['special_points']

        # --- DODANE: lista dowódców i ich punkty ---
        commanders = [g for g in self.gracze if g.nation == self.gracz.nation and g.role == "Dowódca"]
        commanders_report = ""
        for dowodca in commanders:
            # Pobierz aktualne punkty ekonomiczne dowódcy
            punkty = getattr(dowodca, 'punkty_ekonomiczne', None)
            if punkty is None and hasattr(dowodca, 'economy') and dowodca.economy is not None:
                punkty = dowodca.economy.get_points()['economic_points']
            commanders_report += f"\nDowódca {dowodca.id}: {punkty} pkt"

        # Aktualizacja tekstu w panelu ekonomicznym
        economy_report = (
            f"Punkty ekonomiczne: {points}\n"
            f"Punkty specjalne: {special_points}\n"
            f"--- Dowódcy ({self.gracz.nation}) ---{commanders_report}"
        )
        self.economy_panel.update_economy(economy_report)

        # Aktualizacja tekstu w sekcji punktów ekonomicznych
        self.points_frame.config(text=f"Punkty ekonomiczne: {points}")
        if hasattr(self, '_support_sliders_visible') and not self._support_sliders_visible:
            self.points_frame.config(text=f"Punkty ekonomiczne: {points}")

    def zarzadzanie_punktami(self, available_points):
        """Zarządza punktami ekonomicznymi i aktualizuje interfejs."""
        if not hasattr(self, 'zarzadzanie_punktami_widget'):
            # Inicjalizacja widgetu zarządzania punktami, jeśli nie istnieje
            self.zarzadzanie_punktami_widget = ZarzadzaniePunktamiEkonomicznymi(
                self.left_frame,
                available_points=available_points,
                commanders=[gracz.id for gracz in self.gracze if gracz.nacja == self.gracz.nacja and gracz.rola == "Dowódca"]
            )
            self.zarzadzanie_punktami_widget.pack(pady=10, fill=tk.BOTH, expand=False)
        else:
            # Aktualizacja dostępnych punktów w istniejącym widgetcie
            self.zarzadzanie_punktami_widget.refresh_available_points(available_points)

    def _update_points_label_in_sliders(self, new_value):
        if self._support_sliders_visible:
            self.points_frame.config(text=f"Zaakceptuj (pozostało: {new_value})")

    def toggle_support_sliders(self, event=None):
        # Otwieraj okno modalne z suwakami zamiast sekcji pod przyciskiem
        import tkinter as tk
        win = tk.Toplevel(self.root)
        win.title("Przydziel punkty ekonomiczne dowódcom")
        win.configure(bg="darkolivegreen")
        suwak_vars = {}
        dowodcy = [g for g in self.gracze if g.role == "Dowódca" and g.nation == self.gracz.nation]
        max_points = self.ekonomia.get_points()['economic_points']
        suma_var = tk.IntVar(value=0)

        def update_sum(*_):
            suma = sum(var.get() for var in suwak_vars.values())
            suma_var.set(suma)
            left = max_points - suma
            label_left.config(text=f"Pozostało do przydzielenia: {left}")
            btn_ok.config(state="normal" if left >= 0 else "disabled")

        for i, d in enumerate(dowodcy):
            tk.Label(win, text=f"{d.name}", bg="darkolivegreen", fg="white", font=("Arial", 12, "bold")).pack(pady=(10 if i==0 else 2, 2))
            var = tk.IntVar(value=0)
            suwak = tk.Scale(win, from_=0, to=max_points, orient=tk.HORIZONTAL, variable=var, bg="darkolivegreen", fg="white", font=("Arial", 11, "bold"), troughcolor="#556B2F", highlightthickness=0, relief=tk.RAISED, borderwidth=3, length=240)
            suwak.pack()
            suwak_vars[d.id] = var
            var.trace_add("write", update_sum)

        label_left = tk.Label(win, text=f"Pozostało do przydzielenia: {max_points}", bg="darkolivegreen", fg="white", font=("Arial", 11, "bold"))
        label_left.pack(pady=8)

        def zatwierdz():
            for d in dowodcy:
                przydzielone = suwak_vars[d.id].get()
                # Synchronizuj z systemem ekonomii dowódcy
                if not hasattr(d, 'economy') or d.economy is None:
                    from core.ekonomia import EconomySystem
                    d.economy = EconomySystem()
                d.economy.economic_points += przydzielone
                # Dla kompatybilności: synchronizuj atrybut punkty_ekonomiczne
                if not hasattr(d, 'punkty_ekonomiczne') or d.punkty_ekonomiczne is None:
                    d.punkty_ekonomiczne = 0
                d.punkty_ekonomiczne = d.economy.economic_points
            self.ekonomia.subtract_points(sum(var.get() for var in suwak_vars.values()))
            self.update_economy(self.ekonomia.get_points()['economic_points'])
            win.destroy()

        btn_ok = tk.Button(win, text="Akceptuj", command=zatwierdz, font=("Arial", 12, "bold"),
                           bg="#6B8E23", fg="white", activebackground="#7CA942", relief=tk.RAISED, borderwidth=3)
        btn_ok.pack(pady=10)

        win.transient(self.root)
        win.grab_set()
        win.wait_window()

    def update_timer(self):
        """Aktualizuje odliczanie czasu."""
        if self.root.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                minutes = self.remaining_time // 60
                seconds = self.remaining_time % 60
                self.timer_frame.config(text=f"Pozostały czas: {minutes}:{seconds:02d}")
                self.timer_id = self.root.after(1000, self.update_timer)
            else:
                self.end_turn()  # Automatyczne zakończenie tury po upływie czasu

    def reset_support_sliders(self):
        """Resetuje suwaki wsparcia dowódców po zakończeniu tury."""
        if hasattr(self, 'zarzadzanie_punktami_widget'):
            for commander in self.zarzadzanie_punktami_widget.commander_points.keys():
                slider = getattr(self.zarzadzanie_punktami_widget, f"{commander}_slider", None)
                if slider:
                    slider.set(0)
                self.zarzadzanie_punktami_widget.commander_points[commander] = 0
        self.zarzadzanie_punktami_widget.pack_forget()
        self._support_sliders_visible = False
        points = self.ekonomia.get_points()['economic_points']
        self.points_frame.config(text=f"Punkty ekonomiczne: {points}")

    def end_turn(self):
        """Kończy podturę i zamyka panel."""
        self.reset_support_sliders()  # Resetowanie suwaków wsparcia
        self.destroy()  # Zamiast self.root.destroy()

    def confirm_end_turn(self, event=None):
        """Potwierdza zakończenie tury."""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zakończyć turę przed czasem?"):
            self.end_turn()

    def destroy(self):
        """Anuluje timer i niszczy okno."""
        if hasattr(self, 'timer_id') and self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None  # Resetowanie identyfikatora timera
            except Exception as e:
                print(f"[ERROR] Nie udało się anulować timera: {e}")
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()

    def _on_right_click_token(self, event):
        # Podgląd żetonu pod prawym przyciskiem myszy (nie zmienia zaznaczenia do akcji)
        x = self.panel_mapa.canvas.canvasx(event.x)
        y = self.panel_mapa.canvas.canvasy(event.y)
        tokens = self.panel_mapa.tokens
        for token in tokens:
            if token.q is not None and token.r is not None:
                visible_ids = set()
                player = getattr(self.panel_mapa, 'player', None)
                if player and hasattr(player, 'visible_tokens') and hasattr(player, 'temp_visible_tokens'):
                    visible_ids = player.visible_tokens | player.temp_visible_tokens
                elif player and hasattr(player, 'visible_tokens'):
                    visible_ids = player.visible_tokens
                if token.id not in visible_ids:
                    continue
                tx, ty = self.panel_mapa.map_model.hex_to_pixel(token.q, token.r)
                hex_size = self.panel_mapa.map_model.hex_size
                if abs(x - tx) < hex_size // 2 and abs(y - ty) < hex_size // 2:
                    if self.token_info_panel is not None:
                        self.token_info_panel.show_token(token)
                    break

    def show_vp_window(self):
        """Wyświetla okno z bilansem i historią punktów zwycięstwa."""
        import tkinter as tk
        win = tk.Toplevel(self.root)
        win.title("Punkty zwycięstwa (VP)")
        win.configure(bg="#2e2e2e")
        vp = getattr(self.gracz, 'victory_points', 0)
        tk.Label(win, text=f"Twój bilans VP: {vp}", font=("Arial", 15, "bold"), fg="gold", bg="#2e2e2e").pack(pady=10)
        # Historia
        history = getattr(self.gracz, 'vp_history', [])
        frame = tk.Frame(win, bg="#2e2e2e")
        frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        if not history:
            tk.Label(frame, text="Brak zdarzeń.", fg="white", bg="#2e2e2e").pack()
        else:
            for entry in history[-20:][::-1]:
                txt = f"Tura {entry.get('turn','?')}: +{entry['amount']} VP za {entry['reason']} (żeton {entry['token_id']}, wróg: {entry['enemy']})"
                tk.Label(frame, text=txt, fg="white", bg="#2e2e2e", anchor="w", justify="left").pack(fill=tk.X)