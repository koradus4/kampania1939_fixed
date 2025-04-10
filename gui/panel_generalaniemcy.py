"""
Moduł zawierający klasę PanelGenerala odpowiedzialną za interfejs panelu żetonów dla Generała (np. niemieckie jednostki).
"""
from gui.panel_dowodcyniemcy1 import PanelDowodcyNiemcy1  # Import panelu pierwszego dowódcy Niemiec
from gui.panel_dowodcyniemcy2 import PanelDowodcyNiemcy2  # Import panelu drugiego dowódcy Niemiec
from gui.panel_generalapolska import OknoGeneralaPolska  # Import panelu generała Polski
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from model import zasoby
import os  # Dodaj import os, jeśli go brakuje

class OknoGenerala(tk.Toplevel):
    """
    Okno Generała - osobne okno z globalną mapą, sekcjami ekonomicznymi, rozkazami i czasem.
    """
    def __init__(self, parent, nation, economy_system):
        super().__init__(parent)
        self.title(f"Panel Generała - {nation}")
        self.geometry("1280x800")
        self.configure(bg="darkolivegreen")
        self.nation = nation
        self.economy_system = economy_system
        self.remaining_time = 300  # 5 minut w sekundach

        # Mapa globalna
        self.map_frame = ttk.Frame(self, style="Panel.TFrame")
        self.map_frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(self.map_frame, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Wczytaj obraz mapy
        try:
            map_image = Image.open(zasoby.MAP_PATH)
            self.tk_map = ImageTk.PhotoImage(map_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_map)
        except FileNotFoundError:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku mapy: {zasoby.MAP_PATH}")

        # Sekcja ekonomiczna
        self.economy_frame = ttk.LabelFrame(self, text="Ekonomia", style="MilitaryLabel.TLabelframe", height=200)
        self.economy_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.economy_label = ttk.Label(self.economy_frame, text=self.economy_system.generate_report(self.nation))
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
        self.end_turn_button = ttk.Button(self, text="Zakończ turę", command=self.end_turn)
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
            self.end_turn()

    def end_turn(self):
        """Kończy turę generała i zamyka okno."""
        self.destroy()

class OknoGeneralaNiemcy(tk.Toplevel):
    """
    Okno Generała Niemiec - osobne okno z globalną mapą, sekcjami ekonomicznymi, rozkazami i czasem.
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
        self.economy_label = ttk.Label(self.economy_frame, text=self.economy_system.generate_report("Niemcy"))
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

        # Funkcja callback po zakończeniu tury pierwszego dowódcy Niemiec
        def on_dowodca_turn_end_1():
            print("Tura pierwszego dowódcy Niemiec zakończona!")  # Komunikat w konsoli
            PanelDowodcyNiemcy2(self.master, next_turn_callback=on_dowodca_turn_end_2)  # Otwórz panel drugiego dowódcy Niemiec

        # Funkcja callback po zakończeniu tury drugiego dowódcy Niemiec
        def on_dowodca_turn_end_2():
            print("Tura drugiego dowódcy Niemiec zakończona!")  # Komunikat w konsoli
            messagebox.showinfo("Koniec tury", "Tura Niemiec dobiegła końca!")
            
            # Otwórz panel generała Polski
            OknoGeneralaPolska(self.master, economy_system=self.economy_system, nation="Polska")

        # Otwórz panel pierwszego dowódcy Niemiec z callbackiem
        PanelDowodcyNiemcy1(self.master, next_turn_callback=on_dowodca_turn_end_1)
