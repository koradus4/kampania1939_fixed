import tkinter as tk
from gui.panel_dowodcypolska1 import PanelDowodcyPolska1

def next_turn_callback():
    print("Tura zakończona. Przechodzenie do następnej tury...")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ukryj główne okno
    panel = PanelDowodcyPolska1(root, next_turn_callback)
    panel.mainloop()