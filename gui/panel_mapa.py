import tkinter as tk
from engine.hex_utils import get_hex_vertices
from PIL import Image, ImageTk
import os

class PanelMapa(tk.Frame):
    def __init__(self, parent, game_engine, bg_path: str, player_nation: str, width=800, height=600):
        super().__init__(parent)
        self.game_engine = game_engine
        self.map_model = self.game_engine.board
        self.player_nation = player_nation
        self.tokens = self.game_engine.tokens

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
        self.canvas.bind("<Button-3>", self._on_right_click)  # Dodaj obsługę prawego przycisku

        # żetony
        self.token_images = {}
        # Przekazanie obiektu gracza do panelu (potrzebne do filtrowania widoczności)
        self.player = getattr(game_engine, 'current_player_obj', None)
        self._draw_tokens_on_map()

    def _draw_hex_grid(self):
        self.canvas.delete("hex")
        s = self.map_model.hex_size
        cols = getattr(self.map_model, 'cols', 56)
        rows = getattr(self.map_model, 'rows', 40)
        for col in range(cols):
            for row in range(rows):
                # Konwersja offset -> axial (even-q)
                q = col
                r = row - (col // 2)
                cx, cy = self.map_model.hex_to_pixel(q, r)
                # Sprawdź, czy heks mieści się w obszarze mapy
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

    def _draw_tokens_on_map(self):
        self.canvas.delete("token")
        # Filtrowanie widoczności żetonów
        tokens = self.tokens
        if hasattr(self, 'player') and hasattr(self.player, 'role'):
            if self.player.role == 'Generał':
                # Generał widzi tylko żetony swojej nacji, należące do dowódców tej nacji
                tokens = [t for t in self.tokens if t.owner.endswith(f"({self.player.nation})") and t.owner != f"{self.player.id} ({self.player.nation})"]
            elif self.player.role == 'Dowódca':
                # Dowódca widzi tylko swoje żetony
                tokens = [t for t in self.tokens if t.owner == f"{self.player.id} ({self.player.nation})"]
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
                    self.canvas.create_image(x, y, image=tk_img, anchor="center", tags="token")
                    self.token_images[token.id] = tk_img
                except Exception:
                    pass

    def refresh(self):
        self._draw_hex_grid()
        self._draw_tokens_on_map()

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
                tx, ty = self.map_model.hex_to_pixel(token.q, token.r)
                hex_size = self.map_model.hex_size
                if abs(x - tx) < hex_size // 2 and abs(y - ty) < hex_size // 2:
                    clicked_token = token
                    break
        # Sprawdzenie właściciela żetonu dla dowódcy
        if clicked_token:
            if hasattr(self, 'player') and hasattr(self.player, 'id') and hasattr(self.player, 'nation'):
                expected_owner = f"{self.player.id} ({self.player.nation})"
                if clicked_token.owner != expected_owner:
                    from tkinter import messagebox
                    messagebox.showerror("Błąd", "Możesz ruszać tylko swoimi żetonami!")
                    return
            self.selected_token_id = clicked_token.id
        elif hr and self.selected_token_id:
            from engine.action import MoveAction
            token = next((t for t in self.tokens if t.id == self.selected_token_id), None)
            if token:
                action = MoveAction(token.id, hr[0], hr[1])
                success, msg = self.game_engine.execute_action(action, player=getattr(self, 'player', None))
                # Debug: punkty ruchu po ruchu
                token_engine = next((t for t in self.game_engine.tokens if t.id == token.id), None)
                print(f"[DEBUG] Po ruchu: {token.id} MP_GUI={getattr(token, 'currentMovePoints', '?')} MP_ENGINE={getattr(token_engine, 'currentMovePoints', '?')}")
                # Synchronizacja żetonów po ruchu
                self.tokens = self.game_engine.tokens
                if not success:
                    from tkinter import messagebox
                    messagebox.showerror("Błąd ruchu", msg)
                if success:
                    self.selected_token_id = None
                self.refresh()
        else:
            self.selected_token_id = None
        self.refresh()

    def _on_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_token = None
        for token in self.tokens:
            if token.q is not None and token.r is not None:
                tx, ty = self.map_model.hex_to_pixel(token.q, token.r)
                hex_size = self.map_model.hex_size
                if abs(x - tx) < hex_size // 2 and abs(y - ty) < hex_size // 2:
                    clicked_token = token
                    break
        if clicked_token:
            img_path = clicked_token.stats.get("image")
            if not img_path:
                nation = clicked_token.stats.get('nation', '')
                img_path = f"assets/tokens/{nation}/{clicked_token.id}/token.png"
            if not os.path.exists(img_path):
                img_path = "assets/tokens/default/token.png" if os.path.exists("assets/tokens/default/token.png") else None
            if img_path and os.path.exists(img_path):
                from PIL import Image, ImageTk
                img = Image.open(img_path)
                hex_size = self.map_model.hex_size
                scale = 3
                img = img.resize((hex_size*scale, hex_size*scale), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                # Wyświetl w nowym oknie
                top = tk.Toplevel(self)
                top.title(f"Powiększony żeton: {clicked_token.id}")
                label = tk.Label(top, image=tk_img)
                label.image = tk_img  # Trzymaj referencję
                label.pack()
                # Zamknij okno po kliknięciu
                label.bind("<Button-1>", lambda e: top.destroy())