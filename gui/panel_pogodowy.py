import tkinter as tk

class PanelPogodowy(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray", relief=tk.SUNKEN, borderwidth=2)  # Dodano obramowanie

        # Nagłówek panelu
        self.header = tk.Label(self, text="Raport Pogodowy", font=("Arial", 12), bg="lightgray")
        self.header.pack(pady=2)

        # Obszar tekstowy bez przewijania
        self.text_label = tk.Label(self, text="", wraplength=250, justify=tk.LEFT, bg="white", anchor="nw")
        self.text_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_weather(self, weather_report):
        """Aktualizuje zawartość raportu pogodowego."""
        print(f"[DEBUG] Aktualizacja raportu pogodowego: {weather_report}")
        self.text_label.config(text=weather_report)