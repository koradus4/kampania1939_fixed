# main.py – punkt wejścia do gry
import sys
import os

# Dodanie ścieżki projektu do sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.ekran_startowy import EkranStartowy

if __name__ == '__main__':
    app = EkranStartowy()
    app.mainloop()
