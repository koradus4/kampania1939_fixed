import tkinter as tk
from PIL import Image, ImageTk  # Obsługa obrazów
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_ekonomiczny import PanelEkonomiczny

class PanelGeneralaPolska(tk.Tk):
    def __init__(self, turn_number, ekonomia, gracz):
        super().__init__()
        self.title("Panel Generała Polska")
        self.state("zoomed")  # Maksymalizacja okna
        self.ekonomia = ekonomia  # Przechowywanie obiektu ekonomii

        # Pobranie czasu na podturę z obiektu Gracz
        self.remaining_time = gracz.czas * 60  # Czas na podturę w sekundach

        # Wyświetlanie numeru tury
        self.turn_label = tk.Label(self, text=f"Tura: {turn_number}", font=("Arial", 14), bg="lightgray")
        self.turn_label.pack(pady=5)

        # Główna ramka podziału
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel (przyciski)
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="olive")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)  # Zapobiega dynamicznej zmianie rozmiaru panelu
        self.left_frame.config(width=298)  # Ustawia stałą szerokość panelu na 298 pikseli

        # Dodano obramowanie dla nazwiska generała
        self.general_name_label = tk.Label(self.left_frame, text="Marszałek Polski Edward Rydz-Śmigły", font=("Arial", 12), bg="white", relief=tk.SUNKEN, borderwidth=2, wraplength=280, justify=tk.CENTER)
        self.general_name_label.pack(pady=5, fill=tk.BOTH, expand=False)

        # Dodano ramkę na zdjęcie generała
        self.general_photo_frame = tk.Frame(self.left_frame, width=298, height=298, bg="white", relief=tk.SUNKEN, borderwidth=2)
        self.general_photo_frame.pack(pady=10, fill=tk.BOTH, expand=False)

        # Wczytanie zdjęcia generała i dopasowanie do ramki
        general_image_path = "gui/images/Marszałek Polski Edward Rydz-Śmigły .png"
        self.general_image = Image.open(general_image_path).resize((298, 298), Image.Resampling.LANCZOS)
        self.general_photo = ImageTk.PhotoImage(self.general_image)
        general_photo_label = tk.Label(self.general_photo_frame, image=self.general_photo, bg="white")
        general_photo_label.image = self.general_photo  # Referencja, aby obraz nie został usunięty przez GC
        general_photo_label.pack()

        # Sekcja odliczania czasu
        self.timer_frame = tk.Frame(self.left_frame, bg="white", relief=tk.SUNKEN, borderwidth=2, width=298)
        self.timer_frame.pack(pady=15, fill=tk.BOTH, expand=False)

        self.timer_label = tk.Label(self.timer_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14), bg="white")
        self.timer_label.pack(pady=5)

        # Przesunięto przycisk "Zakończ Podturę" poniżej ramki z czasem
        self.end_turn_button = tk.Button(self.left_frame, text="Zakończ Podturę", command=self.end_turn)
        self.end_turn_button.pack(pady=25)

        # Uruchomienie timera
        self.update_timer()

        # Przeniesienie ramki dla raportu ekonomicznego bezpośrednio nad raport pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack(pady=10, side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        self.weather_panel.config(width=300, height=60)  # Ustawia stałą wysokość panelu pogodowego na 60 pikseli

        self.economy_panel = PanelEkonomiczny(self.left_frame)
        self.economy_panel.pack(pady=10, side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        self.economy_panel.config(width=300)  # Ustawia stałą szerokość panelu ekonomicznego na 300 pikseli

        # Prawy panel (mapa z suwakami)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas z mapą
        self.map_canvas = tk.Canvas(self.map_frame, bg="gray", scrollregion=(0, 0, 2000, 2000))
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        self.map_canvas.config(scrollregion=(0, 0, 0, 0))  # Usuwa suwaki

        # Suwaki
        self.h_scroll = tk.Scrollbar(self.map_frame, orient=tk.HORIZONTAL, command=self.map_canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll = tk.Scrollbar(self.map_frame, orient=tk.VERTICAL, command=self.map_canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.map_canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Konfiguracja siatki w map_frame
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)

        self.map_canvas.bind("<Configure>", self.update_scrollregion)

        # Wczytanie mapy
        self.load_map("gui/mapa_cyfrowa/mapa_globalna.jpg")

        # Obsługa przesuwania myszką
        self.map_canvas.bind("<ButtonPress-1>", self.start_pan)
        self.map_canvas.bind("<B1-Motion>", self.do_pan)

        # Debugowanie
        print(f"[DEBUG] Szerokość panelu pogodowego: {self.weather_panel.winfo_width()}")
        print(f"[DEBUG] Szerokość panelu ekonomicznego: {self.economy_panel.winfo_width()}")
        print(f"[DEBUG] Scrollregion mapy: {self.map_canvas.cget('scrollregion')}")

    def load_map(self, map_path):
        """Wczytuje mapę i wyświetla ją na canvasie."""
        try:
            self.map_image = Image.open(map_path)
            self.map_photo = ImageTk.PhotoImage(self.map_image)
            self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_photo)
        except Exception as e:
            print(f"Nie udało się wczytać mapy: {e}")

    def start_pan(self, event):
        """Rozpoczyna przesuwanie mapy myszką."""
        self.map_canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        """Przesuwa mapę myszką."""
        self.map_canvas.scan_dragto(event.x, event.y, gain=1)

    def update_scrollregion(self, event):
        """Aktualizuje obszar przewijania mapy."""
        self.map_canvas.config(scrollregion=self.map_canvas.bbox("all"))
        print(f"[DEBUG] Scrollregion mapy: {self.map_canvas.cget('scrollregion')}")

    def update_timer(self):
        """Aktualizuje odliczanie czasu."""
        if self.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.timer_label.config(text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}")
                self.timer_id = self.after(1000, self.update_timer)
            else:
                self.end_turn()
        else:
            if hasattr(self, 'timer_id'):
                self.after_cancel(self.timer_id)

    def end_turn(self):
        """Kończy podturę."""
        self.destroy()

    def destroy(self):
        super().destroy()

    def update_weather(self, weather_report):
        """Aktualizuje sekcję raportu pogodowego w panelu."""
        print(f"[DEBUG] PanelGeneralaPolska: Otrzymano raport pogodowy: {weather_report}")
        self.weather_panel.update_weather(weather_report)

    def update_economy(self):
        """Aktualizuje sekcję raportu ekonomicznego w panelu."""
        economy_report = f"Punkty ekonomiczne: {self.ekonomia.get_points()['economic_points']}\nPunkty specjalne: {self.ekonomia.get_points()['special_points']}"
        self.economy_panel.update_economy(economy_report)

    def buy_time(self):
        """Logika kupowania dodatkowego czasu."""
        print("Kupiono dodatkowy czas!")

if __name__ == "__main__":
    class MockEkonomia:
        def get_points(self, nation=None):
            return {"economic_points": 100, "special_points": 50}

    class MockGracz:
        def __init__(self):
            self.czas = 5

    ekonomia = MockEkonomia()
    gracz = MockGracz()
    app = PanelGeneralaPolska(turn_number=1, ekonomia=ekonomia, gracz=gracz)
    app.mainloop()