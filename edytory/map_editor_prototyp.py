import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import json
import math
import os
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Folder „assets” obok map_editor_prototyp.py
ASSET_ROOT = Path("C:/Users/klif/kampania1939_fixed/assets")
ASSET_ROOT.mkdir(exist_ok=True)

# Dodajemy folder data na potrzeby silnika i testów
DATA_ROOT = Path("C:/Users/klif/kampania1939_fixed/data")
DATA_ROOT.mkdir(exist_ok=True)

DEFAULT_MAP_FILE = str(ASSET_ROOT / "mapa_globalna.jpg")
DEFAULT_MAP_DIR = ASSET_ROOT
# Zmieniamy domyślną ścieżkę zapisu danych mapy na data/map_data.json
DATA_FILENAME_WORKING = DATA_ROOT / "map_data.json"

def to_rel(path: str) -> str:
    """Zwraca ścieżkę assets/... względem katalogu projektu."""
    try:
        return str(Path(path).relative_to(ASSET_ROOT))
    except ValueError:
        return str(path)   # gdy ktoś wybierze plik spoza assets/

# ----------------------------
# Konfiguracja rodzajów terenu
# ----------------------------
TERRAIN_TYPES = {
    "teren_płaski": {"move_mod": 0, "defense_mod": 0},
    "mała rzeka": {"move_mod": 2, "defense_mod": 1},
    "duża rzeka": {"move_mod": 5, "defense_mod": -1},  # przekraczalna, koszt ruchu 6
    "las": {"move_mod": 2, "defense_mod": 2},
    "bagno": {"move_mod": 3, "defense_mod": 1},
    "mała miejscowość": {"move_mod": 1, "defense_mod": 2},
    "miasto": {"move_mod": 2, "defense_mod": 2},
    "most": {"move_mod": 0, "defense_mod": -1}
}

# mapowanie państw → kolor mgiełki
SPAWN_OVERLAY = {
    "Polska": "#ffcccc;#ffffff",   # białe od góry, czerwone na dole
    "Niemcy": "#ccccff"    # jasnoniebieska
}

def zapisz_dane_hex(hex_data, filename=DATA_FILENAME_WORKING):
    'Zapisuje dane terenu do pliku JSON (roboczy plik).'
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print(f"Nie można utworzyć katalogu {directory}: {e}")
            # Jeśli nie można utworzyć katalogu, zapisz w katalogu skryptu
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(filename))
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(hex_data, f, indent=2, ensure_ascii=False)

def wczytaj_dane_hex(filename=DATA_FILENAME_WORKING):
    'Wczytuje dane terenu z pliku JSON.'
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ----------------------------
# Konfiguracja mapy
# ----------------------------
CONFIG = {
    'map_settings': {
        'map_image_path': r"C:\\ścieżka\\do\\tła\\mapa.jpg",  # Pełna ścieżka do obrazu tła mapy
        'hex_size': 30,
        'grid_cols': 56,   # liczba kolumn heksów
        'grid_rows': 40    # liczba wierszy heksów
    }
}

def point_in_polygon(x, y, poly):
    'Sprawdza, czy punkt (x,y) leży wewnątrz wielokąta poly.'
    num = len(poly)
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
           (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1] + 1e-10) + poly[i][0]):
            c = not c
        j = i
    return c

def get_hex_vertices(center_x, center_y, s):
    # Zwraca wierzchołki heksu (POINTY‑TOP) w układzie axial.
    return [
        (center_x - s, center_y),
        (center_x - s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s, center_y),
        (center_x + s/2, center_y + (math.sqrt(3)/2)*s),
        (center_x - s/2, center_y + (math.sqrt(3)/2)*s)
    ]

def offset_to_axial(col: int, row: int) -> tuple[int, int]:
    # Pointy-top even-q offset: q = col, r = row - (col // 2)
    q = col
    r = row - (col // 2)
    return q, r

class MapEditor:
    def __init__(self, root, config):
        self.root = root
        self.root.configure(bg="darkolivegreen")
        self.config = config["map_settings"]
        self.map_image_path = self.get_last_modified_map()  # Automatyczne otwieranie ostatniej mapy
        self.map_image_path = self.get_last_modified_map()
        
        self.hex_size = self.config.get("hex_size", 30)
        self.hex_defaults = {"defense_mod": 0, "move_mod": 0}
        self.current_working_file = DATA_FILENAME_WORKING
        
        # Słownik z danymi terenu dla niestandardowych heksów
        self.hex_data = {}
        self.key_points = {}
        self.spawn_points = {}
        
        # Inicjalizacja aktualnie wybranego heksu
        self.selected_hex = None  # Dodano inicjalizację atrybutu

        # Lista dostępnych typów kluczowych punktów i ich wartości
        self.available_key_point_types = {
            "most": 50,
            "miasto": 100,
            "węzeł komunikacyjny": 75,
            "fortyfikacja": 150
        }

        # Lista dostępnych nacji
        self.available_nations = ["Polska", "Niemcy"]

        # Atrybut do przechowywania mapowania hex_id → nazwa/obiekt żetonu
        self.hex_tokens = {}  # mapuje hex_id → ścieżka do pliku PNG z żetonem        # Przechowuje referencje do obrazków żetonów
        self.token_images = {}  # Przechowuje referencje do obrazków żetonów

        # Nowe atrybuty dla systemu klik→zaznacz→klik
        self.selected_token_for_deployment = None  # Przechowuje wybrany żeton do umieszczenia
        self.token_selection_window = None  # Referencja do okna wyboru żetonów
        self.token_buttons = {}  # Przechowuj referencje do przycisków żetonów
        self.selected_token_label = None  # Label pokazujący wybrany żeton

        # Zbuduj GUI
        self.build_gui()
        # Wczytaj mapę i dane
        self.load_map_image()
        self.load_data()

    def get_last_modified_map(self):
        # zawsze używamy predefiniowanej mapy
        if os.path.exists(DEFAULT_MAP_FILE):
            return DEFAULT_MAP_FILE
        # jeśli nie ma pliku, pozwalamy wybrać ręcznie
        messagebox.showinfo("Informacja", "Nie znaleziono pliku domyślnej mapy. Wybierz ręcznie.")
        return filedialog.askopenfilename(
            title="Wybierz mapę",
            initialdir=os.path.dirname(DEFAULT_MAP_FILE),
            filetypes=[("Obrazy", "*.jpg *.png *.bmp"), ("Wszystkie pliki", "*.*")]
        )

    def build_gui(self):
        'Tworzy interfejs użytkownika.'
        # Panel boczny z przyciskami
        self.panel_frame = tk.Frame(self.root, bg="darkolivegreen", relief=tk.RIDGE, bd=5)
        self.panel_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Sekcja przycisków operacji
        buttons_frame = tk.Frame(self.panel_frame, bg="darkolivegreen")
        buttons_frame.pack(side=tk.TOP, fill=tk.X)

        # Przycisk "Otwórz Mapę + Dane"
        self.open_map_and_data_button = tk.Button(
            buttons_frame, text="Otwórz Mapę + Dane", command=self.open_map_and_data,
            bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white"
        )
        self.open_map_and_data_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Zapisz dane mapy"
        self.save_map_and_data_button = tk.Button(
            buttons_frame, text="Zapisz dane mapy", command=self.save_map_and_data,
            bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white"
        )
        self.save_map_and_data_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Reset danych" (nieaktywny)
        self.reset_data_button = tk.Button(
            buttons_frame, text="Reset danych", command=self.clear_variables,
            bg="saddlebrown", fg="white", state="disabled",  # Ustawiono stan na disabled
            activebackground="saddlebrown", activeforeground="white"
        )
        self.reset_data_button.pack(padx=5, pady=5, fill=tk.X)

        # Dodanie sekcji "Rodzaje terenu"
        terrain_frame = tk.LabelFrame(self.panel_frame, text="Rodzaje terenu", bg="darkolivegreen", fg="white",
                                      font=("Arial", 10, "bold"))
        terrain_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.current_brush = None
        self.terrain_buttons = {}

        for terrain_key in TERRAIN_TYPES.keys():
            btn = tk.Button(
                terrain_frame,
                text=terrain_key.replace("_", " ").title(),
                width=16,
                bg="saddlebrown",         # stały kolor tła
                fg="white",               # kolor tekstu
                activebackground="saddlebrown",
                activeforeground="white",
                command=lambda k=terrain_key: self.toggle_brush(k)
            )
            btn.pack(padx=5, pady=2, fill=tk.X)
            self.terrain_buttons[terrain_key] = btn

        # Przerwa między sekcjami
        tk.Label(self.panel_frame, text="", bg="darkolivegreen").pack(pady=10)

        # Dodanie sekcji "Punkty kluczowe"
        key_points_frame = tk.LabelFrame(self.panel_frame, text="Punkty kluczowe", bg="darkolivegreen", fg="white",
                                         font=("Arial", 10, "bold"))
        key_points_frame.pack(fill=tk.X, padx=5, pady=5)
        self.add_key_point_button = tk.Button(key_points_frame, text="Dodaj kluczowy punkt", command=self.add_key_point_dialog,
                                              bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
        self.add_key_point_button.pack(padx=5, pady=5, fill=tk.X)

        # Dodanie sekcji "Punkty zrzutu"
        spawn_points_frame = tk.LabelFrame(self.panel_frame, text="Punkty zrzutu", bg="darkolivegreen", fg="white",
                                           font=("Arial", 10, "bold"))
        spawn_points_frame.pack(fill=tk.X, padx=5, pady=5)
        self.add_spawn_point_button = tk.Button(spawn_points_frame, text="Dodaj punkt wystawienia", command=self.add_spawn_point_dialog,
                                                bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
        self.add_spawn_point_button.pack(padx=5, pady=5, fill=tk.X)
        
        # Dodanie sekcji "Reset wybranego heksu"
        reset_hex_frame = tk.LabelFrame(self.panel_frame, text="Reset wybranego heksu", bg="darkolivegreen", fg="white",
                                        font=("Arial", 10, "bold"))
        reset_hex_frame.pack(fill=tk.X, padx=5, pady=5)
        self.reset_hex_button = tk.Button(reset_hex_frame, text="Resetuj wybrany heks", command=self.reset_selected_hex,
                                          bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
        self.reset_hex_button.pack(padx=5, pady=5, fill=tk.X)

        # Dodanie sekcji "Wystaw żeton"
        deploy_token_frame = tk.LabelFrame(self.panel_frame, text="Wystaw żeton", bg="darkolivegreen", fg="white",
                                          font=("Arial", 10, "bold"))
        deploy_token_frame.pack(fill=tk.X, padx=5, pady=5)
        self.deploy_token_button = tk.Button(deploy_token_frame, text="Wystaw żeton", command=self.deploy_token_dialog,
                                             bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
        self.deploy_token_button.pack(padx=5, pady=5, fill=tk.X)

        # Dodanie przycisku eksportu rozmieszczenia żetonów
        self.export_tokens_button = tk.Button(
            self.panel_frame,
            text="Eksportuj rozmieszczenie żetonów",
            command=self.export_start_tokens,
            bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white"
        )
        self.export_tokens_button.pack(padx=5, pady=5, fill=tk.X)

        # Sekcja informacyjna o wybranym heksie
        self.control_panel_frame = tk.Frame(self.panel_frame, bg="darkolivegreen", relief=tk.RIDGE, bd=5)
        self.control_panel_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=5, pady=5, expand=True)
        self.control_canvas = tk.Canvas(self.control_panel_frame, bg="darkolivegreen", highlightthickness=0)
        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.control_panel_frame, orient=tk.VERTICAL, command=self.control_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_canvas.configure(yscrollcommand=scrollbar.set)
        self.control_canvas.bind('<Configure>', lambda e: self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all")))
        self.control_content = tk.Frame(self.control_canvas, bg="darkolivegreen")
        self.control_canvas.create_window((0, 0), window=self.control_content, anchor="nw")

        tk.Label(self.control_content, text="Informacje o heksie", 
                 bg="darkolivegreen", fg="white", font=("Arial", 10, "bold")).pack()
        self.hex_info_label = tk.Label(self.control_content, text="Heks: brak", bg="darkolivegreen", fg="white",
                                       font=("Arial", 10))
        self.hex_info_label.pack(anchor="w")
        self.terrain_info_label = tk.Label(self.control_content, text="Teren: brak", bg="darkolivegreen", fg="white",
                                           font=("Arial", 10))
        self.terrain_info_label.pack(anchor="w")
        self.modifiers_info_label = tk.Label(self.control_content, text="Modyfikatory: brak", bg="darkolivegreen", fg="white",
                                            font=("Arial", 10))
        self.modifiers_info_label.pack(anchor="w")
        self.key_point_info_label = tk.Label(self.control_content, text="Kluczowy punkt: brak", bg="darkolivegreen", fg="white",
                                             font=("Arial", 10))
        self.key_point_info_label.pack(anchor="w")
        self.spawn_info_label = tk.Label(self.control_content, text="Punkt wystawiania: brak", bg="darkolivegreen", fg="white",
                                         font=("Arial", 10))
        self.spawn_info_label.pack(anchor="w")
        # Dodanie informacji o żetonie
        self.token_info_label = tk.Label(self.control_content, text="Żeton: brak", bg="darkolivegreen", fg="white",
                                         font=("Arial", 10))
        self.token_info_label.pack(anchor="w")

        # Pole rysowania mapy z przewijaniem
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", cursor="cross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dodanie suwaka pionowego
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Przeniesienie poziomego suwaka do root
        self.h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_click)  # Prawy klik też obsługuje on_canvas_click
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<Motion>", self.on_canvas_hover)

    def select_default_map_path(self):
        'Pozwala użytkownikowi wybrać nowe tło mapy.'
        file_path = filedialog.askopenfilename(
            title="Wybierz domyślną mapę",
            filetypes=[("Obrazy", "*.jpg *.png *.bmp"), ("Wszystkie pliki", "*.*")]
        )
        if file_path:
            self.map_image_path = file_path
            self.config["map_image_path"] = file_path
            messagebox.showinfo("Sukces", "Wybrano nową domyślną mapę.")
        else:
            messagebox.showinfo("Anulowano", "Nie wybrano nowej mapy.")

    def load_map_image(self):
        'Wczytuje obraz mapy jako tło i ustawia rozmiary.'
        try:
            self.bg_image = Image.open(self.map_image_path).convert("RGB")
        except Exception as e:
            # jeśli nie udało się wczytać domyślnej mapy, poproś użytkownika o wybranie pliku
            messagebox.showwarning("Uwaga", "Nie udało się załadować domyślnej mapy. Wskaż plik ręcznie.")
            file = filedialog.askopenfilename(
                title="Wybierz mapę",
                filetypes=[("Obrazy", "*.jpg *.png *.bmp"), ("Wszystkie pliki", "*.*")]
            )
            if file:
                self.map_image_path = file
                return self.load_map_image()
            else:
                return
        self.world_width, self.world_height = self.bg_image.size
        self.photo_bg = ImageTk.PhotoImage(self.bg_image)
        # Ustaw obszar przewijania
        self.canvas.config(scrollregion=(0, 0, self.world_width, self.world_height))
        # Rysuj ponownie siatkę
        self.draw_grid()

    def draw_grid(self):
        """Rysuje siatkę heksów i aktualizuje wyświetlane żetony."""
        self.canvas.delete("all")
        if not hasattr(self, 'photo_bg'):
            self.photo_bg = ImageTk.PhotoImage(Image.new("RGB", (1, 1), (255, 255, 255)))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
        self.hex_centers = {}
        s = self.hex_size
        hex_height = math.sqrt(3) * s
        horizontal_spacing = 1.5 * s
        grid_cols = self.config.get("grid_cols")
        grid_rows = self.config.get("grid_rows")

        # GENERUJEMY SIATKĘ W UKŁADZIE OFFSETOWYM EVEN-Q (prostokąt)
        for col in range(grid_cols):
            for row in range(grid_rows):
                # Konwersja offset -> axial (even-q)
                q = col
                r = row - (col // 2)
                center_x = s + col * horizontal_spacing
                center_y = (s * math.sqrt(3) / 2) + row * hex_height
                if col % 2 == 1:
                    center_y += hex_height / 2
                if center_x + s > self.world_width or center_y + (s * math.sqrt(3) / 2) > self.world_height:
                    continue
                hex_id = f"{q},{r}"
                self.hex_centers[hex_id] = (center_x, center_y)

                # Dodanie domyślnych danych terenu płaskiego, jeśli brak danych
                if hex_id not in self.hex_data:
                    self.hex_data[hex_id] = {
                        "terrain_key": "teren_płaski",
                        "move_mod": 0,  # domyślnie teren przejezdny
                        "defense_mod": 0
                    }

                terrain = self.hex_data.get(hex_id, self.hex_defaults)
                self.draw_hex(hex_id, center_x, center_y, s, terrain)

        # Rysowanie żetonów na mapie
        self.canvas.image_store = []  # lista na referencje do obrazków
        for hex_id, terrain in self.hex_data.items():
            token = terrain.get("token")
            if token and "image" in token and hex_id in self.hex_centers:
                # normalizuj slashy na wszelki wypadek
                token["image"] = token["image"].replace("\\", "/")
                img_path = ASSET_ROOT / token["image"]
                if not img_path.exists():
                    print(f"[WARN] Missing token image: {img_path}")
                    continue          # pomijamy brakujący plik
                img = Image.open(img_path).resize((self.hex_size, self.hex_size))
                tk_img = ImageTk.PhotoImage(img)
                cx, cy = self.hex_centers[hex_id]
                self.canvas.create_image(cx, cy, image=tk_img)
                self.canvas.image_store.append(tk_img)

        # nakładka mgiełki dla punktów zrzutu
        for nation, hex_list in self.spawn_points.items():
            if nation == "Polska":
                for hex_id in hex_list:
                    if hex_id in self.hex_centers:
                        cx, cy = self.hex_centers[hex_id]
                        verts = get_hex_vertices(cx, cy, self.hex_size)
                        self.canvas.create_polygon(
                            verts,
                            fill="white",  # Górna część biała
                            outline="",
                            stipple="gray25",
                            tags=f"spawn_{nation}_{hex_id}"
                        )
                        self.canvas.create_polygon(
                            verts,
                            fill="red",  # Dolna część czerwona
                            outline="",
                            stipple="gray25",
                            tags=f"spawn_{nation}_{hex_id}"
                        )
            else:
                for hex_id in hex_list:
                    if hex_id in self.hex_centers:
                        cx, cy = self.hex_centers[hex_id]
                        verts = get_hex_vertices(cx, cy, self.hex_size)
                        self.canvas.create_polygon(
                            verts,
                            fill=SPAWN_OVERLAY.get(nation, "#ffffff"),
                            outline="",
                            stipple="gray25",
                            tags=f"spawn_{nation}_{hex_id}"
                        )

        # rysowanie etykiet kluczowych punktów
        for hex_id, kp in self.key_points.items():
            if hex_id in self.hex_centers:
                cx, cy = self.hex_centers[hex_id]
                label = f"{kp['type']} ({kp['value']})"
                self.canvas.create_text(
                    cx, cy - self.hex_size * 0.6,
                    text=label,
                    fill="yellow",
                    font=("Arial", 10, "bold"),
                    tags=f"key_point_label_{hex_id}"
                )

        # Podświetlenie wybranego heksu
        if self.selected_hex is not None:
            self.highlight_hex(self.selected_hex)

    def draw_hex(self, hex_id, center_x, center_y, s, terrain=None):
        'Rysuje pojedynczy heksagon na canvasie wraz z tekstem modyfikatorów.'
        points = get_hex_vertices(center_x, center_y, s)
        self.canvas.create_polygon(points, outline="red", fill="", width=2, tags=hex_id)
        # usuwamy poprzedni tekst
        self.canvas.delete(f"tekst_{hex_id}")
        # rysujemy modyfikatory tylko jeśli ten heks ma niestandardowe dane
        if hex_id in self.hex_data:
            move_mod = terrain.get('move_mod', 0)
            defense_mod = terrain.get('defense_mod', 0)
            tekst = f"M:{move_mod} D:{defense_mod}"
            self.canvas.create_text(
                center_x, center_y,
                text=tekst,
                fill="blue",
                font=("Arial", 10),
                anchor="center",
                tags=f"tekst_{hex_id}"
            )

    def get_clicked_hex(self, x, y):
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                return hex_id  # Zwracaj hex_id jako string "q,r"
        return None

    def on_canvas_click(self, event):
        """Obsługuje kliknięcie myszką na canvasie - zaznacza heks i wyświetla jego dane LUB umieszcza wybrany żeton."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        hex_id = self.get_clicked_hex(x, y)
        
        if hex_id:
            # PRAWY KLIK - usuń żeton z heksa i przywróć do listy
            if event.num == 3:  # Prawy przycisk myszy
                self.remove_token_from_hex(hex_id)
                return
                
            # SPRAWDŹ CZY MAM WYBRANY ŻETON DO UMIESZCZENIA
            if self.selected_token_for_deployment:
                self.place_token_on_hex(self.selected_token_for_deployment, hex_id)
                self.cancel_token_selection()  # Wyczyść wybór po umieszczeniu
                return
            
            # NORMALNY TRYB - zaznaczanie heksu lub malowanie pędzlem
            if self.current_brush:
                q, r = map(int, hex_id.split(","))
                self.paint_hex((q, r), self.current_brush)
                return
                
            # Zaznacz heks i pokaż info
            self.selected_hex = hex_id
            self.highlight_hex(hex_id)
            terrain = self.hex_data.get(hex_id, self.hex_defaults)
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            token_data = terrain.get("token", {})
            if token_data:
                token_png = token_data.get("image", "brak")
                self.token_info_label.config(text=f"Żeton: {token_png}")
            else:
                self.token_info_label.config(text="Żeton: brak")
            messagebox.showinfo("Informacja o heksie",
                                f"Heks: {hex_id}\nModyfikator ruchu: {move_mod}\nModyfikator obrony: {defense_mod}")
        else:
            messagebox.showinfo("Informacja", "Kliknij wewnątrz heksagonu.")

    def highlight_hex(self, hex_id):
        'Oznacza wybrany heks żółtą obwódką.'
        self.canvas.delete("highlight")
        if hex_id in self.hex_centers:
            cx, cy = self.hex_centers[hex_id]
            s = self.hex_size
            self.canvas.create_oval(cx - s, cy - s, cx + s, cy + s,
                                    outline="yellow", width=3, tags="highlight")

    def on_canvas_hover(self, event):
        'Wyświetla informacje o heksie przy najechaniu myszką oraz powiększa heks z żetonem.'
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        hex_id = self.get_clicked_hex(x, y)
        self.canvas.delete("hover_zoom")  # Usuwa poprzedni powiększony heks
        if hex_id:
            terrain = self.hex_data.get(hex_id, self.hex_defaults)
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            key_point = self.key_points.get(hex_id, None)
            spawn_nations = [n for n, hexes in self.spawn_points.items() if hex_id in hexes]
            token = terrain.get("token", {})
            key = terrain.get("terrain_key", "płaski")
            self.terrain_info_label.config(text=f"Teren: {key}")
            token_png = token.get("image", "brak")
            self.token_info_label.config(text=f"Żeton: {token_png}")
            self.hex_info_label.config(text=f"Heks: {hex_id}")
            self.modifiers_info_label.config(text=f"Modyfikatory: Ruch: {move_mod}, Obrona: {defense_mod}")
            if key_point:
                self.key_point_info_label.config(text=f"Kluczowy punkt: {key_point['type']} ({key_point['value']})")
            else:
                self.key_point_info_label.config(text="Kluczowy punkt: brak")
            if spawn_nations:
                self.spawn_info_label.config(text=f"Punkt wystawiania: {', '.join(spawn_nations)}")
            else:
                self.spawn_info_label.config(text="Punkt wystawienia: brak")

            # --- POWIĘKSZENIE HEKSA Z ŻETONEM ---
            if token and "image" in token and hex_id in self.hex_centers:
                cx, cy = self.hex_centers[hex_id]
                s_zoom = int(self.hex_size * 1.5)
                points = get_hex_vertices(cx, cy, s_zoom)
                self.canvas.create_polygon(
                    points, outline="orange", fill="#ffffcc", width=3, tags="hover_zoom"
                )
                label = f"M:{move_mod} D:{defense_mod}"
                if token.get('unit'):
                    label += f"\n{token.get('unit')}"
                self.canvas.create_text(
                    cx, cy, text=label, fill="black", font=("Arial", 14, "bold"), tags="hover_zoom"
                )
                # Wyświetl powiększony żeton
                img_path = ASSET_ROOT / token["image"]
                if img_path.exists():
                    try:
                        img = Image.open(img_path).resize((s_zoom, s_zoom))
                        tk_img = ImageTk.PhotoImage(img)
                        self.canvas.create_image(cx, cy, image=tk_img, tags="hover_zoom")
                        # Przechowuj referencję, by nie znikł z pamięci
                        if not hasattr(self, '_hover_zoom_images'):
                            self._hover_zoom_images = []
                        self._hover_zoom_images.append(tk_img)
                    except Exception:
                        pass
        else:
            self.hex_info_label.config(text="Heks: brak")
            self.terrain_info_label.config(text="Teren: brak")
            self.modifiers_info_label.config(text="Modyfikatory: brak")
            self.key_point_info_label.config(text="Kluczowy punkt: brak")
            self.spawn_info_label.config(text="Punkt wystawiania: brak")
            self.token_info_label.config(text="Żeton: brak")
        # Czyść referencje do obrazków, jeśli nie ma powiększenia
        if not hex_id and hasattr(self, '_hover_zoom_images'):
            self._hover_zoom_images.clear()

    def save_data(self):
        'Zapisuje aktualne dane (teren, kluczowe punkty, spawn_points) do pliku JSON.'
        # --- USUWANIE MARTWYCH ŻETONÓW ---
        for hex_id, terrain in list(self.hex_data.items()):
            token = terrain.get("token")
            if token and "image" in token:
                img_path = ASSET_ROOT / token["image"]
                if not img_path.exists():
                    terrain.pop("token", None)
        # --- KONIEC USUWANIA ---
        # ZAPISZ CAŁĄ SIATKĘ HEKSÓW (nie tylko zmienione)
        map_data = {
            "meta": {
                "hex_size": self.hex_size,
                "cols": self.config.get("grid_cols"),
                "rows": self.config.get("grid_rows"),
                "coord_system": "axial",
                "orientation": "pointy"
            },
            "terrain": self.hex_data,
            "key_points": self.key_points,
            "spawn_points": self.spawn_points
        }
        self.current_working_file = self.get_working_data_path()
        print(f"Zapisywanie danych do: {self.current_working_file}")
        with open(self.current_working_file, "w", encoding="utf-8") as f:
            import json
            json.dump(map_data, f, indent=2, ensure_ascii=False)
        # messagebox.showinfo("Zapisano", f"Dane mapy zostały zapisane w:\n{self.current_working_file}\n"
        #                                 f"Liczba kluczowych punktów: {len(self.key_points)}\n"
        #                                 f"Liczba punktów wystawienia: {sum(len(v) for v in self.spawn_points.values())}")

    def load_data(self):
        'Wczytuje dane z pliku roboczego (teren, kluczowe i spawn).'
        self.current_working_file = self.get_working_data_path()
        print(f"Wczytywanie danych z: {self.current_working_file}")
        loaded_data = wczytaj_dane_hex(self.current_working_file)
        if loaded_data:
            orientation = loaded_data.get("meta", {}).get("orientation", "pointy")
            self.orientation = orientation  # przechowaj w obiekcie, przyda się GUI
            if "meta" not in loaded_data:          # plik starego formatu
                self.hex_data = loaded_data
                self.key_points = {}
                self.spawn_points = {}
            else:
                self.hex_data   = loaded_data.get("terrain", {})
                self.key_points = loaded_data.get("key_points", {})
                self.spawn_points = loaded_data.get("spawn_points", {})
            self.hex_tokens = {
                hex_id: terrain["image"]
                for hex_id, terrain in self.hex_data.items()
                if "image" in terrain and os.path.exists(terrain["image"])
            }
            # MIGRACJA starej struktury tokenów
            for hid, hinfo in list(self.hex_data.items()):
                # 1) absolutna ścieżka w korzeniu heksu -> token + rel
                if "image" in hinfo:
                    img = hinfo.pop("image")
                    hinfo["token"] = {"unit": Path(img).stem, "image": to_rel(img)}

                # 2) przenieś png_file do image, jeśli jeszcze nie przeniesione
                if "token" in hinfo and "png_file" in hinfo["token"]:
                    pf = hinfo["token"].pop("png_file")
                    if "image" not in hinfo["token"]:
                        hinfo["token"]["image"] = to_rel(pf)

                # 3) upewnij się, że image jest relatywne
                if "token" in hinfo and "image" in hinfo["token"]:
                    hinfo["token"]["image"] = to_rel(hinfo["token"]["image"])
            # zawsze upewnij się, że tło jest załadowane
            self.load_map_image()

            # i dopiero potem rysuj grid
            self.draw_grid()
            messagebox.showinfo("Wczytano", f"Dane mapy zostały wczytane z:\n{self.current_working_file}\n"
                                           f"Liczba kluczowych punktów: {len(self.key_points)}\n"
                                           f"Liczba punktów wystawienia: {sum(len(v) for v in self.spawn_points.values())}")
        else:
            messagebox.showinfo("Informacja", f"Brak danych do wczytania lub plik nie istnieje.")

    def clear_variables(self):
        'Kasuje wszystkie niestandardowe ustawienia mapy (reset do płaskiego terenu).'
        answer = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zresetować mapę do domyślnego terenu płaskiego?")
        if answer:
            self.hex_data = {}
            self.key_points = {}
            self.spawn_points = {}
            zapisz_dane_hex({"terrain": {}, "key_points": {}, "spawn_points": {}}, self.current_working_file)
            self.draw_grid()
            messagebox.showinfo("Zresetowano", "Mapa została zresetowana do domyślnego terenu płaskiego.")

    def save_map_and_data(self):
        """Zapisuje tylko dane JSON mapy."""
        try:
            self.save_data()  # Zapisuje dane JSON
            messagebox.showinfo("Sukces", "Dane mapy zostały zapisane pomyślnie.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać danych mapy: {e}")

    def open_map_and_data(self):
        """Otwiera mapę i wczytuje dane."""
        try:
            # Domyślna ścieżka do mapy
            map_path = filedialog.askopenfilename(
                initialdir=DEFAULT_MAP_DIR,
                title="Wybierz mapę",
                filetypes=[("Obrazy", "*.jpg *.png *.bmp"), ("Wszystkie pliki", "*.*")]
            )
            if map_path:
                self.map_image_path = map_path
                self.load_map_image()
                self.load_data()
                messagebox.showinfo("Sukces", "Mapa i dane zostały pomyślnie wczytane.")
            else:
                messagebox.showinfo("Anulowano", "Nie wybrano mapy.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się otworzyć mapy i danych: {e}")

    def add_key_point_dialog(self):
        'Okno dialogowe do dodawania kluczowego punktu na wybranym heksie.'
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Dodaj kluczowy punkt")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Wybierz typ punktu:", font=("Arial", 10)).pack(pady=10)
        point_types = list(self.available_key_point_types.keys())
        selected_type = tk.StringVar(value=point_types[0])
        tk.OptionMenu(dialog, selected_type, *point_types).pack()
        def save_key_point():
            ptype = selected_type.get()
            value = self.available_key_point_types[ptype]
            self.key_points[self.selected_hex] = {"type": ptype, "value": value}
            self.save_data()
            self.draw_key_point(self.selected_hex, ptype, value)
            messagebox.showinfo("Sukces", f"Dodano kluczowy punkt '{ptype}' o wartości {value} na heksie {self.selected_hex}.")
            dialog.destroy()
        tk.Button(dialog, text="Zapisz", command=save_key_point, bg="green", fg="white").pack(pady=10)
        tk.Button(dialog, text="Anuluj", command=dialog.destroy, bg="red", fg="white").pack(pady=5)

    def add_spawn_point_dialog(self):
        'Okno dialogowe do dodawania punktu wystawienia dla nacji.'
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Dodaj punkt wystawienia")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Wybierz nację:", font=("Arial", 10)).pack(pady=10)
        selected_nation = tk.StringVar(value=self.available_nations[0])
        tk.OptionMenu(dialog, selected_nation, *self.available_nations).pack()
        def save_spawn_point():
            nation = selected_nation.get()
            self.spawn_points.setdefault(nation, []).append(self.selected_hex)
            self.save_data()
            self.draw_grid()  # Odśwież rysunek mapy, aby zobaczyć mgiełkę
            messagebox.showinfo("Sukces", f"Dodano punkt wystawienia dla nacji '{nation}' na heksie {self.selected_hex}.")
            dialog.destroy()
        tk.Button(dialog, text="Zapisz", command=save_spawn_point, bg="green", fg="white").pack(pady=10)
        tk.Button(dialog, text="Anuluj", command=dialog.destroy, bg="red", fg="white").pack(pady=5)

    def draw_key_point(self, hex_id, point_type, value):
        'Rysuje na canvasie etykietę kluczowego punktu.'
        if hex_id in self.hex_centers:
            cx, cy = self.hex_centers[hex_id]
            self.canvas.create_text(cx, cy, text=f"{point_type}\n({value})", fill="yellow",
                                    font=("Arial", 10, "bold"), tags=f"key_point_{hex_id}")

    def apply_terrain(self, terrain_key):
        'Przypisuje wybrany typ terenu do aktualnie zaznaczonego heksu.'
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return
        terrain = TERRAIN_TYPES.get(terrain_key)
        if terrain:
            # Sprawdź, czy teren jest domyślny
            if (terrain.get('move_mod', 0) == self.hex_defaults.get('move_mod', 0) and
                terrain.get('defense_mod', 0) == self.hex_defaults.get('defense_mod', 0)):
                # Jeśli teren jest domyślny, usuń wpis z hex_data
                if self.selected_hex in self.hex_data:
                    del self.hex_data[self.selected_hex]
            else:
                # W przeciwnym razie, dodaj/zaktualizuj wpis z kluczem terenu
                self.hex_data[self.selected_hex] = {
                    "terrain_key": terrain_key,
                    "move_mod": terrain["move_mod"],
                    "defense_mod": terrain["defense_mod"]
                }
            # Zapisz dane i odrysuj heks
            self.save_data()
            cx, cy = self.hex_centers[self.selected_hex]
            self.draw_hex(self.selected_hex, cx, cy, self.hex_size, terrain)
            messagebox.showinfo("Zapisano", f"Dla heksu {self.selected_hex} ustawiono teren: {terrain_key}")
        else:
            messagebox.showerror("Błąd", "Niepoprawny rodzaj terenu.")

    def reset_selected_hex(self):
        """Czyści wszystkie dane przypisane do wybranego heksu i aktualizuje plik start_tokens.json."""
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return

        # Usuwanie danych przypisanych do heksu
        self.hex_data.pop(self.selected_hex, None)
        self.key_points.pop(self.selected_hex, None)
        for nation, hexes in self.spawn_points.items():
            if self.selected_hex in hexes:
                hexes.remove(self.selected_hex)
        # Usuwanie żetonu z hex_tokens
        self.hex_tokens.pop(self.selected_hex, None)

        # --- USUWANIE MARTWYCH WPISÓW ŻETONÓW Z CAŁEJ MAPY ---
        for hex_id, terrain in list(self.hex_data.items()):
            token = terrain.get("token")
            if token and "image" in token:
                img_path = ASSET_ROOT / token["image"]
                if not img_path.exists():
                    terrain.pop("token", None)

        # Zapisanie zmian i odświeżenie mapy
        self.save_data()
        self.draw_grid()
        # Automatyczna aktualizacja pliku start_tokens.json po usunięciu żetonu
        self.export_start_tokens()
        messagebox.showinfo("Sukces", f"Dane dla heksu {self.selected_hex} zostały zresetowane.")

    def do_pan(self, event):
        'Przesuwa mapę myszką.'
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def start_pan(self, event):
        'Rozpoczyna przesuwanie mapy myszką.'
        self.canvas.scan_mark(event.x, event.y)

    def on_close(self):
        'Obsługuje zamknięcie aplikacji - daje możliwość zapisu mapy.'
        answer = messagebox.askyesno("Zamykanie programu", "Czy chcesz zapisać dane mapy przed zamknięciem?")
        if answer:
            self.save_map_and_data()
        self.root.destroy()

    def print_extreme_hexes(self):
        'Wypisuje w konsoli współrzędne skrajnych heksów (debug).'
        if not self.hex_centers:
            print("Brak heksów do analizy.")
            return
        xs = [coord[0] for coord in self.hex_centers.values()]
        ys = [coord[1] for coord in self.hex_centers.values()]
        print("Skrajne heksy:")
        print("Lewy skrajny (x) =", min(xs))
        print("Prawy skrajny (x) =", max(xs))
        print("Górny skrajny (y) =", min(ys))
        print("Dolny skrajny (y) =", max(ys))

    def get_working_data_path(self):
        # Zawsze zwracaj ścieżkę do data/map_data.json
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / "map_data.json")

    def load_tokens_from_folders(self, folders):
        """Wczytuje listę żetonów z podanych folderów (zgodnie z nową strukturą: token.json + token.png)."""
        tokens = []
        for folder in folders:
            if os.path.exists(folder):
                for subfolder in os.listdir(folder):
                    token_folder = os.path.join(folder, subfolder)
                    if os.path.isdir(token_folder):
                        json_path = os.path.join(token_folder, "token.json")   # poprawka: nowa nazwa pliku
                        png_path = os.path.join(token_folder, "token.png")     # poprawka: nowa nazwa pliku
                        if os.path.exists(json_path) and os.path.exists(png_path):
                            tokens.append({
                                "name": subfolder,
                                "json_path": json_path,
                                "image_path": png_path
                            })
        return tokens

    def deploy_token_dialog(self):
        """Wyświetla okno dialogowe z wszystkimi dostępnymi żetonami - KLIK żetonu go zaznacza, potem KLIK na mapie go umieszcza."""
        if self.token_selection_window and self.token_selection_window.winfo_exists():
            self.token_selection_window.lift()  # Przenieś na wierzch jeśli już istnieje
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Wybierz żeton do umieszczenia")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        # NIE używamy grab_set() żeby móc klikać na mapę
        
        self.token_selection_window = dialog  # Zapisz referencję
        
        # Instrukcja użytkowania
        tk.Label(dialog, text="1. Kliknij żeton żeby go zaznaczyć\n2. Kliknij na mapie żeby go umieścić", 
                 bg="lightyellow", font=("Arial", 10, "bold")).pack(pady=10, fill=tk.X)
        
        # Status wybranego żetonu
        self.selected_token_label = tk.Label(dialog, text="Wybrany żeton: brak", 
                                           bg="lightgray", font=("Arial", 10))
        self.selected_token_label.pack(pady=5, fill=tk.X)
        
        # Ramka przewijana dla żetonów
        frame_container = tk.Frame(dialog, bg="darkolivegreen")
        frame_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(frame_container, bg="darkolivegreen")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_y = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        frame = tk.Frame(canvas, bg="darkolivegreen")
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        
        # Wczytaj żetony z folderów
        token_base = str(ASSET_ROOT / "tokens")
        token_folders = [os.path.join(token_base, d)
                         for d in os.listdir(token_base)
                         if os.path.isdir(os.path.join(token_base, d))]
        tokens = self.load_tokens_from_folders(token_folders)
        
        # POKAŻ wszystkie żetony (nie filtruj już użytych)
        available_tokens = tokens
        
        # Wyświetlanie żetonów w siatce
        self.token_buttons = {}  # Resetuj referencje do przycisków
        
        row = 0
        col = 0
        max_cols = 3  # 3 żetony na rząd
        
        for token in available_tokens:
            if os.path.exists(token["image_path"]):
                img = Image.open(token["image_path"]).resize((80, 80))
                img = ImageTk.PhotoImage(img)
                
                # Frame dla każdego żetonu
                token_frame = tk.Frame(frame, bg="saddlebrown", relief=tk.RAISED, bd=2)
                token_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                # Label z obrazkiem
                btn = tk.Label(token_frame, image=img, bg="saddlebrown")
                btn.image = img  # Przechowuj referencję
                btn.pack(pady=2)
                
                # Label z nazwą
                name_label = tk.Label(token_frame, text=token["name"][:15], bg="saddlebrown", 
                                    fg="white", font=("Arial", 8))
                name_label.pack()
                
                # Obsługa kliknięcia - ZAZNACZANIE żetonu
                def on_token_click(selected_token=token):
                    self.selected_token_for_deployment = selected_token
                    self.selected_token_label.config(text=f"Wybrany żeton: {selected_token['name']}")
                    
                    # Podświetl wybrany żeton
                    for other_frame in self.token_buttons.values():
                        other_frame.config(bg="saddlebrown", relief=tk.RAISED)
                    token_frame.config(bg="gold", relief=tk.SUNKEN)
                    
                    print(f"🎯 Zaznaczono żeton: {selected_token['name']}")
                
                btn.bind("<Button-1>", lambda e, t=token: on_token_click(t))
                name_label.bind("<Button-1>", lambda e, t=token: on_token_click(t))
                token_frame.bind("<Button-1>", lambda e, t=token: on_token_click(t))
                
                self.token_buttons[token["name"]] = token_frame
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        # Ustawienie scrollregion
        frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Przyciski kontrolne
        control_frame = tk.Frame(dialog, bg="darkolivegreen")
        control_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(control_frame, text="Anuluj wybór", 
                 command=self.cancel_token_selection,
                 bg="orange", fg="white").pack(side=tk.LEFT, padx=10)
        
        tk.Button(control_frame, text="Zamknij okno", 
                 command=self.close_token_selection_window,
                 bg="red", fg="white").pack(side=tk.RIGHT, padx=10)
        
        # Obsługa zamknięcia okna
        dialog.protocol("WM_DELETE_WINDOW", self.close_token_selection_window)

        # Ustawienie scrollregion po dodaniu widgetów
        frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def cancel_token_selection(self):
        """Anuluje wybór żetonu."""
        self.selected_token_for_deployment = None
        if hasattr(self, 'selected_token_label'):
            self.selected_token_label.config(text="Wybrany żeton: brak")
        
        # Usuń podświetlenie
        if hasattr(self, 'token_buttons'):
            for frame in self.token_buttons.values():
                frame.config(bg="saddlebrown", relief=tk.RAISED)
        
        print("❌ Anulowano wybór żetonu")

    def close_token_selection_window(self):
        """Zamyka okno wyboru żetonów."""
        self.cancel_token_selection()
        if self.token_selection_window and self.token_selection_window.winfo_exists():
            self.token_selection_window.destroy()
        self.token_selection_window = None

    def hide_token_from_list(self, token_name):
        """Ukrywa żeton z listy dostępnych (symuluje usunięcie)."""
        if hasattr(self, 'token_buttons') and token_name in self.token_buttons:
            frame = self.token_buttons[token_name]
            frame.grid_remove()  # Ukryj ale nie zniszcz
            print(f"🚫 Ukryto żeton z listy: {token_name}")

    def restore_token_to_list(self, token_id, token_image_path):
        """Przywraca żeton do listy dostępnych."""
        if hasattr(self, 'token_buttons'):
            # Znajdź żeton po ID i przywróć go
            for token_name, frame in self.token_buttons.items():
                # Sprawdź czy to ten żeton (porównaj ID)
                if token_id in token_name:  # Proste dopasowanie
                    frame.grid()  # Pokaż ponownie
                    print(f"🔄 Przywrócono żeton do listy: {token_name}")
                    break

    def remove_token_from_hex(self, hex_id):
        """Usuwa żeton z heksa i przywraca go do listy dostępnych."""
        terrain = self.hex_data.get(hex_id, {})
        token = terrain.get("token")
        
        if token:
            token_id = token.get("unit")
            token_image = token.get("image", "")
            
            # Usuń żeton z heksa
            del self.hex_data[hex_id]["token"]
            
            # Przywróć do listy dostępnych
            self.restore_token_to_list(token_id, token_image)
            
            # Przerysuj mapę
            self.redraw_map()
            
            print(f"🗑️ Usunięto żeton {token_id} z heksa {hex_id}")
            messagebox.showinfo("Żeton usunięty", f"Żeton przywrócony do listy dostępnych")
        else:
            messagebox.showinfo("Brak żetonu", "Na tym heksie nie ma żetonu do usunięcia")

    def redraw_map(self):
        """Przerysowuje całą mapę - używane po dodaniu/usunięciu żetonów."""
        self.draw_grid()
        # Dodatkowe czynności po przerysowaniu mapy, jeśli potrzebne

        print("🖼️ Przerysowano mapę")

    def _get_token_id_from_json(self, json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                token_json = json.load(f)
            return token_json.get("id")
        except Exception:
            return None

    def place_token_on_hex(self, token, hex_id):
        """Umieszcza żeton na heksie i USUWA go z listy dostępnych żetonów."""
        print(f"🎯 Umieszczam żeton {token['name']} na heksie {hex_id}")
        
        # Sprawdź czy na tym heksie już jest żeton
        current_terrain = self.hex_data.get(hex_id, {})
        old_token = current_terrain.get("token")
        
        # Jeśli był stary żeton, PRZYWRÓĆ go do listy dostępnych
        if old_token:
            old_token_id = old_token.get("unit")
            if old_token_id:
                # Znajdź token w available_tokens i przywróć go
                self.restore_token_to_list(old_token_id, old_token.get("image", ""))
                print(f"🔄 Przywrócono stary żeton: {old_token_id}")
        
        # Jeśli wpisu brak – utwórz z domyślnym terenem
        if hex_id not in self.hex_data:
            self.hex_data[hex_id] = {
                "terrain_key": "płaski",
                "move_mod": 0,
                "defense_mod": 0
            }

        # Wczytaj prawdziwe ID żetonu z token.json
        try:
            with open(token["json_path"], "r", encoding="utf-8") as f:
                token_json = json.load(f)
            token_id = token_json["id"]
        except Exception:
            token_id = Path(token["json_path"]).stem

        rel_path = to_rel(token["image_path"]).replace("\\", "/")
        self.hex_data[hex_id]["token"] = {
            "unit": token_id,
            "image": rel_path
        }
        
        # USUŃ żeton z okna wyboru (ukryj przycisk)
        self.hide_token_from_list(token["name"])

        self.redraw_map()   # odśwież mapę
        print(f"✅ Żeton {token['name']} umieszczony i usunięty z listy")

    def toggle_brush(self, key):
        if self.current_brush == key:           # drugi klik → wyłącz
            self.terrain_buttons[key].config(relief="raised")
            self.current_brush = None
            return
        # przełącz pędzel
        for k,b in self.terrain_buttons.items():
            b.config(relief="raised")
        self.terrain_buttons[key].config(relief="sunken")
        self.current_brush = key

    def paint_hex(self, clicked_hex, terrain_key):
        'Maluje heks wybranym typem terenu.'
        q, r = clicked_hex
        hex_id = f"{q},{r}"
        terrain = TERRAIN_TYPES.get(terrain_key)
        if terrain:
            if (terrain.get('move_mod', 0) == self.hex_defaults.get('move_mod', 0) and
                terrain.get('defense_mod', 0) == self.hex_defaults.get('defense_mod', 0)):
                if hex_id in self.hex_data:
                    del self.hex_data[hex_id]
            else:
                self.hex_data[hex_id] = {
                    "terrain_key": terrain_key,
                    "move_mod": terrain["move_mod"],
                    "defense_mod": terrain["defense_mod"]
                }
            self.save_data()
            cx, cy = self.hex_centers[hex_id]
            self.draw_hex(hex_id, cx, cy, self.hex_size, terrain)
        else:
            messagebox.showerror("Błąd", "Niepoprawny rodzaj terenu.")

    def export_start_tokens(self, path=None):
        """Eksportuje rozmieszczenie wszystkich żetonów na mapie do assets/start_tokens.json."""
        if path is None:
            path = str(ASSET_ROOT / "start_tokens.json")
        tokens = []
        for hex_id, terrain in self.hex_data.items():
            token = terrain.get("token")
            if token and "unit" in token:
                try:
                    q, r = map(int, hex_id.split(","))
                except Exception:
                    continue
                tokens.append({
                    "id": token["unit"],
                    "q": q,
                    "r": r
                })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Sukces", f"Wyeksportowano rozmieszczenie żetonów do:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Edytor Mapy 3v3")
    root.geometry("1024x768")
    editor = MapEditor(root, CONFIG)
    root.protocol("WM_DELETE_WINDOW", editor.on_close)
    root.mainloop()
