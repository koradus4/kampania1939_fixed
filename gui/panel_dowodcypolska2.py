"""
Moduł zawierający klasę PanelDowodcyPolska2 odpowiedzialną za interfejs panelu dowódcy dla Polski (Gracz 2).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class PanelDowodcyPolska2(tk.Toplevel):
    """
    Panel Dowódcy Polska 2 - okno z mapą, zegarem i przyciskiem zakończenia tury.
    """
    def __init__(self, parent, next_turn_callback):
        super().__init__(parent)
        self.title("Panel Dowódcy Polska - Gracz 2")
        self.geometry("1280x800")
        self.configure(bg="darkolivegreen")
        self.remaining_time = 300  # 5 minut w sekundach
        self.next_turn_callback = next_turn_callback

        # Górna sekcja na przyciski
        self.top_frame = ttk.Frame(self, height=50)
        self.top_frame.pack(side="top", fill="x", padx=10, pady=5)

        # Przycisk "Zakończ turę"
        self.end_turn_button = ttk.Button(self.top_frame, text="Zakończ turę", command=self.end_turn)
        self.end_turn_button.pack(side="right", padx=10)

        # Mapa
        self.map_frame = ttk.Frame(self, style="Panel.TFrame")
        self.map_frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(self.map_frame, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Wczytaj obraz mapy
        try:
            map_image = Image.open(r"C:\Users\klif\kampania1939_fixed\gui\mapa_cyfrowa\mapa_dowodca2.jpg")
            self.tk_map = ImageTk.PhotoImage(map_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_map)
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Nie znaleziono pliku mapy: mapa_dowodca2.jpg")

        # Zegar
        self.time_frame = ttk.LabelFrame(self, text="Czas", style="MilitaryLabel.TLabelframe", height=100)
        self.time_frame.pack(side="right", fill="y", padx=10, pady=5)
        self.time_label = ttk.Label(self.time_frame, text="Pozostały czas: 5:00")
        self.time_label.pack(padx=10, pady=10)

        # Rozpocznij odliczanie czasu
        self.start_timer()

    def start_timer(self):
        """Rozpoczyna odliczanie czasu."""
        minutes, seconds = divmod(self.remaining_time, 60)
        self.time_label.config(text=f"Pozostały czas: {minutes:02}:{seconds:02}")
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.after(1000, self.start_timer)  # Odliczaj co sekundę
        else:
            messagebox.showinfo("Koniec czasu", "Czas dowódcy dobiegł końca!")
            self.end_turn()

    def end_turn(self):
        """Kończy turę dowódcy i przechodzi do następnej podtury."""
        self.destroy()
        if self.next_turn_callback:
            self.next_turn_callback()