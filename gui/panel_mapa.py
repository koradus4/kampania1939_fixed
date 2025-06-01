import tkinter as tk
from engine.hex_utils import get_hex_vertices
from PIL import Image, ImageTk
import os

class PanelMapa(tk.Frame):
    def __init__(self, parent, game_engine, bg_path: str, player_nation: str, width=800, height=600, token_info_panel=None, panel_dowodcy=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.map_model = self.game_engine.board
        self.player_nation = player_nation
        self.tokens = self.game_engine.tokens
        self.token_info_panel = token_info_panel
        self.panel_dowodcy = panel_dowodcy  # <--- dodane

        # Canvas + Scrollbary
        self.canvas = tk.Canvas(self, width=width, height=height)
        hbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        vbar = tk.Scrollbar(self, orient="vertical",   command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        hbar.grid(row=1, column=0, sticky="ew")
        vbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # tło mapy - jeśli nie podano lub plik nie istnieje, nie ustawiaj tła
        if bg_path and os.path.exists(bg_path):
            bg = Image.open(bg_path)
            self._bg = ImageTk.PhotoImage(bg)
            self.canvas.create_image(0, 0, anchor="nw", image=self._bg)
            self.canvas.config(scrollregion=(0, 0, bg.width, bg.height))
            self._bg_width = bg.width
            self._bg_height = bg.height
        else:
            self._bg = None
            self._bg_width = width
            self._bg_height = height
            self.canvas.config(scrollregion=(0, 0, width, height))

        # rysuj siatkę i etykiety
        self._draw_hex_grid()

        # kliknięcia
        self.canvas.bind("<Button-1>", self._on_click)
        # self.canvas.bind("<Button-3>", self._on_right_click)  # Usunięto obsługę prawego przycisku

        # żetony
        self.token_images = {}
        # Przekazanie obiektu gracza do panelu (potrzebne do filtrowania widoczności)
        self.player = getattr(game_engine, 'current_player_obj', None)
        self._draw_tokens_on_map()

    def _sync_player_from_engine(self):
        """Synchronizuje self.player z aktualnym obiektem gracza z silnika gry."""
        if hasattr(self.game_engine, 'current_player_obj'):
            self.player = self.game_engine.current_player_obj

    def _draw_hex_grid(self):
        self._sync_player_from_engine()
        self.canvas.delete("hex")
        self.canvas.delete("fog")
        s = self.map_model.hex_size
        visible_hexes = set()
        if hasattr(self, 'player') and hasattr(self.player, 'visible_hexes'):
            visible_hexes = set((int(q), int(r)) for q, r in self.player.visible_hexes)
        # Dodaj tymczasową widoczność (odkryte w tej turze)
        if hasattr(self.player, 'temp_visible_hexes'):
            visible_hexes |= set((int(q), int(r)) for q, r in self.player.temp_visible_hexes)
        # DEBUG: wypisz heksy widoczne i zamglenione
        # print(f"[DEBUG] visible_hexes: {sorted(visible_hexes)}")
        fogged = []
        for key, tile in self.map_model.terrain.items():
            if isinstance(key, tuple) and len(key) == 2:
                q, r = key
            else:
                q, r = map(int, str(key).split(','))
            cx, cy = self.map_model.hex_to_pixel(q, r)
            if 0 <= cx <= self._bg_width and 0 <= cy <= self._bg_height:
                if (int(q), int(r)) not in visible_hexes:
                    fogged.append((int(q), int(r)))
        # print(f"[DEBUG] fogged_hexes: {sorted(fogged)}")
        for key, tile in self.map_model.terrain.items():
            # Obsługa kluczy tuple (q, r) lub string "q,r"
            if isinstance(key, tuple) and len(key) == 2:
                q, r = int(key[0]), int(key[1])
            else:
                q, r = map(int, str(key).split(','))
            cx, cy = self.map_model.hex_to_pixel(q, r)
            if 0 <= cx <= self._bg_width and 0 <= cy <= self._bg_height:
                verts = get_hex_vertices(cx, cy, s)
                flat = [coord for p in verts for coord in p]
                self.canvas.create_polygon(
                    flat,
                    outline="red",
                    fill="",
                    width=1,
                    tags="hex"
                )
                # Rysuj mgiełkę tylko jeśli (q, r) nie jest w visible_hexes (upewnij się, że tuple intów)
                if (q, r) not in visible_hexes:
                    self.canvas.create_polygon(
                        flat,
                        fill="#222222",
                        stipple="gray50",
                        outline="",
                        tags="fog"
                    )

    def _draw_tokens_on_map(self):
        self._sync_player_from_engine()
        self.tokens = self.game_engine.tokens  # Zawsze aktualizuj listę żetonów
        self.canvas.delete("token")
        self.canvas.delete("token_sel")  # Usuwamy stare obwódki
        # Filtrowanie widoczności żetonów przez fog of war (uwzględnij temp_visible_tokens)
        tokens = self.tokens
        if hasattr(self, 'player') and hasattr(self.player, 'visible_tokens') and hasattr(self.player, 'temp_visible_tokens'):
            tokens = [t for t in self.tokens if t.id in (self.player.visible_tokens | self.player.temp_visible_tokens)]
        elif hasattr(self, 'player') and hasattr(self.player, 'visible_tokens'):
            tokens = [t for t in self.tokens if t.id in self.player.visible_tokens]
        for token in tokens:
            if token.q is not None and token.r is not None:
                img_path = token.stats.get("image")
                if not img_path:
                    nation = token.stats.get('nation', '')
                    img_path = f"assets/tokens/{nation}/{token.id}/token.png"
                if not os.path.exists(img_path):
                    img_path = "assets/tokens/default/token.png" if os.path.exists("assets/tokens/default/token.png") else None
                    if not img_path:
                        continue
                try:
                    img = Image.open(img_path)
                    hex_size = self.map_model.hex_size
                    img = img.resize((hex_size, hex_size), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    x, y = self.map_model.hex_to_pixel(token.q, token.r)
                    self.canvas.create_image(x, y, image=tk_img, anchor="center", tags=("token", f"token_{token.id}"))
                    self.token_images[token.id] = tk_img
                    # Jeśli to wybrany żeton, dorysuj zieloną obwódkę
                    if hasattr(self, 'selected_token_id') and token.id == self.selected_token_id:
                        verts = get_hex_vertices(x, y, hex_size)
                        flat = [coord for p in verts for coord in p]
                        self.canvas.create_polygon(
                            flat,
                            outline="limegreen",
                            width=1,
                            fill="",
                            tags="token_sel"
                        )
                except Exception:
                    pass
        # Kod spełnia wymagania: synchronizacja żetonów, tagowanie, poprawna mgiełka i widoczność.

    def refresh(self):
        self._sync_player_from_engine()
        self._draw_hex_grid()
        self._draw_tokens_on_map()

    def clear_token_info_panel(self):
        parent = self.master
        while parent is not None:
            if hasattr(parent, 'token_info_panel'):
                parent.token_info_panel.clear()
                break
            parent = getattr(parent, 'master', None)

    def _on_click(self, event):
        # Blokada akcji dla generała (podgląd, brak ruchu)
        if hasattr(self, 'player') and hasattr(self.player, 'role') and self.player.role == 'Generał':
            from tkinter import messagebox
            messagebox.showinfo("Podgląd", "Generał nie może wykonywać akcji na żetonach.")
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        hr = self.map_model.coords_to_hex(x, y)
        if not hasattr(self, 'selected_token_id'):
            self.selected_token_id = None
        # Sprawdź, czy kliknięto na żeton
        clicked_token = None
        for token in self.tokens:
            if token.q is not None and token.r is not None:
                # Pozwól kliknąć tylko jeśli żeton jest widoczny dla gracza (uwzględnij temp_visible_tokens)
                visible_ids = set()
                if hasattr(self.player, 'visible_tokens') and hasattr(self.player, 'temp_visible_tokens'):
                    visible_ids = self.player.visible_tokens | self.player.temp_visible_tokens
                elif hasattr(self.player, 'visible_tokens'):
                    visible_ids = self.player.visible_tokens
                if token.id not in visible_ids:
                    continue
                tx, ty = self.map_model.hex_to_pixel(token.q, token.r)
                hex_size = self.map_model.hex_size
                if abs(x - tx) < hex_size // 2 and abs(y - ty) < hex_size // 2:
                    clicked_token = token
                    break
        # Sprawdzenie właściciela żetonu dla dowódcy
        if clicked_token:
            if self.panel_dowodcy is not None:
                self.panel_dowodcy.wybrany_token = clicked_token
                # Ustaw także selected_token_id, by umożliwić ruch
                self.selected_token_id = clicked_token.id
            # --- USTAWIAMY WYBRANY ŻETON DLA PANELU DOWÓDCY ---
            if self.token_info_panel is not None:
                self.token_info_panel.show_token(clicked_token)
        elif hr and self.selected_token_id:
            from engine.action import MoveAction
            token = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if token:
                action = MoveAction(token.id, hr[0], hr[1])
                success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
                # Synchronizacja żetonów po ruchu
                self.tokens = self.game_engine.tokens
                if success:
                    # --- AKTUALIZACJA WIDOCZNOŚCI PO RUCHU ---
                    from engine.engine import update_all_players_visibility
                    if hasattr(self.game_engine, 'players'):
                        update_all_players_visibility(self.game_engine.players, self.game_engine.tokens, self.game_engine.board)
                if not success:
                    from tkinter import messagebox
                    messagebox.showerror("Błąd ruchu", msg)
                if success:
                    self.selected_token_id = None
                self.refresh()
        else:
            self.selected_token_id = None
        # Po kliknięciu w puste miejsce wyczyść panel info
        if clicked_token is None:
            self.clear_token_info_panel()
        self.refresh()