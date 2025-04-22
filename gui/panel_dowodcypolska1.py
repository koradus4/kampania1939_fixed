import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Obsługa obrazów
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_gracza import PanelGracza

class PanelDowodcyPolska1(tk.Tk):
    def __init__(self, turn_number, remaining_time):
        super().__init__()
        self.remaining_time = remaining_time
        self.title("Panel Dowódcy Polska 1")
        self.state("zoomed")  # Maksymalizacja okna

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

        # Zastąpienie kodu odpowiedzialnego za zdjęcie i nazwisko gracza
        panel_gracza = PanelGracza(self.left_frame, "c:/Users/klif/kampania1939_fixed/gui/images/Generał Tadeusz Kutrzeba.png", "Generał Tadeusz Kutrzeba")
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4, width=298, cursor="hand2")
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodano obsługę kliknięcia na ramkę z czasem
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Dodano obsługę zmiany wyglądu przy najechaniu myszką
        self.timer_frame.bind("<Enter>", lambda e: self.timer_frame.config(bg="#556B2F"))
        self.timer_frame.bind("<Leave>", lambda e: self.timer_frame.config(bg="#6B8E23"))

        # Dodanie okna do odbioru punktów w odpowiednim miejscu
        self.points_frame = tk.Label(self.left_frame, text="Punkty do odbioru: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Sekcja raportu pogodowego
        # Inicjalizacja panelu pogodowego
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack(pady=10, side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        self.weather_panel.config(height=60)  # Ustawia stałą wysokość panelu pogodowego na 60 pikseli

        # Zmniejszono przerwę między dolną częścią panelu pogodowego a dolną krawędzią okna do 1 piksela
        self.weather_panel.pack_configure(pady=1)

        # Prawy panel (mapa z suwakami)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas z mapą
        self.map_canvas = tk.Canvas(self.map_frame, bg="gray", scrollregion=(0, 0, 2000, 2000))
        self.map_canvas.grid(row=0, column=0, sticky="nsew")

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
        self.load_map("gui/mapa_cyfrowa/mapa_dowodca1.jpg")

        # Obsługa przesuwania myszką
        self.map_canvas.bind("<ButtonPress-1>", self.start_pan)
        self.map_canvas.bind("<B1-Motion>", self.do_pan)

        # Uruchomienie timera
        self.update_timer()

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

    def destroy(self):
        if hasattr(self, 'timer_id'):
            self.after_cancel(self.timer_id)
        super().destroy()

    def end_turn(self):
        """Kończy podturę."""
        self.destroy()

    def confirm_end_turn(self, event):
        """Potwierdza zakończenie tury."""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zakończyć turę przed czasem?"):
            self.end_turn()

    def update_weather(self, weather_report):
        """Aktualizuje sekcję raportu pogodowego w panelu."""
        self.weather_panel.update_weather(weather_report)

    def update_timer(self):
        if self.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.timer_frame.config(text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}")
                self.timer_id = self.after(1000, self.update_timer)
            else:
                self.end_turn()

if __name__ == "__main__":
    app = PanelDowodcyPolska1(turn_number=1, remaining_time=60)
    app.mainloop()