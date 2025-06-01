import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_gracza import PanelGracza
from gui.panel_mapa import PanelMapa
from gui.token_info_panel import TokenInfoPanel

class PanelDowodcy:
    def __init__(self, turn_number, remaining_time, gracz, game_engine):
        self.turn_number = turn_number
        self.remaining_time = remaining_time
        self.gracz = gracz
        self.game_engine = game_engine

        self.wybrany_token = None  # INICJALIZACJA NA POCZĄTKU!

        # Tworzenie głównego okna
        self.root = tk.Tk()
        # Ustaw tytuł z numerem dowódcy i nacją
        self.root.title(f"Dowódca {self.gracz.id} – {self.gracz.nation}")
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
        panel_gracza = PanelGracza(self.left_frame, self.gracz.name, self.gracz.image_path)
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Pozostały czas NAD sekcją właściwości żetonu
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 8), fill=tk.BOTH, expand=False)
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty do odbioru NAD sekcją właściwości żetonu
        self.points_frame = tk.Label(self.left_frame, text="Punkty do odbioru: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 8), fill=tk.BOTH, expand=False)

        # Panel informacyjny o żetonie
        self.token_info_panel = TokenInfoPanel(self.left_frame)
        self.token_info_panel.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        # self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        # self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na ramkę z czasem
        # self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty ekonomiczne
        # self.points_frame = tk.Label(self.left_frame, text="Punkty do odbioru: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        # self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Panel pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack(pady=(10, 0), side=tk.BOTTOM, fill=tk.BOTH, expand=False)

        # Przycisk uzupełniania żetonu tuż nad panelem pogodowym
        self.btn_tankuj = None
        self.dodaj_przycisk_tankowania()
        if self.btn_tankuj is not None:
            self.btn_tankuj.pack_forget()
            self.btn_tankuj.pack(side=tk.BOTTOM, fill=tk.X)

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
            token_info_panel=self.token_info_panel,
            panel_dowodcy=self  # <--- przekazanie referencji
        )
        self.panel_mapa.pack(fill="both", expand=True)

        self.update_timer()

    def update_timer(self):
        if self.root.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.timer_frame.config(text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}")
                self.timer_id = self.root.after(1000, self.update_timer)  # Przypisanie identyfikatora timera
            else:
                self.destroy()

    def update_weather(self, weather_report):
        self.weather_panel.update_weather(weather_report)

    def update_economy(self, points):
        self.points_frame.config(text=f"Punkty do odbioru: {points}")

    def confirm_end_turn(self, event):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zakończyć turę przed czasem?"):
            self.destroy()

    def end_turn(self):
        self.destroy()

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

    def uzupelnij_zeton(self, token, max_fuel_do_uzupelnienia, max_combat_do_uzupelnienia, max_punkty, callback=None):
        """Okno uzupełniania żetonu: dwa suwaki (paliwo, zasoby bojowe), łączny koszt nie przekracza punktów ekonomicznych."""
        import tkinter as tk
        win = tk.Toplevel(self.root)
        win.title(f"Uzupełnianie: {token.stats.get('label', token.id)}")
        win.geometry("370x270")
        win.configure(bg="darkolivegreen")
        # Nagłówek
        tk.Label(
            win,
            text=f"Uzupełnianie żetonu: {token.stats.get('label', token.id)}",
            font=("Arial", 13, "bold"),
            bg="darkolivegreen",
            fg="white"
        ).pack(pady=10)
        # Aktualne wartości
        current_fuel = getattr(token, 'currentFuel', token.maxFuel)
        max_fuel = getattr(token, 'maxFuel', token.stats.get('maintenance', 0))
        current_combat = getattr(token, 'combat_value', token.stats.get('combat_value', 0))
        max_combat = token.stats.get('combat_value', 0)
        # Suwaki
        var_fuel = tk.IntVar(value=max_fuel_do_uzupelnienia)
        var_combat = tk.IntVar(value=max_combat_do_uzupelnienia)
        # Funkcja ograniczająca sumę
        def on_slider_change(*_):
            fuel = var_fuel.get()
            combat = var_combat.get()
            suma = fuel + combat
            if suma > max_punkty:
                # Cofnij ostatnią zmianę
                if fuel > prev_fuel[0]:
                    var_fuel.set(max(0, max_punkty - combat))
                else:
                    var_combat.set(max(0, max_punkty - fuel))
            prev_fuel[0] = var_fuel.get()
            prev_combat[0] = var_combat.get()
            label_sum.config(text=f"Łączny koszt: {var_fuel.get() + var_combat.get()} / {max_punkty}")
        prev_fuel = [var_fuel.get()]
        prev_combat = [var_combat.get()]
        slider_fuel = tk.Scale(
            win,
            from_=0,
            to=max_fuel_do_uzupelnienia,
            orient=tk.HORIZONTAL,
            label="Paliwo do uzupełnienia",
            variable=var_fuel,
            bg="darkolivegreen",
            fg="white",
            font=("Arial", 11, "bold"),
            troughcolor="#556B2F",
            highlightthickness=0,
            relief=tk.RAISED,
            borderwidth=3,
            length=240,
            command=lambda _: on_slider_change()
        )
        slider_fuel.pack(pady=(5,0), fill=tk.X, padx=20)
        slider_combat = tk.Scale(
            win,
            from_=0,
            to=max_combat_do_uzupelnienia,
            orient=tk.HORIZONTAL,
            label="Zasoby bojowe do uzupełnienia",
            variable=var_combat,
            bg="darkolivegreen",
            fg="white",
            font=("Arial", 11, "bold"),
            troughcolor="#556B2F",
            highlightthickness=0,
            relief=tk.RAISED,
            borderwidth=3,
            length=240,
            command=lambda _: on_slider_change()
        )
        slider_combat.pack(pady=(5,0), fill=tk.X, padx=20)
        label_sum = tk.Label(win, text=f"Łączny koszt: {var_fuel.get() + var_combat.get()} / {max_punkty}", font=("Arial", 11, "bold"), bg="darkolivegreen", fg="white")
        label_sum.pack(pady=(5,0))
        def zatwierdz():
            ile_fuel = var_fuel.get()
            ile_combat = var_combat.get()
            token.currentFuel += ile_fuel
            if hasattr(token, 'combat_value'):
                token.combat_value += ile_combat
            else:
                token.combat_value = ile_combat
            if callback:
                callback(ile_fuel, ile_combat)
            win.destroy()
        btn = tk.Button(
            win,
            text="Akceptuj",
            command=zatwierdz,
            font=("Arial", 12, "bold"),
            bg="saddlebrown",
            fg="white",
            relief=tk.RAISED,
            borderwidth=4,
            activebackground="#8B5A2B",
            activeforeground="white"
        )
        btn.pack(pady=10)
        win.transient(self.root)
        win.grab_set()
        win.wait_window()

    def dodaj_przycisk_tankowania(self):
        # Przycisk uzupełniania w panelu dowódcy
        btn = tk.Button(
            self.left_frame,
            text="Uzupełnij żeton",
            font=("Arial", 14, "bold"),
            bg="#6B8E23",
            fg="white",
            relief=tk.RAISED,
            borderwidth=4,
            activebackground="#556B2F",
            activeforeground="white"
        )
        btn.pack(pady=8, fill=tk.X)
        def on_uzupelnij():
            token = getattr(self, 'wybrany_token', None)
            if not token:
                messagebox.showinfo("Uzupełnianie", "Najpierw wybierz żeton do uzupełnienia!")
                return
            expected_owner = f"{self.gracz.id} ({self.gracz.nation})"
            if token.owner != expected_owner:
                messagebox.showinfo("Uzupełnianie", f"Możesz uzupełniać tylko własne żetony! (owner={token.owner}, expected={expected_owner})")
                return
            punkty = getattr(self.gracz, 'punkty_ekonomiczne', 0)
            max_fuel = getattr(token, 'maxFuel', token.stats.get('maintenance', 0))
            max_fuel_do_uzupelnienia = max(0, min(max_fuel - getattr(token, 'currentFuel', max_fuel), punkty))
            max_combat = token.stats.get('combat_value', 0)
            current_combat = getattr(token, 'combat_value', max_combat)
            max_combat_do_uzupelnienia = max(0, min(max_combat - current_combat, punkty))
            max_lacznie = min(punkty, max_fuel_do_uzupelnienia + max_combat_do_uzupelnienia)
            if max_lacznie <= 0:
                messagebox.showinfo("Uzupełnianie", "Brak możliwości uzupełnienia (pełny bak, pełne zasoby lub brak punktów)")
                return
            def callback(ile_fuel, ile_combat):
                self.gracz.punkty_ekonomiczne -= (ile_fuel + ile_combat)
                if hasattr(self, 'points_frame'):
                    self.points_frame.config(text=f"Punkty do odbioru: {self.gracz.punkty_ekonomiczne}")
                if hasattr(self, 'token_info_panel'):
                    self.token_info_panel.show_token(token)
            self.uzupelnij_zeton(token, max_fuel_do_uzupelnienia, max_combat_do_uzupelnienia, max_lacznie, callback)
        btn.config(command=on_uzupelnij)
        self.btn_tankuj = btn