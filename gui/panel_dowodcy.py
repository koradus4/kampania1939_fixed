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

        # Panel informacyjny o żetonie
        self.token_info_panel = TokenInfoPanel(self.left_frame)
        self.token_info_panel.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na ramkę z czasem
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty ekonomiczne
        self.points_frame = tk.Label(self.left_frame, text="Punkty do odbioru: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Panel pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack(pady=10, side=tk.BOTTOM, fill=tk.BOTH, expand=False)

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
        self.dodaj_przycisk_tankowania()

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

    def tankuj_zeton(self, token, max_do_tankowania, callback=None):
        """Wywołuje okno tankowania dla wybranego żetonu. max_do_tankowania = ile można dolać (ograniczone przez maxFuel i punkty ekonomiczne dowódcy)."""
        import tkinter as tk
        win = tk.Toplevel(self.root)
        win.title(f"Tankowanie: {token.stats.get('label', token.id)}")
        win.geometry("320x180")
        tk.Label(win, text=f"Tankowanie żetonu: {token.stats.get('label', token.id)}", font=("Arial", 12)).pack(pady=8)
        current = getattr(token, 'currentFuel', token.maxFuel)
        max_fuel = getattr(token, 'maxFuel', token.stats.get('maintenance', 0))
        ile_mozna = min(max_fuel - current, max_do_tankowania)
        var = tk.IntVar(value=ile_mozna)
        slider = tk.Scale(win, from_=0, to=ile_mozna, orient=tk.HORIZONTAL, label="Ilość paliwa do uzupełnienia", variable=var)
        slider.pack(pady=10, fill=tk.X, padx=20)
        def zatwierdz():
            ile = var.get()
            token.currentFuel += ile
            if callback:
                callback(ile)
            win.destroy()
        btn = tk.Button(win, text="Akceptuj", command=zatwierdz)
        btn.pack(pady=10)
        win.transient(self.root)
        win.grab_set()
        win.wait_window()

    def dodaj_przycisk_tankowania(self):
        # Przycisk tankowania w panelu dowódcy
        btn = tk.Button(self.left_frame, text="Tankuj żeton", font=("Arial", 12, "bold"), bg="#e6e600", fg="black")
        btn.pack(pady=8, fill=tk.X)
        def on_tankuj():
            # Pobierz wybrany żeton (np. z panelu info lub mapy)
            token = getattr(self, 'wybrany_token', None)
            print(f"[DEBUG] wybrany_token: {token}")
            if token:
                print(f"[DEBUG] token.id={token.id}, token.owner={token.owner}, gracz.id={self.gracz.id}, gracz.nation={self.gracz.nation}")
            if not token:
                from tkinter import messagebox
                messagebox.showinfo("Tankowanie", "Najpierw wybierz żeton do tankowania!")
                return
            # Sprawdź czy to żeton tego dowódcy
            expected_owner = f"{self.gracz.id} ({self.gracz.nation})"
            if token.owner != expected_owner:
                print(f"[DEBUG] Nie możesz tankować żetonu: owner={token.owner}, expected_owner={expected_owner}")
                from tkinter import messagebox
                messagebox.showinfo("Tankowanie", f"Możesz tankować tylko własne żetony! (owner={token.owner}, expected={expected_owner})")
                return
            # Punkty ekonomiczne dowódcy
            punkty = getattr(self.gracz, 'punkty_ekonomiczne', 0)
            max_do_tankowania = min(token.maxFuel - token.currentFuel, punkty)
            print(f"[DEBUG] max_do_tankowania={max_do_tankowania}, punkty={punkty}, maxFuel={token.maxFuel}, currentFuel={token.currentFuel}")
            if max_do_tankowania <= 0:
                from tkinter import messagebox
                messagebox.showinfo("Tankowanie", "Brak możliwości tankowania (pełny bak lub brak punktów)")
                return
            def callback(ile):
                self.gracz.punkty_ekonomiczne -= ile
                # Odśwież panel punktów ekonomicznych
                if hasattr(self, 'points_frame'):
                    self.points_frame.config(text=f"Punkty do odbioru: {self.gracz.punkty_ekonomiczne}")
                # Odśwież panel info żetonu
                if hasattr(self, 'token_info_panel'):
                    self.token_info_panel.show_token(token)
            self.tankuj_zeton(token, max_do_tankowania, callback)
        btn.config(command=on_tankuj)
        self.btn_tankuj = btn