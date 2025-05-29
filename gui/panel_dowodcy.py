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
            token_info_panel=self.token_info_panel
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