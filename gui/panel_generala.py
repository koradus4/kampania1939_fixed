import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_ekonomiczny import PanelEkonomiczny
from gui.panel_gracza import PanelGracza
from gui.zarzadzanie_punktami_ekonomicznymi import ZarzadzaniePunktamiEkonomicznymi
from model.mapa import Mapa
from gui.panel_mapa import PanelMapa
from model.zetony import ZetonyMapy

class PanelGenerala:
    def __init__(self, turn_number, ekonomia, gracz, gracze):
        self.turn_number = turn_number
        self.ekonomia = ekonomia
        self.gracz = gracz
        self.gracze = gracze

        # Tworzenie głównego okna
        self.root = tk.Tk()
        self.root.title(f"Panel Generała - {self.gracz.nacja}")
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

        # Sekcja odliczania czasu
        minutes = self.gracz.czas
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {minutes}:00", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na ramkę z czasem jako przycisk zakończenia tury
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty ekonomiczne
        self.points_frame = tk.Label(self.left_frame, text="Punkty ekonomiczne: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)
        # Dodanie obsługi kliknięcia na "Punkty ekonomiczne" do otwierania suwaków wsparcia
        self.points_frame.bind("<Button-1>", lambda e: self.show_support_sliders())

        # Przycisk 'Zakup żetony'
        self.buy_tokens_button = tk.Button(
            self.left_frame,
            text="Zakup żetony",
            font=("Arial", 14, "bold"),
            bg="#6B8E23",
            fg="white",
            relief=tk.RAISED,
            borderwidth=4,
            command=self.open_token_shop
        )
        self.buy_tokens_button.pack(pady=(10, 10), fill=tk.BOTH, expand=False)

        # Dodanie sekcji raportu ekonomicznego
        self.economy_panel = PanelEkonomiczny(self.left_frame)
        self.economy_panel.pack_forget()
        self.economy_panel.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH, expand=False)
        self.economy_panel.config(width=300)  # Ustawia stałą szerokość panelu ekonomicznego na 300 pikseli

        # Panel pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack_forget()
        self.weather_panel.pack(side=tk.BOTTOM, pady=1, fill=tk.BOTH, expand=False)

        # Inicjalizacja suwaków wsparcia dowódców
        commanders = [gracz for gracz in self.gracze if gracz.nacja == self.gracz.nacja and gracz.rola == "Dowódca"]
        self.zarzadzanie_punktami_widget = ZarzadzaniePunktamiEkonomicznymi(
            self.left_frame,
            available_points=self.ekonomia.get_points()['economic_points'],
            commanders=[dowodca.numer for dowodca in commanders]
        )
        self.zarzadzanie_punktami_widget.pack_forget()  # Ukrycie suwaków na początku

        # Prawy panel (mapa)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Pobranie żetonów dla nacji generała
        zetony = ZetonyMapy()
        tokens_to_draw = zetony.get_tokens_for_nation(self.gracz.nacja)

        # Inicjalizacja modelu mapy i panelu mapy
        self.mapa_model = Mapa("assets/mapa_dane.json")
        self.panel_mapa = PanelMapa(
            parent=self.map_frame,
            map_model=self.mapa_model,
            bg_path="assets/mapa_globalna.jpg",
            player_nation=self.gracz.nacja,  # Przekazanie nacji gracza
            tokens_to_draw=tokens_to_draw,
            width=800, height=600
        )
        self.panel_mapa.pack(fill="both", expand=True)
        self.panel_mapa.bind_click_callback(self.on_map_click)

        # Przeliczenie czasu z minut na sekundy i zapisanie w zmiennej remaining_time
        self.remaining_time = self.gracz.czas * 60

        # Uruchomienie timera
        self.update_timer()

    def on_map_click(self, q, r):
        tile = self.mapa_model.get_tile(q, r)
        additional_info = f"\nSpawn: {tile.spawn_nation}" if tile.spawn_nation else ""
        tk.messagebox.showinfo(
            "Płytka",
            f"Hex: ({q},{r})\nTyp: {tile.terrain_key}\nRuch: {tile.move_mod}\nObrona: {tile.defense_mod}{additional_info}"
        )

    def update_weather(self, weather_report):
        self.weather_panel.update_weather(weather_report)

    def update_economy(self, points=None):
        """Aktualizuje sekcję raportu ekonomicznego w panelu."""
        if points is None:
            points = self.ekonomia.get_points()['economic_points']
        special_points = self.ekonomia.get_points()['special_points']

        # Aktualizacja tekstu w panelu ekonomicznym
        economy_report = f"Punkty ekonomiczne: {points}\nPunkty specjalne: {special_points}"
        self.economy_panel.update_economy(economy_report)

        # Aktualizacja tekstu w sekcji punktów ekonomicznych
        self.points_frame.config(text=f"Punkty ekonomiczne: {points}")

    def zarzadzanie_punktami(self, available_points):
        """Zarządza punktami ekonomicznymi i aktualizuje interfejs."""
        if not hasattr(self, 'zarzadzanie_punktami_widget'):
            # Inicjalizacja widgetu zarządzania punktami, jeśli nie istnieje
            self.zarzadzanie_punktami_widget = ZarzadzaniePunktamiEkonomicznymi(
                self.left_frame,
                available_points=available_points,
                commanders=[gracz.numer for gracz in self.gracze if gracz.nacja == self.gracz.nacja and gracz.rola == "Dowódca"]
            )
            self.zarzadzanie_punktami_widget.pack(pady=10, fill=tk.BOTH, expand=False)
        else:
            # Aktualizacja dostępnych punktów w istniejącym widgetcie
            self.zarzadzanie_punktami_widget.refresh_available_points(available_points)

    def show_support_sliders(self):
        """Wyświetla suwaki do zarządzania punktami wsparcia dowódców."""
        # Ukrycie klawisza "Wsparcie dowódców"
        if hasattr(self, 'support_button'):
            self.support_button.pack_forget()

        # Resetowanie wartości suwaków do 0 przy każdym otwarciu sekcji
        if hasattr(self, 'zarzadzanie_punktami_widget'):
            for commander in self.zarzadzanie_punktami_widget.commander_points.keys():
                slider = getattr(self.zarzadzanie_punktami_widget, f"{commander}_slider", None)
                if slider:
                    slider.set(0)
                self.zarzadzanie_punktami_widget.commander_points[commander] = 0

            # Wyświetlenie suwaków
            self.zarzadzanie_punktami_widget.pack(pady=10, fill=tk.BOTH, expand=False)

        # Dodanie przycisku "Akceptuj" tylko raz
        if not hasattr(self, 'accept_button'):
            self.accept_button = tk.Button(self.zarzadzanie_punktami_widget, text="Akceptuj", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", command=self.accept_support)
            self.accept_button.pack(pady=10, fill=tk.BOTH, expand=False)

    def accept_support(self):
        """Akceptuje przydzielone punkty wsparcia i aktualizuje ekonomię."""
        # Przekazanie punktów do dowódców
        for commander_id, pts in self.zarzadzanie_punktami_widget.commander_points.items():
            if pts > 0:
                for player in self.gracze:  # Iteracja po liście graczy
                    if player.numer == commander_id and player.rola == "Dowódca":
                        player.economy.economic_points += pts

        # Aktualizacja raportu ekonomicznego po rozdysponowaniu punktów
        self.ekonomia.subtract_points(sum(self.zarzadzanie_punktami_widget.commander_points.values()))
        self.update_economy()

        # Ukrycie suwaków
        self.zarzadzanie_punktami_widget.pack_forget()

        # Przywrócenie klawisza "Wsparcie dowódców"
        if hasattr(self, 'support_button'):
            self.support_button.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

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

    def open_token_shop(self):
        import tkinter as tk
        from edytory.token_shop import TokenEditor
        # Przekazanie liczby punktów ekonomicznych
        points = self.ekonomia.get_points()['economic_points']
        # Wyznacz listę dostępnych dowódców dla aktualnego generała
        commanders = [(gracz.numer, gracz.nacja) for gracz in self.gracze if gracz.nacja == self.gracz.nacja and gracz.rola == "Dowódca"]
        shop_window = tk.Toplevel(self.root)
        token_editor = TokenEditor(shop_window, available_points=points, available_commanders=commanders)
        shop_window.grab_set()

    def mainloop(self):
        self.root.mainloop()