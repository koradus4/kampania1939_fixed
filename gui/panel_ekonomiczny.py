import tkinter as tk

class PanelEkonomiczny(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray", relief=tk.SUNKEN, borderwidth=2)  # Dodano obramowanie

        # Nagłówek panelu
        self.header = tk.Label(self, text="Raport Ekonomiczny", font=("Arial", 12), bg="lightgray")
        self.header.pack(pady=2)

        # Obszar tekstowy bez przewijania
        self.text_label = tk.Label(self, text="", wraplength=250, justify=tk.LEFT, bg="white", anchor="nw")
        self.text_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_economy(self, economy_report):
        """Aktualizuje zawartość raportu ekonomicznego."""
        self.text_label.config(text=economy_report)