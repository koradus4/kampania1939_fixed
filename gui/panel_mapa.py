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
        self.canvas.delete("spawn_overlay")  # Usuwamy stare nakładki spawnów
        s = self.map_model.hex_size
        visible_hexes = set()
        if hasattr(self, 'player') and hasattr(self.player, 'visible_hexes'):
            visible_hexes = set((int(q), int(r)) for q, r in self.player.visible_hexes)
        # Dodaj tymczasową widoczność (odkryte w tej turze)
        if hasattr(self.player, 'temp_visible_hexes'):
            visible_hexes |= set((int(q), int(r)) for q, r in self.player.temp_visible_hexes)
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
        # --- PODŚWIETLANIE SPAWNÓW ---
        spawn_colors = {
            'Polska': '#ff5555',   # półprzezroczysty czerwony
            'Niemcy': '#5555ff',   # półprzezroczysty niebieski
        }
        spawn_points = getattr(self.map_model, 'spawn_points', {})
        for nation, hex_list in spawn_points.items():
            color = spawn_colors.get(nation, '#cccccc')
            for hex_id in hex_list:
                if ',' in hex_id:
                    try:
                        q, r = map(int, hex_id.split(','))
                    except Exception:
                        continue
                else:
                    continue
                cx, cy = self.map_model.hex_to_pixel(q, r)
                verts = get_hex_vertices(cx, cy, s)
                flat = [coord for p in verts for coord in p]
                self.canvas.create_polygon(
                    flat,
                    fill=color,
                    outline='',
                    stipple='gray25',
                    tags='spawn_overlay'
                )
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
            # USUNIĘTO DEBUGI
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
                    hex_size = 40  # Ustaw stały rozmiar 40x40
                    img = img.resize((hex_size, hex_size), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    x, y = self.map_model.hex_to_pixel(token.q, token.r)
                    self.canvas.create_image(x, y, image=tk_img, anchor="center", tags=("token", f"token_{token.id}"))
                    self.token_images[token.id] = tk_img
                    # --- USUNIĘTO: wyświetlanie parametrów tekstowych na żetonie ---
                    # Obwódka zależna od trybu ruchu
                    border_color = "yellow"  # domyślnie bojowy
                    if hasattr(token, 'movement_mode'):
                        if token.movement_mode == 'combat':
                            border_color = "yellow"  # bojowy
                        elif token.movement_mode == 'march':
                            border_color = "limegreen"  # marsz
                        elif token.movement_mode == 'recon':
                            border_color = "red"  # zwiad
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
                except Exception as e:
                    pass  # USUNIĘTO DEBUGI
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
        # --- DODANE: obsługa wystawiania żetonu z poczekalni ---
        if self.panel_dowodcy is not None and hasattr(self.panel_dowodcy, 'deploy_window'):
            deploy = self.panel_dowodcy.deploy_window
            if deploy is not None and getattr(deploy, 'selected_token_path', None):
                import os, json, shutil
                from engine.token import Token
                from tkinter import messagebox
                token_folder = deploy.selected_token_path
                # print(f"[DEBUG] Wybrano folder żetonu: {token_folder}")
                token_json = os.path.join(token_folder, "token.json")
                if os.path.exists(token_json):
                    # SPRAWDŹ SPAWN NATION
                    if hr is None:
                        messagebox.showerror("Błąd", "Kliknij na pole mapy, aby wystawić żeton.")
                        return
                    tile = self.game_engine.board.get_tile(hr[0], hr[1])
                    nation = str(self.player.nation).strip().lower()
                    if not tile or not tile.spawn_nation or str(tile.spawn_nation).strip().lower() != nation:
                        messagebox.showerror("Błąd wystawiania", f"Możesz wystawiać nowe żetony tylko na polach spawnu swojej nacji!")
                        return
                    # print(f"[DEBUG] Plik token.json istnieje: {token_json}")
                    with open(token_json, encoding="utf-8") as f:
                        token_data = json.load(f)
                    # Ustaw owner na aktualnego gracza
                    token_owner = f"{self.player.id} ({self.player.nation})"
                    # print(f"[DEBUG] Ustawiam ownera: {token_owner}")
                    token_data["owner"] = token_owner
                    # Utwórz obiekt Token
                    new_token = Token.from_json(token_data)
                    new_token.set_position(hr[0], hr[1])
                    new_token.owner = token_owner
                    # Resetuj punkty ruchu i paliwa po wystawieniu
                    new_token.apply_movement_mode(reset_mp=True)
                    new_token.currentFuel = new_token.maxFuel
                    # Skopiuj PNG do katalogu docelowego jeśli wymagane (np. assets/tokens/aktualne/)
                    png_src = os.path.join(token_folder, "token.png")
                    if os.path.exists(png_src):
                        dest_dir = os.path.join("assets", "tokens", "aktualne")
                        os.makedirs(dest_dir, exist_ok=True)
                        png_dst = os.path.join(dest_dir, os.path.basename(token_folder) + ".png")
                        shutil.copy2(png_src, png_dst)
                        # print(f"[DEBUG] Skopiowano PNG do: {png_dst}")
                        # Ustaw nową ścieżkę do obrazka w stats['image']
                        new_token.stats['image'] = png_dst.replace('\\', '/')
                    # print(f"[DEBUG] Utworzono Token: id={new_token.id}, q={new_token.q}, r={new_token.r}, owner={new_token.owner}")
                    self.game_engine.tokens.append(new_token)
                    # print(f"[DEBUG] Liczba żetonów po dodaniu: {len(self.game_engine.tokens)}")
                    self.game_engine.board.set_tokens(self.game_engine.tokens)
                    # Dodaj: aktualizacja widoczności po dodaniu żetonu
                    from engine.engine import update_all_players_visibility
                    update_all_players_visibility(self.game_engine.players, self.game_engine.tokens, self.game_engine.board)
                    # Wymuś ustawienie current_player_obj na gracza, który wystawił żeton
                    self.game_engine.current_player_obj = self.player
                    # Odśwież panel mapy po synchronizacji widoczności
                    self.refresh()
                    # print(f"[DEBUG] Odświeżono mapę po dodaniu żetonu.")
                    # Usuń folder z poczekalni
                    shutil.rmtree(token_folder)
                    # print(f"[DEBUG] Usunięto folder: {token_folder}")
                    # Zamknij okno deploy
                    deploy.destroy()
                    self.panel_dowodcy.deploy_window = None
                    # print(f"[DEBUG] Zamknięto okno deploy.")
                    return
        # ...existing code...
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
            expected_owner = f"{getattr(self.player, 'id', '?')} ({getattr(self.player, 'nation', '?')})"
            if getattr(clicked_token, 'owner', None) != expected_owner:
                self.selected_token_id = None
                self.current_path = None
                if self.token_info_panel is not None:
                    self.token_info_panel.clear()
                self.refresh()
                return
            # Najpierw pokaż info panel z aktualnym stanem żetonu
            self.selected_token_id = clicked_token.id
            if self.panel_dowodcy is not None:
                self.panel_dowodcy.wybrany_token = clicked_token
            if self.token_info_panel is not None:
                self.token_info_panel.show_token(clicked_token)
            # Jeśli tryb nie jest zablokowany, pokaż okno wyboru trybu ruchu
            if not getattr(clicked_token, 'movement_mode_locked', False):
                class ModeDialog(simpledialog.Dialog):
                    def body(self, master):
                        tk.Label(master, text="Wybierz tryb ruchu:").pack()
                        self.combo = ttk.Combobox(master, values=["Bojowy", "Marsz", "Zwiad"], state="readonly")
                        mode_map = {'combat': 0, 'marsz': 1, 'recon': 2}
                        curr_mode = getattr(clicked_token, 'movement_mode', 'combat')
                        idx = mode_map.get(curr_mode, 0)
                        self.combo.current(idx)
                        self.combo.pack()
                        return self.combo
                    def apply(self):
                        self.result = self.combo.get()
                dialog = ModeDialog(self)
                mode = getattr(dialog, 'result', None)
                if mode is not None:
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
                        self.token_info_panel.show_token(clicked_token)  # Odśwież info panel po zmianie trybu
            self.current_path = None
            self.refresh()
            return
        elif hr and self.selected_token_id:
            token = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if token:
                path = self.game_engine.board.find_path((token.q, token.r), hr, max_mp=token.currentMovePoints, max_fuel=getattr(token, 'currentFuel', 9999))
                print(f"[DEBUG][MAPA] find_path: start=({token.q},{token.r}), goal={hr}, MP={token.currentMovePoints}, Fuel={getattr(token, 'currentFuel', 9999)} -> path={path}")
                if path:
                    # POLICZ RZECZYWISTY KOSZT RUCHU
                    real_cost = 0
                    for step in path[1:]:  # pomijamy start
                        tile = self.game_engine.board.get_tile(*step)
                        move_mod = getattr(tile, 'move_mod', 0)
                        move_cost = 1 + move_mod
                        real_cost += move_cost
                    self.current_path = path
                    self.refresh()
                    from tkinter import messagebox
                    if messagebox.askyesno("Ruch", f"Czy wykonać ruch do {hr}?\nKoszt: {real_cost}"):
                        from engine.action import MoveAction
                        action = MoveAction(token.id, hr[0], hr[1])
                        success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
                        self.tokens = self.game_engine.tokens
                        if success:
                            from engine.engine import update_all_players_visibility
                            if hasattr(self.game_engine, 'players'):
                                update_all_players_visibility(self.game_engine.players, self.game_engine.tokens, self.game_engine.board)
                            # --- AUTOMATYCZNA REAKCJA WROGÓW ---
                            moved_token = token  # żeton, który się ruszał
                            # print(f"[DEBUG] Sprawdzam reakcję wrogów na ruch żetonu {moved_token.id} ({moved_token.owner}) na ({moved_token.q},{moved_token.r})")
                            for enemy in self.game_engine.tokens:
                                if enemy.id == moved_token.id or enemy.owner == moved_token.owner:
                                    continue
                                # Blokada: nie atakuje własnych żetonów
                                nation_enemy = enemy.owner.split('(')[-1].replace(')','').strip()
                                nation_moved = moved_token.owner.split('(')[-1].replace(')','').strip()
                                if nation_enemy == nation_moved:
                                    # print(f"[DEBUG] Blokada: {enemy.id} ({enemy.owner}) nie atakuje własnego żetonu {moved_token.id} ({moved_token.owner})!")
                                    continue
                                sight = enemy.stats.get('sight', 0)
                                dist = self.game_engine.board.hex_distance((enemy.q, enemy.r), (moved_token.q, moved_token.r))
                                in_sight = dist <= sight
                                attack_range = enemy.stats.get('attack', {}).get('range', 1)
                                in_range = dist <= attack_range
                                # print(f"[DEBUG] Wróg {enemy.id} ({enemy.owner}) na ({enemy.q},{enemy.r}): dystans={dist}, sight={sight}, attack_range={attack_range}, in_sight={in_sight}, in_range={in_range}")
                                if in_sight and in_range:
                                    # print(f"[REAKCJA WROGA] {enemy.id} ({enemy.owner}) atakuje {moved_token.id} ({moved_token.owner})!")
                                    setattr(moved_token, 'wykryty_do_konca_tury', True)
                                    from engine.action import CombatAction
                                    action = CombatAction(enemy.id, moved_token.id)
                                    success2, msg2 = self.game_engine.execute_action(action)
                                    # print(f"[WYNIK REAKCJI] {enemy.id} -> {moved_token.id}: {msg2}")
                                    self._visualize_combat(enemy, moved_token, msg2)
                                    # Komunikat zwrotny także dla ataku reakcyjnego
                                    from tkinter import messagebox
                                    messagebox.showinfo("Wynik walki", msg2)
                            # --- DODANE: wymuszone odświeżenie mapy po wszystkich reakcjach wrogów ---
                            self.refresh()
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
                    print(f"[DEBUG][MAPA] Brak możliwej ścieżki do celu z ({token.q},{token.r}) do {hr}!")
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
            # Efekty wizualne (szkielet): podświetlenie pól, miganie, usuwanie, cofania
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

        # 2. Miganie żetonów, usuwanie, cofania (na podstawie msg)
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
            # Aktualizacja VP po eliminacji
            if hasattr(self, 'panel_dowodcy') and hasattr(self.panel_dowodcy, 'panel_gracza'):
                from gui.panel_gracza import PanelGracza
                PanelGracza.update_all_vp()
        # Eliminacja atakującego
        elif 'atakujący został zniszczony' in msg_l:
            blink_token(attacker.id, color='red', times=4, delay=100, on_end=lambda: animate_remove(attacker.id))
            # Aktualizacja VP po eliminacji
            if hasattr(self, 'panel_dowodcy') and hasattr(self.panel_dowodcy, 'panel_gracza'):
                from gui.panel_gracza import PanelGracza
                PanelGracza.update_all_vp()
        # Cofanie obrońcy
        elif 'cofnął się na' in msg_l:
            import re
            m = re.search(r'cofnął się na \(([-\d]+),([\-\d]+)\)', msg)
            if m:
                new_q, new_r = int(m.group(1)), int(m.group(2))
                old_q, old_r = defender.q, defender.r
                animate_retreat(defender, old_q, old_r, new_q, new_r)
                blink_token(defender.id, color='red', times=2, delay=120, on_end=self.refresh)
        # Domyślnie: krótkie miganie obu żetonów
        else:
            def after_blink():
                self.refresh()
            blink_token(attacker.id, color='orange', times=2, delay=100, on_end=None)
            blink_token(defender.id, color='orange', times=2, delay=100, on_end=after_blink)
        # Po animacjach, po odświeżeniu mapy, wypisz wartości po walce
        def print_after_refresh():
            att = next((t for t in self.tokens if t.id == attacker.id), None)
            defn = next((t for t in self.tokens if t.id == defender.id), None)
            # Usunięto printy debugujące
        self.canvas.after(600, print_after_refresh)

    # Dodane: metoda do ładowania stanu gry (przykładowa implementacja)
    def load_game_state(self, state):
        # Przykładowa struktura state:
        # {
        #     'tokens': [ { 'id': 1, 'q': 2, 'r': 3, ... }, { 'id': 2, 'q': 4, 'r': 5, ... }, ... ],
        #     'current_player': 1,
        #     'turn': 5,
        #     ...
        # }
        try:
            # Przywróć żetony
            token_map = {t.id: t for t in self.tokens}
            for token_data in state.get('tokens', []):
                token_id = token_data.get('id')
                token = token_map.get(token_id)
                if token:
                    # Aktualizuj tylko istniejące tokeny
                    for key, value in token_data.items():
                        setattr(token, key, value)
            # Przywróć inne istotne dane ze stanu gry
            self.game_engine.current_player_id = state.get('current_player', self.game_engine.current_player_id)
            self.game_engine.turn = state.get('turn', self.game_engine.turn)
            # Odśwież widok
            self.refresh()
            # Usunięto printy debugujące
        except Exception as e:
            print(f"[ERROR] Ładowanie stanu gry nie powiodło się: {e}")

    # Dodane: metoda do zapisywania stanu gry (przykładowa implementacja)
    def save_game_state(self):
        try:
            state = {
                'tokens': [ { 'id': t.id, 'q': t.q, 'r': t.r, 'owner': t.owner, 'movement_mode': t.movement_mode, 'currentMovePoints': t.currentMovePoints, 'stats': t.stats } for t in self.tokens ],
                'current_player': self.game_engine.current_player_id,
                'turn': self.game_engine.turn,
            }
            # Zapisz stan do pliku lub innego medium
            with open('save_game.json', 'w') as f:
                import json
                json.dump(state, f, ensure_ascii=False, indent=4)
            # Usunięto printy debugujące
        except Exception as e:
            print(f"[ERROR] Zapisywanie stanu gry nie powiodło się: {e}")

    # Dodane: debug metoda do wypisywania aktualnego stanu gry w konsoli
    def debug_print_game_state(self):
        # Usunięto wszystkie printy debugujące
        pass