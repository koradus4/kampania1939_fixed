import sys
import os
import tkinter as tk

# Dodaj katalog 'gui' do ścieżki wyszukiwania modułów
sys.path.append(os.path.join(os.getcwd(), "gui"))

from panel_generalapolska import OknoGeneralaPolska

class MockEconomySystem:
    def generate_report(self, country):
        return f"Raport ekonomiczny dla: {country}"

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ukryj główne okno

    economy_system = MockEconomySystem()
    general_window = OknoGeneralaPolska(root, economy_system)
    general_window.mainloop()