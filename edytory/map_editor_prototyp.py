import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import math
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ----------------------------
# Konfiguracja rodzajów terenu
# ----------------------------
TERRAIN_TYPES = {
    "teren_płaski": {"move_mod": 0, "defense_mod": 0},
    "mała rzeka": {"move_mod": -2, "defense_mod": 1},
    "duża rzeka": {"move_mod": -4, "defense_mod": -1},
    "las": {"move_mod": -2, "defense_mod": 2},
    "bagno": {"move_mod": -3, "defense_mod": 1},
    "mała miejscowość": {"move_mod": -2, "defense_mod": 2},
    "miasto": {"move_mod": -2, "defense_mod": 2},
    "most": {"move_mod": 0, "defense_mod": 0}
}

# Używamy oddzielnego pliku do zapisu danych (roboczy plik)
DEFAULT_MAP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa_cyfrowa")
DATA_FILENAME_WORKING = os.path.join(DEFAULT_MAP_DIR, "mapa_dane.json")

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
    'Zwraca wierzchołki heksagonu (flat-topped).'
    return [
        (center_x - s, center_y),
        (center_x - s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s, center_y),
        (center_x + s/2, center_y + (math.sqrt(3)/2)*s),
        (center_x - s/2, center_y + (math.sqrt(3)/2)*s)
    ]

# Ścieżki docelowe w folderze mapa_cyfrowa
DEST_FOLDER = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa"
DEST_GLOBAL_MAP = f"{DEST_FOLDER}/mapa_globalna.jpg"
DEST_COMMANDER1_MAP = f"{DEST_FOLDER}/mapa_dowodca1.jpg"
DEST_COMMANDER2_MAP = f"{DEST_FOLDER}/mapa_dowodca2.jpg"
DEST_DATA_FILE = f"{DEST_FOLDER}/mapa_dane.json"

class MapEditor:
    def __init__(self, root, config):
        self.root = root
        self.root.configure(bg="darkolivegreen")
        self.config = config["map_settings"]
        self.map_image_path = self.get_last_modified_map()  # Automatyczne otwieranie ostatniej mapy
        
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

        # Zbuduj GUI
        self.build_gui()
        # Wczytaj mapę i dane
        self.load_map_image()
        self.load_data()

    def get_last_modified_map(self):
        """Zwraca ścieżkę do ostatnio zmodyfikowanej mapy lub domyślną mapę."""
        if os.path.exists(DEST_GLOBAL_MAP):
            return DEST_GLOBAL_MAP
        else:
            messagebox.showinfo("Informacja", "Nie znaleziono ostatniej mapy. Wybierz nową mapę.")
            return filedialog.askopenfilename(
                title="Wybierz mapę",
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

        # Przycisk "Zapisz Mapę + Dane"
        self.save_map_and_data_button = tk.Button(
            buttons_frame, text="Zapisz Mapę + Dane", command=self.save_map_and_data,
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
        for terrain_name in TERRAIN_TYPES.keys():
            display_name = terrain_name.replace("_", " ")
            btn = tk.Button(terrain_frame, text=display_name,
                            command=lambda t=terrain_name: self.apply_terrain(t),
                            bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
            btn.pack(padx=5, pady=2, fill=tk.X)

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

        # Pole rysowania mapy z przewijaniem
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", cursor="cross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dodanie suwaków przewijania
        # self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        # self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
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
            messagebox.showerror("Błąd", f"Nie udało się załadować mapy:\n{str(e)}")
            return
        self.world_width, self.world_height = self.bg_image.size
        self.photo_bg = ImageTk.PhotoImage(self.bg_image)
        # Ustaw obszar przewijania
        self.canvas.config(scrollregion=(0, 0, self.world_width, self.world_height))
        # Rysuj ponownie siatkę
        self.draw_grid()

    def draw_grid(self):
        'Rysuje siatkę heksów i aktualizuje wyświetlane heksy.'
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
        self.hex_centers = {}
        s = self.hex_size
        hex_height = math.sqrt(3) * s
        horizontal_spacing = 1.5 * s
        grid_cols = self.config.get("grid_cols")
        grid_rows = self.config.get("grid_rows")
        for col in range(grid_cols):
            center_x = s + col * horizontal_spacing
            for row in range(grid_rows):
                center_y = (s * math.sqrt(3) / 2) + row * hex_height
                if col % 2 == 1:
                    center_y += hex_height / 2
                if center_x + s > self.world_width or center_y + (s * math.sqrt(3) / 2) > self.world_height:
                    continue
                hex_id = f"{col}_{row}"
                self.hex_centers[hex_id] = (center_x, center_y)
                terrain = self.hex_data.get(hex_id, self.hex_defaults)
                self.draw_hex(hex_id, center_x, center_y, s, terrain)
        # Nakładanie mgiełki (półprzezroczystej) na punkty wystawienia
        for nation, hexes in self.spawn_points.items():
            for hex_id in hexes:
                if hex_id in self.hex_centers:
                    cx, cy = self.hex_centers[hex_id]
                    vertices = get_hex_vertices(cx, cy, s)
                    self.canvas.create_polygon(vertices, outline="", fill="gray", stipple="gray50", tags=f"spawn_{hex_id}")
        # Rysowanie kluczowych punktów na mapie
        for hex_id, key_point in self.key_points.items():
            self.draw_key_point(hex_id, key_point['type'], key_point['value'])
        # Podświetlenie wybranego heksu
        if self.selected_hex is not None:
            self.highlight_hex(self.selected_hex)
        # Wypisanie skrajnych heksów w konsoli (debug)
        self.print_extreme_hexes()

    def draw_hex(self, hex_id, center_x, center_y, s, terrain=None):
        'Rysuje pojedynczy heksagon na canvasie wraz z tekstem modyfikatorów.'
        points = get_hex_vertices(center_x, center_y, s)
        self.canvas.create_polygon(points, outline="red", fill="", width=2, tags=hex_id)
        if terrain:
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            tekst = f"M:{move_mod} D:{defense_mod}"
        else:
            move_mod = self.hex_defaults.get('move_mod', 0)
            defense_mod = self.hex_defaults.get('defense_mod', 0)
            tekst = f"M:{move_mod} D:{defense_mod}"
        self.canvas.delete(f"tekst_{hex_id}")
        self.canvas.create_text(center_x, center_y, text=tekst, fill="blue",
                                font=("Arial", 10), anchor="center", tags=f"tekst_{hex_id}")

    def on_canvas_click(self, event):
        'Obsługuje kliknięcie myszką na canvasie - zaznacza heks i wyświetla jego dane.'
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_hex = None
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                clicked_hex = hex_id
                break
        if clicked_hex:
            self.selected_hex = clicked_hex
            self.highlight_hex(clicked_hex)
            terrain = self.hex_data.get(clicked_hex, self.hex_defaults)
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            messagebox.showinfo("Informacja o heksie",
                                f"Heks: {clicked_hex}\nModyfikator ruchu: {move_mod}\nModyfikator obrony: {defense_mod}")
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
        'Wyświetla informacje o heksie przy najechaniu myszką.'
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        hovered_hex = None
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                hovered_hex = hex_id
                break
        if hovered_hex:
            terrain = self.hex_data.get(hovered_hex, self.hex_defaults)
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            key_point = self.key_points.get(hovered_hex, None)
            spawn_nations = [n for n, hexes in self.spawn_points.items() if hovered_hex in hexes]
            self.hex_info_label.config(text=f"Heks: {hovered_hex}")
            self.terrain_info_label.config(text=f"Teren: {terrain}")
            self.modifiers_info_label.config(text=f"Modyfikatory: Ruch: {move_mod}, Obrona: {defense_mod}")
            if key_point:
                self.key_point_info_label.config(text=f"Kluczowy punkt: {key_point['type']} ({key_point['value']})")
            else:
                self.key_point_info_label.config(text="Kluczowy punkt: brak")
            if spawn_nations:
                self.spawn_info_label.config(text=f"Punkt wystawiania: {', '.join(spawn_nations)}")
            else:
                self.spawn_info_label.config(text="Punkt wystawiania: brak")
        else:
            self.hex_info_label.config(text="Heks: brak")
            self.terrain_info_label.config(text="Teren: brak")
            self.modifiers_info_label.config(text="Modyfikatory: brak")
            self.key_point_info_label.config(text="Kluczowy punkt: brak")
            self.spawn_info_label.config(text="Punkt wystawiania: brak")

    def save_data(self):
        'Zapisuje aktualne dane (teren, kluczowe punkty, spawn_points) do pliku JSON.'
        optimized_data = {}
        for hex_id, terrain in self.hex_data.items():
            if (terrain.get('move_mod', 0) != self.hex_defaults.get('move_mod', 0) or
                terrain.get('defense_mod', 0) != self.hex_defaults.get('defense_mod', 0)):
                optimized_data[hex_id] = terrain
        map_data = {
            "terrain": optimized_data,
            "key_points": self.key_points,
            "spawn_points": self.spawn_points
        }
        self.current_working_file = self.get_working_data_path()
        print(f"Zapisywanie danych do: {self.current_working_file}")
        zapisz_dane_hex(map_data, self.current_working_file)
        messagebox.showinfo("Zapisano", f"Dane mapy zostały zapisane w:\n{self.current_working_file}\n"
                                        f"Liczba kluczowych punktów: {len(self.key_points)}\n"
                                        f"Liczba punktów wystawienia: {sum(len(v) for v in self.spawn_points.values())}")

    def load_data(self):
        'Wczytuje dane z pliku roboczego (teren, kluczowe i spawn).'
        self.current_working_file = self.get_working_data_path()
        print(f"Wczytywanie danych z: {self.current_working_file}")
        loaded_data = wczytaj_dane_hex(self.current_working_file)
        if loaded_data:
            self.hex_data = loaded_data.get("terrain", {})
            self.key_points = loaded_data.get("key_points", {})
            self.spawn_points = loaded_data.get("spawn_points", {})
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

    def save_files(self):
        """Zapisuje pliki map i dane JSON do folderu mapa_cyfrowa."""
        # Tworzenie folderu, jeśli nie istnieje
        os.makedirs(DEST_FOLDER, exist_ok=True)

        try:
            # Zapisanie mapy globalnej
            self.bg_image.save(DEST_GLOBAL_MAP)
            print(f"[INFO] Zapisano mapę globalną: {DEST_GLOBAL_MAP}")

            # Zapisanie map dowódców (przykład: podział na pół mapy)
            mid_pixel = self.world_height // 2
            img_top = self.bg_image.crop((0, 0, self.world_width, mid_pixel))
            img_bottom = self.bg_image.crop((0, mid_pixel, self.world_width, self.world_height))
            img_top.save(DEST_COMMANDER1_MAP)
            img_bottom.save(DEST_COMMANDER2_MAP)
            print(f"[INFO] Zapisano mapy dowódców: {DEST_COMMANDER1_MAP}, {DEST_COMMANDER2_MAP}")

            # Zapisanie danych JSON
            map_data = {
                "terrain": self.hex_data,
                "key_points": self.key_points,
                "spawn_points": self.spawn_points
            }
            with open(DEST_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(map_data, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Zapisano dane mapy: {DEST_DATA_FILE}")

        except Exception as e:
            print(f"[ERROR] Nie udało się zapisać plików: {e}")

    def save_map_as_image(self):
        """Zapisuje obrazy mapy i dane JSON."""
        try:
            # Zapisz mapę globalną i dane
            self.save_files()
            print("[INFO] Mapa i dane zostały zapisane w folderze mapa_cyfrowa.")
        except Exception as e:
            print(f"[ERROR] Nie udało się zapisać mapy: {e}")

    def save_map_and_data(self):
        """Zapisuje zarówno obraz mapy, jak i dane JSON."""
        try:
            self.save_files()  # Zapisuje mapy i dane
            messagebox.showinfo("Sukces", "Mapa i dane zostały zapisane pomyślnie.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać mapy i danych: {e}")

    def open_map_and_data(self):
        """Otwiera mapę i wczytuje dane."""
        try:
            # Domyślna ścieżka do mapy
            map_path = filedialog.askopenfilename(
                initialdir=DEST_FOLDER,
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
                # W przeciwnym razie, dodaj/zaktualizuj wpis
                self.hex_data[self.selected_hex] = terrain.copy()
            # Zapisz dane i odrysuj heks
            self.save_data()
            cx, cy = self.hex_centers[self.selected_hex]
            self.draw_hex(self.selected_hex, cx, cy, self.hex_size, terrain)
            messagebox.showinfo("Zapisano", f"Dla heksu {self.selected_hex} ustawiono teren: {terrain_key}")
        else:
            messagebox.showerror("Błąd", "Niepoprawny rodzaj terenu.")

    def reset_selected_hex(self):
        """Czyści wszystkie dane przypisane do wybranego heksu."""
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return

        # Usuwanie danych przypisanych do heksu
        self.hex_data.pop(self.selected_hex, None)
        self.key_points.pop(self.selected_hex, None)
        for nation, hexes in self.spawn_points.items():
            if self.selected_hex in hexes:
                hexes.remove(self.selected_hex)

        # Zapisanie zmian i odświeżenie mapy
        self.save_data()
        self.draw_grid()
        messagebox.showinfo("Sukces", f"Dane dla heksu {self.selected_hex} zostały zresetowane.")

    def do_pan(self, event):
        'Przesuwa mapę myszką.'
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def start_pan(self, event):
        'Rozpoczyna przesuwanie mapy myszką.'
        self.canvas.scan_mark(event.x, event.y)

    def on_close(self):
        'Obsługuje zamknięcie aplikacji - daje możliwość zapisu mapy.'
        answer = messagebox.askyesno("Zamykanie programu", "Czy chcesz zapisać mapę przed zamknięciem?")
        if answer:
            self.save_map_as_image()
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
        'Zwraca ścieżkę do pliku roboczego w folderze mapa_cyfrowa.'
        map_folder = DEFAULT_MAP_DIR
        if not os.path.exists(map_folder):
            try:
                os.makedirs(map_folder)
                print(f"Utworzono folder docelowy: {map_folder}")
            except Exception as e:
                print(f"Nie można utworzyć folderu mapa_cyfrowa: {e}")
                return os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa_dane.json")
        if os.access(map_folder, os.W_OK):
            return os.path.join(map_folder, "mapa_dane.json")
        else:
            print(f"Brak uprawnień do zapisu w folderze {map_folder}")
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa_dane.json")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Edytor Mapy 3v3")
    root.geometry("1024x768")
    editor = MapEditor(root, CONFIG)
    root.protocol("WM_DELETE_WINDOW", editor.on_close)
    root.mainloop()
