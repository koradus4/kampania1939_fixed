import sys
import unittest
import tkinter as tk
import os
from gui.panel_dowodcy import PanelDowodcy
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DummyGracz:
    def __init__(self, id, nation):
        self.id = id
        self.nation = nation
        self.name = f"Dowódca {id}"
        self.image_path = "assets/mapa_globalna.jpg"
        self.punkty_ekonomiczne = 100
        self.economy = None

class DummyGameEngine:
    def __init__(self):
        self.current_player_obj = None
        self.tokens = []
        self.board = None

class TestDeployButtonBlink(unittest.TestCase):
    def setUp(self):
        # Przygotuj sztucznego gracza i folder z nowymi żetonami
        self.gracz = DummyGracz(99, "Polska")
        self.engine = DummyGameEngine()
        self.root = tk.Tk()
        self.root.withdraw()  # Ukryj główne okno
        # Utwórz pusty folder na nowe żetony
        self.folder = Path(f"assets/tokens/nowe_dla_{self.gracz.id}/")
        self.folder.mkdir(parents=True, exist_ok=True)
        # Dodaj jeden "żeton" (symulacja)
        (self.folder / "zeton1").mkdir(exist_ok=True)
        with open(self.folder / "zeton1" / "token.json", "w") as f:
            f.write("{}")
        with open(self.folder / "zeton1" / "token.png", "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # fake PNG header

    def tearDown(self):
        # Usuń testowy folder i okna
        import shutil
        shutil.rmtree(self.folder.parent / f"nowe_dla_{self.gracz.id}", ignore_errors=True)
        self.root.destroy()

    def test_deploy_button_stops_blinking_after_deploy(self):
        # Utwórz panel dowódcy
        panel = PanelDowodcy(turn_number=1, remaining_time=60, gracz=self.gracz, game_engine=self.engine)
        # Otwórz okno wystawiania nowych jednostek
        panel.open_deploy_window()
        panel.root.update()
        # Symuluj usunięcie wszystkich żetonów (tak jakby zostały wystawione)
        import shutil
        shutil.rmtree(self.folder, ignore_errors=True)
        # Zamknij okno rezerwy
        if hasattr(panel, 'deploy_window'):
            panel.deploy_window.destroy()
        panel.root.update()
        # Sprawdź, czy miganie zostało zatrzymane
        # (przycisk nie powinien już migać, czyli nie ma aktywnego _deploy_blink_id)
        blink_id = getattr(panel, '_deploy_blink_id', None)
        self.assertTrue(blink_id is None or blink_id == 0, "Przycisk nadal miga mimo braku żetonów do wystawienia!")

if __name__ == "__main__":
    unittest.main()
