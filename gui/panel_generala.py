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
        panel_gracza = PanelGracza(self.left_frame, self.gracz.name, self.gracz.image_path)
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Panel informacyjny o żetonie
        self.token_info_panel = TokenInfoPanel(self.left_frame)
        self.token_info_panel.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        minutes = self.gracz.time_limit
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {minutes}:00", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na ramkę z czasem jako przycisk zakończenia tury
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty ekonomiczne
        self.points_frame = tk.Label(self.left_frame, text="Punkty ekonomiczne: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)
        self.points_frame.bind("<Button-1>", self.toggle_support_sliders)
        self._support_sliders_visible = False  # Stan toggle

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

        # Przeliczenie czasu z minut na sekundy i zapisanie w zmiennej remaining_time
        self.remaining_time = self.gracz.time_limit * 60

        # Uruchomienie timera
        self.update_timer()

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
        if not self._support_sliders_visible:
            # Otwórz panel suwaków
            print(f"[DEBUG][SLIDERS] Otwieram suwaki. Dostępne punkty ekonomiczne generała: {self.ekonomia.get_points()['economic_points']}")
            for commander in self.zarzadzanie_punktami_widget.commander_points.keys():
                slider = getattr(self.zarzadzanie_punktami_widget, f"{commander}_slider", None)
                if slider:
                    slider.set(0)
                self.zarzadzanie_punktami_widget.commander_points[commander] = 0
            self.zarzadzanie_punktami_widget.pack(pady=10, fill=tk.BOTH, expand=False)
            left = self.ekonomia.get_points()['economic_points']
            self._support_sliders_visible = True  # <-- PRZED callbackiem!
            if self.zarzadzanie_punktami_widget.on_points_change:
                self.zarzadzanie_punktami_widget.on_points_change(left)
            self.points_frame.config(text=f"Zaakceptuj (pozostało: {left})")
            print(f"[DEBUG][SLIDERS] Po otwarciu suwaków można rozdzielić: {left}")
        else:
            # Akceptuj i zamknij panel suwaków
            print(f"[DEBUG][SLIDERS] Akceptuję i zamykam suwaki. Punkty do przekazania: {self.zarzadzanie_punktami_widget.commander_points}")
            self.zarzadzanie_punktami_widget.accept_final_points()
            for commander_id, pts in self.zarzadzanie_punktami_widget.commander_points.items():
                if pts > 0:
                    for player in self.gracze:
                        if player.id == commander_id and player.role == "Dowódca":
                            player.economy.economic_points += pts
            przekazane = sum(self.zarzadzanie_punktami_widget.commander_points.values())
            print(f"[DEBUG][SLIDERS] Suma przekazanych punktów: {przekazane}")
            self.ekonomia.subtract_points(przekazane)
            print(f"[DEBUG][SLIDERS] Po akceptacji, punkty ekonomiczne generała: {self.ekonomia.get_points()['economic_points']}")
            self.update_economy()
            self.zarzadzanie_punktami_widget.pack_forget()
            self._support_sliders_visible = False
            # Przywróć etykietę z aktualną wartością
            points = self.ekonomia.get_points()['economic_points']
            self.points_frame.config(text=f"Punkty ekonomiczne: {points}")

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