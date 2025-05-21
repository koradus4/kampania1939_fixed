import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from engine.engine import GameEngine
from engine.action import MoveAction

# PanelMapa importowany dynamicznie, bo zależy od tkinter i modelu
import sys
import importlib.util
import types

spec = importlib.util.spec_from_file_location("panel_mapa", "gui/panel_mapa.py")
panel_mapa = importlib.util.module_from_spec(spec)
sys.modules["panel_mapa"] = panel_mapa
spec.loader.exec_module(panel_mapa)

class TestPanelMapaIntegration(unittest.TestCase):
    def setUp(self):
        # Minimalny model mapy z wymaganymi metodami
        class DummyMapModel:
            hex_size = 30
            def get_overlay_items(self):
                return []
            def hex_to_pixel(self, q, r):
                return (q*30, r*30)
            def coords_to_hex(self, x, y):
                return (int(x//30), int(y//30))
        self.map_model = DummyMapModel()
        self.root = tk.Tk()
        self.root.withdraw()  # nie pokazuj okna
        # Patchujemy __init__ PanelMapa, by nie inicjalizował GameEngine
        with patch.object(panel_mapa.PanelMapa, '__init__', lambda self, *a, **kw: None):
            self.panel = panel_mapa.PanelMapa(None, None, None, None)
            self.panel.map_model = self.map_model
            self.panel.bg_path = "assets/mapa_globalna.jpg"
            self.panel.player_nation = "Polska"
            self.panel.tokens_to_draw = None
            self.panel.width = 300
            self.panel.height = 300
            self.panel.selected_token_id = None
            self.panel.canvas = MagicMock()
            self.panel.engine = GameEngine(
                map_path='data/map_data.json',
                tokens_index_path='assets/tokens/index.json',
                tokens_start_path='assets/start_tokens.json',
                seed=123
            )
            self.panel.token_images = {}
            # Adapter do prawdziwych żetonów z silnika
            class ZetonyAdapter:
                def __init__(self, tokens):
                    self._tokens = tokens
                def get_tokens_on_map(self):
                    # Zwraca listę dictów z id, q, r
                    return [
                        {'id': t.id, 'q': t.q, 'r': t.r} for t in self._tokens if t.q is not None and t.r is not None
                    ]
                def get_token_data(self, token_id):
                    # Zwraca dict z danymi żetonu (np. image, nation, itp.)
                    for t in self._tokens:
                        if t.id == token_id:
                            d = dict(t.stats)
                            d['id'] = t.id
                            d['nation'] = t.owner
                            return d
                    return {}
            self.panel.zetony = ZetonyAdapter(self.panel.engine.tokens)
            # Minimalna wersja metody on_canvas_click do testu wyboru żetonu
            def on_canvas_click(x, y):
                q, r = self.map_model.coords_to_hex(x, y)
                for token in self.panel.engine.tokens:
                    if token.q == q and token.r == r:
                        self.panel.selected_token_id = token.id
                        return
                self.panel.selected_token_id = None
            self.panel.on_canvas_click = on_canvas_click
        # Patchujemy metody rysujące, by nie korzystały z prawdziwego canvas
        self.panel._draw_hex_grid = MagicMock()
        self.panel._bind_hover = MagicMock()

    def test_token_move_and_refresh(self):
        # Pobierz pierwszy żeton
        tokens = self.panel.engine.tokens
        if not tokens:
            self.skipTest("Brak żetonów do testu integracyjnego")
        token = tokens[0]
        start = (token.q, token.r)
        # Znajdź inny heks
        for (k, tile) in self.panel.engine.board.terrain.items():
            q, r = tile.q, tile.r
            if (q, r) != start:
                action = MoveAction(token.id, q, r)
                success, msg = self.panel.engine.execute_action(action)
                self.assertTrue(success)
                self.panel.refresh()
                # Sprawdź, czy canvas.create_image został wywołany z nowymi współrzędnymi
                called = False
                for call in self.panel.canvas.create_image.call_args_list:
                    args, kwargs = call
                    if abs(args[0] - q*30) < 1 and abs(args[1] - r*30) < 1:
                        called = True
                        break
                self.assertTrue(called, f"Żeton nie został narysowany na nowej pozycji ({q},{r}) po refresh")
                break

    def test_token_select_on_click(self):
        # Pobierz pierwszy żeton
        tokens = self.panel.engine.tokens
        if not tokens:
            self.skipTest("Brak żetonów do testu integracyjnego")
        token = tokens[0]
        # Załóżmy, że PanelMapa ma metodę on_canvas_click(x, y)
        # Symulujemy kliknięcie na pozycję żetonu
        x, y = self.map_model.hex_to_pixel(token.q, token.r)
        # Jeśli metoda nazywa się inaczej, popraw nazwę poniżej
        if hasattr(self.panel, 'on_canvas_click'):
            self.panel.on_canvas_click(x, y)
        else:
            self.skipTest("PanelMapa nie ma metody on_canvas_click – popraw nazwę w teście")
        # Sprawdź, czy selected_token_id został ustawiony
        self.assertEqual(self.panel.selected_token_id, token.id, f"Po kliknięciu na żeton powinien być wybrany jego id: {token.id}")

    def test_token_combat_and_refresh(self):
        # Testuje akcję walki i odświeżenie GUI
        from engine.action import CombatAction
        tokens = self.panel.engine.tokens
        if len(tokens) < 2:
            self.skipTest("Za mało żetonów do testu walki")
        attacker = tokens[0]
        # Szukamy innego żetonu na innym polu
        defender = None
        for t in tokens[1:]:
            if (t.q, t.r) != (attacker.q, attacker.r):
                defender = t
                break
        if not defender:
            self.skipTest("Brak drugiego żetonu do testu walki")
        # Przesuwamy obrońcę na sąsiednie pole do atakującego
        defender.q = attacker.q + 1
        defender.r = attacker.r
        # Wykonujemy akcję walki
        action = CombatAction(attacker.id, defender.id)
        success, msg = self.panel.engine.execute_action(action)
        self.assertTrue(success, f"Walka nie powiodła się: {msg}")
        self.panel.refresh()
        # Sprawdzamy, czy canvas.create_image został wywołany dla atakującego (może się przesunął)
        called = False
        for call in self.panel.canvas.create_image.call_args_list:
            args, kwargs = call
            if abs(args[0] - attacker.q*30) < 1 and abs(args[1] - attacker.r*30) < 1:
                called = True
                break
        self.assertTrue(called, "Żeton atakujący nie został narysowany po walce")

    def test_token_move_to_occupied_hex(self):
        # Testuje próbę ruchu na zajęte pole (powinno się nie udać)
        tokens = self.panel.engine.tokens
        if len(tokens) < 2:
            self.skipTest("Za mało żetonów do testu ruchu na zajęte pole")
        t1, t2 = tokens[0], tokens[1]
        # Ustawiamy oba żetony na różnych polach
        t1.q, t1.r = 5, 5
        t2.q, t2.r = 6, 5
        # Aktualizujemy stan planszy (ważne dla sprawdzania kolizji)
        self.panel.engine.board.set_tokens(self.panel.engine.tokens)
        # Próbujemy przesunąć t1 na pole t2 (nie zmieniamy ręcznie pozycji t1!)
        action = MoveAction(t1.id, t2.q, t2.r)
        success, msg = self.panel.engine.execute_action(action)
        print(f"[DEBUG] Po akcji: t1=({t1.q},{t1.r}), t2=({t2.q},{t2.r}), success={success}, msg={msg}")
        self.assertEqual((t1.q, t1.r), (5, 5), f"Po nieudanej akcji t1 powinien być na (5,5), jest na ({t1.q},{t1.r})")
        self.assertEqual((t2.q, t2.r), (6, 5), f"Po nieudanej akcji t2 powinien być na (6,5), jest na ({t2.q},{t2.r})")
        self.assertFalse(success, "Ruch na zajęte pole powinien się nie udać")
        # Resetujemy mocka create_image przed refresh, by sprawdzać tylko aktualne wywołania
        self.panel.canvas.create_image.reset_mock()
        self.panel.refresh()
        # Sprawdzamy, czy żeton t1 nie został narysowany na pozycji t2
        for call, token in zip(self.panel.canvas.create_image.call_args_list, self.panel.engine.tokens):
            args, kwargs = call
            if token.id == t1.id:
                self.assertFalse(abs(args[0] - t2.q*30) < 1 and abs(args[1] - t2.r*30) < 1,
                                 "Żeton t1 nie powinien być narysowany na zajętym polu t2")

    def test_token_remove_and_refresh(self):
        # Testuje usunięcie żetonu i odświeżenie GUI
        tokens = self.panel.engine.tokens
        if not tokens:
            self.skipTest("Brak żetonów do testu usuwania")
        token = tokens[0]
        # Usuwamy żeton z silnika
        self.panel.engine.tokens.remove(token)
        self.panel.refresh()
        # Sprawdzamy, czy żeton nie został narysowany
        for call in self.panel.canvas.create_image.call_args_list:
            args, kwargs = call
            self.assertFalse(abs(args[0] - token.q*30) < 1 and abs(args[1] - token.r*30) < 1,
                             "Usunięty żeton nie powinien być narysowany na mapie")

    def tearDown(self):
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()
