import tkinter as tk

class PanelPogodowy(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray")

        # Nagłówek panelu
        self.header = tk.Label(self, text="Raport Pogodowy", font=("Arial", 12), bg="lightgray")
        self.header.pack(pady=2)

        # Obszar tekstowy z przewijaniem (zmniejszona wysokość)
        self.text_area = tk.Text(self, wrap=tk.WORD, height=5, width=30, bg="white", state=tk.DISABLED)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        # Suwak pionowy
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

    def update_weather(self, weather_report):
        """Aktualizuje zawartość raportu pogodowego."""
        print(f"[DEBUG] Aktualizacja raportu pogodowego: {weather_report}")
        if not hasattr(self, 'text_area') or not self.text_area.winfo_exists():
            print("Błąd: Panel pogodowy nie istnieje lub został zniszczony.")
            return

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, weather_report)
        self.text_area.config(state=tk.DISABLED)