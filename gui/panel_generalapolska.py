"""
Moduł zawierający klasę OknoGeneralaPolska odpowiedzialną za interfejs panelu dla Generała Polski.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from gui.panel_dowodcypolska1 import PanelDowodcyPolska1  # Import panelu dowódcy
from gui.panel_dowodcypolska2 import PanelDowodcyPolska2  # Import panelu drugiego dowódcy
from gui.panel_generalaniemcy import OknoGeneralaNiemcy  # Import panelu generała Niemiec

class OknoGeneralaPolska(tk.Toplevel):
    """
    Okno Generała Polska - osobne okno z globalną mapą, sekcjami ekonomicznymi, rozkazami i czasem.
    """
    def __init__(self, parent, economy_system, nation):
        super().__init__(parent)
        self.title(f"Panel Generała - {nation}")
        self.geometry("1280x800")
        self.configure(bg="darkolivegreen")
        self.economy_system = economy_system
        self.nation = nation  # Przechowaj nazwę nacji
        self.remaining_time = 300  # 5 minut w sekundach

        # Ścieżka do mapy
        map_path = os.path.join(os.getcwd(), "gui", "mapa_cyfrowa", "mapa_hex.jpg")

        # Mapa globalna
        self.map_frame = ttk.Frame(self, style="Panel.TFrame")
        self.map_frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(self.map_frame, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Wczytaj obraz mapy
        try:
            map_image = Image.open(map_path)
            self.tk_map = ImageTk.PhotoImage(map_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_map)
        except FileNotFoundError:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku mapy: {map_path}")

        # Sekcja ekonomiczna
        self.economy_frame = ttk.LabelFrame(self, text="Ekonomia", style="MilitaryLabel.TLabelframe", height=200)
        self.economy_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.economy_label = ttk.Label(self.economy_frame, text=self.economy_system.generate_report("Polska"))
        self.economy_label.pack(padx=10, pady=10)

        # Sekcja rozkazów
        self.orders_frame = ttk.LabelFrame(self, text="Rozkazy", style="MilitaryLabel.TLabelframe", height=200)
        self.orders_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.orders_label = ttk.Label(self.orders_frame, text="Brak rozkazów")
        self.orders_label.pack(padx=10, pady=10)

        # Sekcja czasu
        self.time_frame = ttk.LabelFrame(self, text="Czas", style="MilitaryLabel.TLabelframe", height=100)
        self.time_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.time_label = ttk.Label(self.time_frame, text="Pozostały czas: 5:00")
        self.time_label.pack(padx=10, pady=10)

        # Przycisk zakończenia tury
        self.end_turn_button = ttk.Button(self, text="Zakończ turę", command=self.close_window)
        self.end_turn_button.pack(side="bottom", pady=20)

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
            messagebox.showinfo("Koniec czasu", "Czas generała dobiegł końca!")
            self.close_window()

    def close_window(self):
        """Zamyka okno i otwiera panel dowódcy."""
        self.destroy()  # Zamknij okno generała

        # Funkcja callback po zakończeniu tury pierwszego dowódcy
        def on_dowodca_turn_end_1():
            print("Tura pierwszego dowódcy zakończona!")  # Komunikat w konsoli
            PanelDowodcyPolska2(self.master, next_turn_callback=on_dowodca_turn_end_2)  # Otwórz panel drugiego dowódcy

        # Funkcja callback po zakończeniu tury drugiego dowódcy
        def on_dowodca_turn_end_2():
            print("Tura drugiego dowódcy zakończona!")  # Komunikat w konsoli
            messagebox.showinfo("Koniec tury", "Tura Polski dobiegła końca!")
            
            # Otwórz panel generała Niemiec
            OknoGeneralaNiemcy(self.master, economy_system=self.economy_system, nation="Niemcy")

        # Otwórz panel pierwszego dowódcy z callbackiem
        PanelDowodcyPolska1(self.master, next_turn_callback=on_dowodca_turn_end_1)