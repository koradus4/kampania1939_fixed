import tkinter as tk
from PIL import Image, ImageTk  # Obsługa obrazów

class PanelDowodcyPolska1(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Panel Dowódcy Polska 1")
        self.state("zoomed")  # Maksymalizacja okna

        # Główna ramka podziału
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel (przyciski i licznik czasu)
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="lightgray")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Nagłówek
        self.label = tk.Label(self.left_frame, text="Panel Dowódcy Polska 1", font=("Arial", 16), bg="lightgray")
        self.label.pack(pady=10)

        # Licznik czasu
        self.timer_label = tk.Label(self.left_frame, text="Pozostały czas: 180 sekund", font=("Arial", 12), bg="lightgray")
        self.timer_label.pack(pady=10)

        # Przycisk zakończenia podtury
        self.end_turn_button = tk.Button(self.left_frame, text="Zakończ Podturę", command=self.end_turn)
        self.end_turn_button.pack(pady=20)

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

        # Inicjalizacja licznika czasu
        self.remaining_time = 180
        self.after(1000, self.update_timer)

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

    def update_timer(self):
        """Aktualizuje licznik czasu."""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Pozostały czas: {self.remaining_time} sekund")
            self.after(1000, self.update_timer)
        else:
            self.end_turn()

    def update_scrollregion(self, event):
        """Aktualizuje obszar przewijania mapy."""
        self.map_canvas.config(scrollregion=self.map_canvas.bbox("all"))

    def end_turn(self):
        """Kończy podturę."""
        self.destroy()

if __name__ == "__main__":
    app = PanelDowodcyPolska1()
    app.mainloop()