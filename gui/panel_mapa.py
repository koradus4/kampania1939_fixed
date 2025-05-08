import tkinter as tk
from PIL import Image, ImageTk
from model.mapa import Mapa

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