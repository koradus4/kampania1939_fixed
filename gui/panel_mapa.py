import tkinter as tk
from tkinter import ttk, simpledialog
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
        self.canvas.bind("<Button-3>", self._on_right_click_token)

        # żetony
        self.token_images = {}
        # Przekazanie obiektu gracza do panelu (potrzebne do filtrowania widoczności)
        self.player = getattr(game_engine, 'current_player_obj', None)
        self._draw_tokens_on_map()

        self.current_path = None  # Ścieżka do wizualizacji

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
                    # Dodaj napis z combat_value (i bazowym w nawiasie)
                    base_cv = token.stats.get('combat_value', '?')
                    curr_cv = getattr(token, 'combat_value', base_cv)
                    self.canvas.create_text(x, y+hex_size//2-8, text=f"{curr_cv} ({base_cv})", fill="black", font=("Arial", 10, "bold"), tags="token")
                    # Obwódka zależna od trybu ruchu
                    border_color = "limegreen"  # domyślnie bojowy
                    if hasattr(token, 'movement_mode'):
                        if token.movement_mode == 'combat':
                            border_color = "limegreen"
                        elif token.movement_mode == 'march':
                            border_color = "red"
                        elif token.movement_mode == 'recon':
                            border_color = "yellow"
                    if hasattr(self, 'selected_token_id') and token.id == self.selected_token_id:
                        verts = get_hex_vertices(x, y, hex_size)
                        flat = [coord for p in verts for coord in p]
                        self.canvas.create_polygon(
                            flat,
                            outline=border_color,
                            width=2,
                            fill="",
                            tags="token_sel"
                        )
                except Exception:
                    pass
        # Kod spełnia wymagania: synchronizacja żetonów, tagowanie, poprawna mgiełka i widoczność.

    def _draw_path_on_map(self):
        if self.current_path:
            coords = []
            for q, r in self.current_path:
                x, y = self.map_model.hex_to_pixel(q, r)
                coords.append((x, y))
            if len(coords) > 1:
                for i in range(len(coords)-1):
                    self.canvas.create_line(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1], fill='blue', width=4, tags='path')

    def refresh(self):
        self.canvas.delete('path')
        self._sync_player_from_engine()
        self._draw_hex_grid()
        self._draw_tokens_on_map()
        self._draw_path_on_map()

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
        if clicked_token:
            # Sprawdź, czy kliknięty żeton należy do aktywnego gracza
            if clicked_token:
                # Sprawdź właściciela żetonu (owner może być np. '2 (Polska)')
                expected_owner = f"{getattr(self.player, 'id', '?')} ({getattr(self.player, 'nation', '?')})"
                if getattr(clicked_token, 'owner', None) != expected_owner:
                    # Kliknięto żeton przeciwnika lub sojusznika – nie pokazuj wyboru trybu ruchu
                    self.selected_token_id = None
                    self.current_path = None
                    if self.token_info_panel is not None:
                        self.token_info_panel.clear()
                    self.refresh()
                    return
                # ...reszta logiki wyboru trybu ruchu i blokady...
                if hasattr(clicked_token, 'movement_mode_locked') and clicked_token.movement_mode_locked:
                    self.selected_token_id = clicked_token.id
                    if self.panel_dowodcy is not None:
                        self.panel_dowodcy.wybrany_token = clicked_token
                    if self.token_info_panel is not None:
                        self.token_info_panel.show_token(clicked_token)
                    self.current_path = None
                    self.refresh()
                    return
                # Okno wyboru trybu ruchu przez combobox (tylko jeśli nie zablokowany)
                class ModeDialog(simpledialog.Dialog):
                    def body(self, master):
                        tk.Label(master, text="Wybierz tryb ruchu:").pack()
                        self.combo = ttk.Combobox(master, values=["Bojowy", "Marsz", "Zwiad"], state="readonly")
                        mode_map = {'combat': 0, 'marsz': 1, 'recon': 2}
                        idx = mode_map.get(getattr(clicked_token, 'movement_mode', 'combat'), 0)
                        self.combo.current(idx)
                        self.combo.pack()
                        return self.combo
                    def apply(self):
                        self.result = self.combo.get()
                dialog = ModeDialog(self)
                mode = dialog.result
                if mode == "Bojowy":
                    clicked_token.movement_mode = "combat"
                elif mode == "Marsz":
                    clicked_token.movement_mode = "march"
                elif mode == "Zwiad":
                    clicked_token.movement_mode = "recon"
                clicked_token.apply_movement_mode(reset_mp=False)
                clicked_token.movement_mode_locked = True  # Blokada zmiany trybu do końca tury
                self.selected_token_id = clicked_token.id
                if self.panel_dowodcy is not None:
                    self.panel_dowodcy.wybrany_token = clicked_token
                if self.token_info_panel is not None:
                    self.token_info_panel.show_token(clicked_token)
                self.current_path = None
                self.refresh()
                return
        elif hr and self.selected_token_id:
            token = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if token:
                path = self.game_engine.board.find_path((token.q, token.r), hr, max_cost=token.currentMovePoints)
                if path:
                    self.current_path = path
                    self.refresh()
                    from tkinter import messagebox
                    if messagebox.askyesno("Ruch", f"Czy wykonać ruch do {hr}?\nKoszt: {len(path)-1}"):
                        from engine.action import MoveAction
                        action = MoveAction(token.id, hr[0], hr[1])
                        success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
                        self.tokens = self.game_engine.tokens
                        if success:
                            from engine.engine import update_all_players_visibility
                            if hasattr(self.game_engine, 'players'):
                                update_all_players_visibility(self.game_engine.players, self.game_engine.tokens, self.game_engine.board)
                        if not success:
                            from tkinter import messagebox
                            messagebox.showerror("Błąd ruchu", msg)
                        if success:
                            self.selected_token_id = None
                        self.current_path = None
                        self.refresh()
                    else:
                        pass
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Błąd", "Brak możliwej ścieżki do celu!")
        else:
            self.selected_token_id = None
            self.current_path = None
        if clicked_token is None:
            self.clear_token_info_panel()
        self.refresh()

    def _on_right_click_token(self, event):
        # Obsługa ataku na żeton przeciwnika
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_token = None
        for token in self.tokens:
            if token.q is not None and token.r is not None:
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
        # Sprawdź, czy kliknięto w żeton przeciwnika (nie swój, nie sojusznika)
        if clicked_token and self.selected_token_id:
            attacker = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if not attacker:
                return
            # Sprawdź, czy to przeciwnik
            nation1 = str(attacker.stats.get('nation', ''))
            nation2 = str(clicked_token.stats.get('nation', ''))
            if nation1 == nation2:
                return  # Nie atakuj sojusznika
            from tkinter import messagebox
            answer = messagebox.askyesno("Potwierdź atak", f"Czy chcesz zaatakować żeton {clicked_token.id}?\n({clicked_token.stats.get('unit','')})")
            if not answer:
                return
            # Wywołaj CombatAction
            from engine.action import CombatAction
            action = CombatAction(attacker.id, clicked_token.id)
            success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
            self.tokens = self.game_engine.tokens
            # Efekty wizualne (szkielet): podświetlenie pól, miganie, usuwanie, cofanie
            self._visualize_combat(attacker, clicked_token, msg)
            # Komunikat zwrotny
            if not success:
                messagebox.showerror("Błąd ataku", msg)
            else:
                messagebox.showinfo("Wynik walki", msg)
            # Odśwież mapę i panele
            self.selected_token_id = None
            self.refresh()

    def _visualize_combat(self, attacker, defender, msg):
        print(f"[DEBUG] Przed walką: attacker {attacker.id} combat_value={getattr(attacker, 'combat_value', '?')}, defender {defender.id} combat_value={getattr(defender, 'combat_value', '?')}")
        # 1. Podświetlenie pól atakującego i broniącego (mgiełka)
        ax, ay = self.map_model.hex_to_pixel(attacker.q, attacker.r)
        dx, dy = self.map_model.hex_to_pixel(defender.q, defender.r)
        hex_size = self.map_model.hex_size
        verts_a = get_hex_vertices(ax, ay, hex_size)
        verts_d = get_hex_vertices(dx, dy, hex_size)
        # Poprawione kolory: jasnozielony i jasnoczerwony (bez przezroczystości)
        self.canvas.create_polygon([c for p in verts_a for c in p], fill='#90ee90', outline='', tags='combat_fx')
        self.canvas.create_polygon([c for p in verts_d for c in p], fill='#ff7f7f', outline='', tags='combat_fx')
        self.canvas.after(400, lambda: self.canvas.delete('combat_fx'))

        # 2. Miganie żetonów, usuwanie, cofanie (na podstawie msg)
        def blink_token(token_id, color, times=4, delay=120, on_end=None):
            tag = f"token_{token_id}"
            def blink(i):
                if i % 2 == 0:
                    self.canvas.itemconfig(tag, state='hidden')
                else:
                    self.canvas.itemconfig(tag, state='normal')
                if i < times * 2:
                    self.canvas.after(delay, lambda: blink(i + 1))
                elif on_end:
                    on_end()
            blink(0)

        def animate_remove(token_id):
            self.canvas.after(350, self.refresh)

        def animate_retreat(token, old_q, old_r, new_q, new_r):
            steps = 6
            x0, y0 = self.map_model.hex_to_pixel(old_q, old_r)
            x1, y1 = self.map_model.hex_to_pixel(new_q, new_r)
            dx = (x1 - x0) / steps
            dy = (y1 - y0) / steps
            tag = f"token_{token.id}"
            def move_step(i):
                if i > steps:
                    self.refresh()
                    return
                self.canvas.move(tag, dx, dy)
                self.canvas.after(40, lambda: move_step(i + 1))
            move_step(1)

        # Rozpoznanie efektu na podstawie komunikatu msg
        msg_l = msg.lower()
        # Eliminacja obrońcy
        if 'obrońca został zniszczony' in msg_l or 'obrońca nie mógł się cofnąć' in msg_l:
            blink_token(defender.id, color='red', times=4, delay=100, on_end=lambda: animate_remove(defender.id))
        # Eliminacja atakującego
        elif 'atakujący został zniszczony' in msg_l:
            blink_token(attacker.id, color='red', times=4, delay=100, on_end=lambda: animate_remove(attacker.id))
        # Cofanie obrońcy
        elif 'cofnął się na' in msg_l:
            import re
            m = re.search(r'cofnął się na \(([-\d]+),([\-\d]+)\)', msg)
            if m:
                new_q, new_r = int(m.group(1)), int(m.group(2))
                old_q, old_r = defender.q, defender.r
                animate_retreat(defender, old_q, old_r, new_q, new_r)
                blink_token(defender.id, color='red', times=2, delay=120)
        # Domyślnie: krótkie miganie obu żetonów
        else:
            blink_token(attacker.id, color='orange', times=2, delay=100)
            blink_token(defender.id, color='orange', times=2, delay=100)
        # Po animacjach, po odświeżeniu mapy, wypisz wartości po walce
        def print_after_refresh():
            att = next((t for t in self.tokens if t.id == attacker.id), None)
            defn = next((t for t in self.tokens if t.id == defender.id), None)
            print(f"[DEBUG] Po walce: attacker {attacker.id} combat_value={getattr(att, 'combat_value', '?') if att else 'X'}, defender {defender.id} combat_value={getattr(defn, 'combat_value', '?') if defn else 'X'}")
        self.canvas.after(600, print_after_refresh)

    def refresh(self):
        self.canvas.delete('path')
        self._sync_player_from_engine()
        self._draw_hex_grid()
        self._draw_tokens_on_map()
        self._draw_path_on_map()

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
        if clicked_token:
            # Sprawdź, czy kliknięty żeton należy do aktywnego gracza
            if clicked_token:
                # Sprawdź właściciela żetonu (owner może być np. '2 (Polska)')
                expected_owner = f"{getattr(self.player, 'id', '?')} ({getattr(self.player, 'nation', '?')})"
                if getattr(clicked_token, 'owner', None) != expected_owner:
                    # Kliknięto żeton przeciwnika lub sojusznika – nie pokazuj wyboru trybu ruchu
                    self.selected_token_id = None
                    self.current_path = None
                    if self.token_info_panel is not None:
                        self.token_info_panel.clear()
                    self.refresh()
                    return
                # ...reszta logiki wyboru trybu ruchu i blokady...
                if hasattr(clicked_token, 'movement_mode_locked') and clicked_token.movement_mode_locked:
                    self.selected_token_id = clicked_token.id
                    if self.panel_dowodcy is not None:
                        self.panel_dowodcy.wybrany_token = clicked_token
                    if self.token_info_panel is not None:
                        self.token_info_panel.show_token(clicked_token)
                    self.current_path = None
                    self.refresh()
                    return
                # Okno wyboru trybu ruchu przez combobox (tylko jeśli nie zablokowany)
                class ModeDialog(simpledialog.Dialog):
                    def body(self, master):
                        tk.Label(master, text="Wybierz tryb ruchu:").pack()
                        self.combo = ttk.Combobox(master, values=["Bojowy", "Marsz", "Zwiad"], state="readonly")
                        mode_map = {'combat': 0, 'marsz': 1, 'recon': 2}
                        idx = mode_map.get(getattr(clicked_token, 'movement_mode', 'combat'), 0)
                        self.combo.current(idx)
                        self.combo.pack()
                        return self.combo
                    def apply(self):
                        self.result = self.combo.get()
                dialog = ModeDialog(self)
                mode = dialog.result
                if mode == "Bojowy":
                    clicked_token.movement_mode = "combat"
                elif mode == "Marsz":
                    clicked_token.movement_mode = "march"
                elif mode == "Zwiad":
                    clicked_token.movement_mode = "recon"
                clicked_token.apply_movement_mode(reset_mp=False)
                clicked_token.movement_mode_locked = True  # Blokada zmiany trybu do końca tury
                self.selected_token_id = clicked_token.id
                if self.panel_dowodcy is not None:
                    self.panel_dowodcy.wybrany_token = clicked_token
                if self.token_info_panel is not None:
                    self.token_info_panel.show_token(clicked_token)
                self.current_path = None
                self.refresh()
                return
        elif hr and self.selected_token_id:
            token = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if token:
                path = self.game_engine.board.find_path((token.q, token.r), hr, max_cost=token.currentMovePoints)
                if path:
                    self.current_path = path
                    self.refresh()
                    from tkinter import messagebox
                    if messagebox.askyesno("Ruch", f"Czy wykonać ruch do {hr}?\nKoszt: {len(path)-1}"):
                        from engine.action import MoveAction
                        action = MoveAction(token.id, hr[0], hr[1])
                        success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
                        self.tokens = self.game_engine.tokens
                        if success:
                            from engine.engine import update_all_players_visibility
                            if hasattr(self.game_engine, 'players'):
                                update_all_players_visibility(self.game_engine.players, self.game_engine.tokens, self.game_engine.board)
                        if not success:
                            from tkinter import messagebox
                            messagebox.showerror("Błąd ruchu", msg)
                        if success:
                            self.selected_token_id = None
                        self.current_path = None
                        self.refresh()
                    else:
                        pass
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Błąd", "Brak możliwej ścieżki do celu!")
        else:
            self.selected_token_id = None
            self.current_path = None
        if clicked_token is None:
            self.clear_token_info_panel()
        self.refresh()

    def _on_right_click_token(self, event):
        # Obsługa ataku na żeton przeciwnika
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_token = None
        for token in self.tokens:
            if token.q is not None and token.r is not None:
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
        # Sprawdź, czy kliknięto w żeton przeciwnika (nie swój, nie sojusznika)
        if clicked_token and self.selected_token_id:
            attacker = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if not attacker:
                return
            # Sprawdź, czy to przeciwnik
            nation1 = str(attacker.stats.get('nation', ''))
            nation2 = str(clicked_token.stats.get('nation', ''))
            if nation1 == nation2:
                return  # Nie atakuj sojusznika
            from tkinter import messagebox
            answer = messagebox.askyesno("Potwierdź atak", f"Czy chcesz zaatakować żeton {clicked_token.id}?\n({clicked_token.stats.get('unit','')})")
            if not answer:
                return
            # Wywołaj CombatAction
            from engine.action import CombatAction
            action = CombatAction(attacker.id, clicked_token.id)
            success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
            self.tokens = self.game_engine.tokens
            # Efekty wizualne (szkielet): podświetlenie pól, miganie, usuwanie, cofanie
            self._visualize_combat(attacker, clicked_token, msg)
            # Komunikat zwrotny
            if not success:
                messagebox.showerror("Błąd ataku", msg)
            else:
                messagebox.showinfo("Wynik walki", msg)
            # Odśwież mapę i panele
            self.selected_token_id = None
            self.refresh()

    def _visualize_combat(self, attacker, defender, msg):
        print(f"[DEBUG] Przed walką: attacker {attacker.id} combat_value={getattr(attacker, 'combat_value', '?')}, defender {defender.id} combat_value={getattr(defender, 'combat_value', '?')}")
        # 1. Podświetlenie pól atakującego i broniącego (mgiełka)
        ax, ay = self.map_model.hex_to_pixel(attacker.q, attacker.r)
        dx, dy = self.map_model.hex_to_pixel(defender.q, defender.r)
        hex_size = self.map_model.hex_size
        verts_a = get_hex_vertices(ax, ay, hex_size)
        verts_d = get_hex_vertices(dx, dy, hex_size)
        # Poprawione kolory: jasnozielony i jasnoczerwony (bez przezroczystości)
        self.canvas.create_polygon([c for p in verts_a for c in p], fill='#90ee90', outline='', tags='combat_fx')
        self.canvas.create_polygon([c for p in verts_d for c in p], fill='#ff7f7f', outline='', tags='combat_fx')
        self.canvas.after(400, lambda: self.canvas.delete('combat_fx'))

        # 2. Miganie żetonów, usuwanie, cofanie (na podstawie msg)
        def blink_token(token_id, color, times=4, delay=120, on_end=None):
            tag = f"token_{token_id}"
            def blink(i):
                if i % 2 == 0:
                    self.canvas.itemconfig(tag, state='hidden')
                else:
                    self.canvas.itemconfig(tag, state='normal')
                if i < times * 2:
                    self.canvas.after(delay, lambda: blink(i + 1))
                elif on_end:
                    on_end()
            blink(0)

        def animate_remove(token_id):
            self.canvas.after(350, self.refresh)

        def animate_retreat(token, old_q, old_r, new_q, new_r):
            steps = 6
            x0, y0 = self.map_model.hex_to_pixel(old_q, old_r)
            x1, y1 = self.map_model.hex_to_pixel(new_q, new_r)
            dx = (x1 - x0) / steps
            dy = (y1 - y0) / steps
            tag = f"token_{token.id}"
            def move_step(i):
                if i > steps:
                    self.refresh()
                    return
                self.canvas.move(tag, dx, dy)
                self.canvas.after(40, lambda: move_step(i + 1))
            move_step(1)

        # Rozpoznanie efektu na podstawie komunikatu msg
        msg_l = msg.lower()
        # Eliminacja obrońcy
        if 'obrońca został zniszczony' in msg_l or 'obrońca nie mógł się cofnąć' in msg_l:
            blink_token(defender.id, color='red', times=4, delay=100, on_end=lambda: animate_remove(defender.id))
        # Eliminacja atakującego
        elif 'atakujący został zniszczony' in msg_l:
            blink_token(attacker.id, color='red', times=4, delay=100, on_end=lambda: animate_remove(attacker.id))
        # Cofanie obrońcy
        elif 'cofnął się na' in msg_l:
            import re
            m = re.search(r'cofnął się na \(([-\d]+),([\-\d]+)\)', msg)
            if m:
                new_q, new_r = int(m.group(1)), int(m.group(2))
                old_q, old_r = defender.q, defender.r
                animate_retreat(defender, old_q, old_r, new_q, new_r)
                blink_token(defender.id, color='red', times=2, delay=120)
        # Domyślnie: krótkie miganie obu żetonów
        else:
            blink_token(attacker.id, color='orange', times=2, delay=100)
            blink_token(defender.id, color='orange', times=2, delay=100)
        # Po animacjach, po odświeżeniu mapy, wypisz wartości po walce
        def print_after_refresh():
            att = next((t for t in self.tokens if t.id == attacker.id), None)
            defn = next((t for t in self.tokens if t.id == defender.id), None)
            print(f"[DEBUG] Po walce: attacker {attacker.id} combat_value={getattr(att, 'combat_value', '?') if att else 'X'}, defender {defender.id} combat_value={getattr(defn, 'combat_value', '?') if defn else 'X'}")
        self.canvas.after(600, print_after_refresh)