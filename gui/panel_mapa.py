import tkinter as tk
from PIL import Image, ImageTk
from model.mapa import Mapa
from model.zetony import ZetonyMapy

class PanelMapa(tk.Frame):
    def __init__(self, parent, map_model: Mapa, bg_path: str, player_nation: str, width=800, height=600):
        super().__init__(parent)
        self.map_model = map_model
        self.player_nation = player_nation  # Dodano nację gracza

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
        self.zetony = ZetonyMapy()
        self.token_images = {}  # referencje do obrazków żetonów
        self._draw_tokens_on_map()

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
        # Rysuje wszystkie żetony na mapie na podstawie danych z ZetonyMapy
        print("[DEBUG] Start rysowania żetonów na mapie")
        for token in self.zetony.get_tokens_on_map():
            token_id = token["id"]
            q, r = token["q"], token["r"]
            print(f"[DEBUG] Próba rysowania żetonu: id={token_id}, q={q}, r={r}")
            token_data = self.zetony.get_token_data(token_id)
            if not token_data:
                print(f"[DEBUG] Brak danych żetonu w index.json: {token_id}")
                continue
            # Ścieżka do obrazka żetonu
            img_path = token_data.get("image")
            if not img_path:
                img_path = f"assets/tokens/{token_data['nation']}/{token_id}/token.png"
            print(f"[DEBUG] Ścieżka do obrazka: {img_path}")
            try:
                img = Image.open(img_path)
                # Skalowanie do rozmiaru heksa
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