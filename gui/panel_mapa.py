import tkinter as tk
from PIL import Image, ImageTk

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

        # tło mapy
        bg = Image.open(bg_path)
        self._bg = ImageTk.PhotoImage(bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self._bg)
        self.canvas.config(scrollregion=(0, 0, bg.width, bg.height))

        # rysuj siatkę i etykiety
        self._draw_hex_grid()

        # kliknięcia
        self.canvas.bind("<Button-1>", self._on_click)

        # żetony
        self.token_images = {}
        self._draw_tokens_on_map()

        # hover
        self._bind_hover()

    def _draw_hex_grid(self):
        self.canvas.delete("hex")
        for verts, (cx, cy), txt in self.map_model.get_overlay_items():
            flat = [coord for p in verts for coord in p]
            if "spawn" in txt:
                spawn_nation = txt.replace("spawn", "")
                if spawn_nation == self.player_nation.lower():
                    self.canvas.create_polygon(
                        flat,
                        outline="red",
                        fill="gray",
                        stipple="gray12",
                        tags="hex"
                    )
            elif txt.startswith("key"):
                self.canvas.create_polygon(
                    flat,
                    outline="red",
                    fill="",
                    width=1,
                    tags="hex"
                )
                self.canvas.create_text(
                    cx, cy,
                    text=txt.replace("key", ""),
                    anchor="center",
                    fill="blue",
                    tags="hex"
                )
            else:
                self.canvas.create_polygon(
                    flat,
                    outline="red",
                    fill="",
                    width=1,
                    tags="hex"
                )

    def _draw_tokens_on_map(self):
        print("[DEBUG] Start rysowania żetonów na mapie")
        tokens = [
            {'id': t.id, 'q': t.q, 'r': t.r} for t in self.tokens if t.q is not None and t.r is not None
        ]
        for token in tokens:
            token_id = token["id"]
            q, r = token["q"], token["r"]
            print(f"[DEBUG] Próba rysowania żetonu: id={token_id}, q={q}, r={r}")
            token_data = next((t for t in self.tokens if t.id == token_id), None)
            if not token_data:
                print(f"[DEBUG] Brak danych żetonu: {token_id}")
                continue
            img_path = token_data.stats.get("image")
            if not img_path:
                img_path = f"assets/tokens/{token_data.stats.get('nation','')}/{token_id}/token.png"
            print(f"[DEBUG] Ścieżka do obrazka: {img_path}")
            try:
                img = Image.open(img_path)
                hex_size = self.map_model.hex_size
                img = img.resize((hex_size, hex_size), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                x, y = self.map_model.hex_to_pixel(q, r)
                print(f"[DEBUG] Rysuję żeton {token_id} na pikselach: x={x}, y={y}, rozmiar={hex_size}")
                self.canvas.create_image(x, y, image=tk_img, anchor="center")
                self.token_images[token_id] = tk_img  # referencja, by nie znikł z pamięci
            except Exception as e:
                print(f"[DEBUG] Błąd ładowania żetonu {token_id}: {e}")
        print("[DEBUG] Koniec rysowania żetonów na mapie")

    def _on_hover(self, event):
        # Usuwa poprzedni powiększony żeton
        self.canvas.delete("hover_zoom")
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # Znajdź heks pod kursorem
        hr = self.map_model.coords_to_hex(x, y)
        if not hr:
            return
        q, r = hr
        # Sprawdź, czy na tym heksie jest żeton
        for token in self.tokens:
            if token.q == q and token.r == r:
                token_id = token.id
                token_data = next((t for t in self.tokens if t.id == token_id), None)
                if not token_data:
                    return
                img_path = token_data.stats.get("image")
                if not img_path:
                    img_path = f"assets/tokens/{token_data.stats.get('nation','')}/{token_id}/token.png"
                try:
                    img = Image.open(img_path)
                    hex_size = self.map_model.hex_size
                    zoom_size = int(hex_size * 2)
                    img = img.resize((zoom_size, zoom_size), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    x_pix, y_pix = self.map_model.hex_to_pixel(q, r)
                    self.canvas.create_image(x_pix, y_pix, image=tk_img, anchor="center", tags="hover_zoom")
                    # Przechowuj referencję, by nie znikł z pamięci
                    if not hasattr(self, '_hover_zoom_images'):
                        self._hover_zoom_images = []
                    self._hover_zoom_images.clear()
                    self._hover_zoom_images.append(tk_img)
                except Exception as e:
                    print(f"[DEBUG] Błąd ładowania powiększonego żetonu {token_id}: {e}")
                break

    def _bind_hover(self):
        self.canvas.bind("<Motion>", self._on_hover)

    def _unbind_hover(self):
        self.canvas.unbind("<Motion>")

    def _on_click(self, ev):
        x = self.canvas.canvasx(ev.x)
        y = self.canvas.canvasy(ev.y)
        hr = self.map_model.coords_to_hex(x, y)
        if hr and hasattr(self, "_click_cb"):
            self._click_cb(*hr)

    def bind_click_callback(self, cb):
        self._click_cb = cb

    def refresh(self):
        self._draw_hex_grid()
        self._draw_tokens_on_map()
        self._bind_hover()