import tkinter as tk
from tkinter import ttk
from gui.panel_generalapolska import OknoGeneralaPolska  # Poprawiona nazwa klasy

class EkranStartowy(tk.Tk):
    """
    Ekran startowy gry, umożliwiający wybór nacji.
    """
    def __init__(self):
        super().__init__()
        self.title("Kampania 1939 - Ekran Startowy")
        self.geometry("400x300")
        self.configure(bg="darkolivegreen")

        # Nagłówek
        label = tk.Label(self, text="Wybierz nację", font=("Arial", 16), bg="darkolivegreen", fg="white")
        label.pack(pady=20)

        # Przycisk dla Polski
        polska_button = ttk.Button(self, text="Polska", command=lambda: self.open_panel_generala("Polska"))
        polska_button.pack(pady=10)

        # Przycisk dla Niemiec
        niemcy_button = ttk.Button(self, text="Niemcy", command=lambda: self.open_panel_generala("Niemcy"))
        niemcy_button.pack(pady=10)

    def open_panel_generala(self, nation):
        """
        Otwiera panel generała dla wybranej nacji.
        """
        self.withdraw()  # Ukryj ekran startowy
        economy_system = MockEconomySystem()  # Przykładowy system ekonomiczny
        panel_generala = OknoGeneralaPolska(self, nation=nation, economy_system=economy_system)
        panel_generala.mainloop()

        # Po zamknięciu panelu generała przywróć ekran startowy
        self.deiconify()


class MockEconomySystem:
    """
    Przykładowy system ekonomiczny do generowania raportów.
    """
    def generate_report(self, nation):
        return f"Raport ekonomiczny dla: {nation}"