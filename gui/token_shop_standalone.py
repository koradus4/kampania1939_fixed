import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from gui.token_shop import TokenShop

# Szybki standalone launcher do testowania sklepu bez uruchamiania całej gry
if __name__ == "__main__":
    class DummyEkonomia:
        def get_points(self):
            return {'economic_points': 999}
        def subtract_points(self, pts):
            pass
    class DummyDowodca:
        def __init__(self, id):
            self.id = id
    root = tk.Tk()
    root.withdraw()  # Ukryj główne okno
    # Przykład: sklep dla generała Polski, dowódcy o id 2 i 3
    dowodcy = [DummyDowodca(2), DummyDowodca(3)]
    TokenShop(root, DummyEkonomia(), dowodcy, nation="Polska")
    root.mainloop()
