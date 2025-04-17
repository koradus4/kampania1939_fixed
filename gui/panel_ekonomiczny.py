import tkinter as tk

class PanelEkonomiczny(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray")

        # Nagłówek panelu
        self.header = tk.Label(self, text="Raport Ekonomiczny", font=("Arial", 12), bg="lightgray")
        self.header.pack(pady=2)

        # Obszar tekstowy z przewijaniem
        self.text_area = tk.Text(self, wrap=tk.WORD, height=5, width=30, bg="white", state=tk.DISABLED)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        # Suwak pionowy
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

    def update_economy(self, economy_report):
        """Aktualizuje zawartość raportu ekonomicznego."""
        print(f"[DEBUG] Aktualizacja raportu ekonomicznego: {economy_report}")
        if not hasattr(self, 'text_area') or not self.text_area.winfo_exists():
            print("Błąd: Panel ekonomiczny nie istnieje lub został zniszczony.")
            return

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, economy_report)
        self.text_area.config(state=tk.DISABLED)