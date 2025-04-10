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
DATA_FILENAME_WORKING = os.path.join(DEFAULT_MAP_DIR, "dane_terenow_hexow_working.json")

def zapisz_dane_hex(hex_data, filename=DATA_FILENAME_WORKING):
    # Sprawdź czy katalog istnieje, jeśli nie - stwórz go
    directory = os.path.dirname(filename)
    if (directory and not os.path.exists(directory)):
        try:
            os.makedirs(directory)
        except Exception as e:
            print(f"Nie można utworzyć katalogu {directory}: {e}")
            # Jeśli nie można utworzyć katalogu, użyj katalogu skryptu
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(filename))
            
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(hex_data, f, indent=2, ensure_ascii=False)

def wczytaj_dane_hex(filename=DATA_FILENAME_WORKING):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Funkcja do sprawdzania czy plik istnieje
def plik_istnieje(sciezka):
    exists = os.path.isfile(sciezka) if sciezka else False
    print(f"Sprawdzanie ścieżki: {sciezka} -> {exists}")
    return exists

# Funkcja do znalezienia pierwszego pliku obrazu w folderze
def znajdz_plik_obrazu(folder):
    if not os.path.exists(folder):
        return None
    
    obraz_rozszerzenia = ['.jpg', '.jpeg', '.png', '.bmp']
    for plik in os.listdir(folder):
        if any(plik.lower().endswith(ext) for ext in obraz_rozszerzenia):
            return os.path.join(folder, plik)
    return None

# ----------------------------
# Konfiguracja mapy
# ----------------------------
CONFIG = {
    'map_settings': {
        'map_image_path': r"C:\Users\klif\OneDrive\Pulpit\rzeczy do bzura 1939\mapa_wszystko_co_potrzebne\mapa_obraz_pierwotny\Bzura-1939-mapa-bitwy.jpg",  # Pełna ścieżka do tła mapy
        'hex_size': 30,
        'grid_cols': 56,   # liczba kolumn heksów
        'grid_rows': 40    # liczba wierszy heksów
    }
}

# ----------------------------
# Funkcja pomocnicza: punkt w wielokącie (ray-casting)
# ----------------------------
def point_in_polygon(x, y, poly):
    """Zwraca True, jeśli punkt (x, y) leży wewnątrz wielokąta poly (lista krotek (x, y))."""
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
    """Zwraca listę wierzchołków heksagonu (flat-topped)."""
    return [
        (center_x - s, center_y),
        (center_x - s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s, center_y),
        (center_x + s/2, center_y + (math.sqrt(3)/2)*s),
        (center_x - s/2, center_y + (math.sqrt(3)/2)*s)
    ]

# ----------------------------
# Klasa interaktywnego edytora mapy
# ----------------------------
class MapEditor:
    def __init__(self, root, config):
        self.root = root
        self.root.configure(bg="darkolivegreen")  # Ustawienie koloru tła głównego okna
        
        self.config = config["map_settings"]
        self.map_image_path = self.config.get("map_image_path")
        
        # Zapytaj użytkownika o nową domyślną ścieżkę mapy
        answer = messagebox.askyesno("Domyślna mapa", "Czy chcesz wybrać nową domyślną mapę?")
        if answer:
            self.select_default_map_path()
        
        self.hex_size = self.config.get("hex_size", 30)
        
        # Wartości domyślne dla heksów
        self.hex_defaults = {"defense_mod": 0, "move_mod": 0}
        
        print(f"Inicjalizacja edytora mapy. Ścieżka do mapy: {self.map_image_path}")
        
        # Dodajemy nową zmienną do przechowywania aktualnej ścieżki pliku roboczego
        self.current_working_file = DATA_FILENAME_WORKING
        
        # Dodanie zmiennej do przechowywania kluczowych punktów
        self.key_points = {}  # klucz: "kolumna_wiersz" -> {"type": "most", "value": 100}

        # Lista dostępnych typów punktów i ich wartości
        self.available_key_point_types = {
            "most": 50,
            "miasto": 100,
            "węzeł komunikacyjny": 75,
            "fortyfikacja": 150
        }

        # Sprawdź, czy plik mapy istnieje
        try:
            if not os.path.isfile(self.map_image_path):
                print(f"Plik mapy nie istnieje: {self.map_image_path}")
                
                # Wyświetl dodatkowe informacje o folderze
                folder = os.path.dirname(self.map_image_path)
                if os.path.exists(folder):
                    print(f"Folder istnieje: {folder}")
                    print(f"Zawartość folderu:")
                    for f in os.listdir(folder):
                        print(f"  - {f}")
                    
                    # Spróbuj znaleźć jakikolwiek plik obrazu w folderze
                    plik_obrazu = znajdz_plik_obrazu(folder)
                    if plik_obrazu:
                        print(f"Znaleziono plik obrazu: {plik_obrazu}")
                        self.map_image_path = plik_obrazu
                        self.config["map_image_path"] = plik_obrazu
                        
                        # Wczytanie obrazu tła
                        self.bg_image = Image.open(self.map_image_path).convert("RGB")
                        self.world_width, self.world_height = self.bg_image.size
                        self.photo_bg = ImageTk.PhotoImage(self.bg_image)
                        print(f"Automatycznie załadowano mapę: {self.world_width}x{self.world_height}")
                        
                        # Kontynuuj inicjalizację
                        self.create_interface()
                        return
                else:
                    print(f"Folder nie istnieje: {folder}")
                
                messagebox.showwarning("Ostrzeżenie", 
                    f"Nie znaleziono pliku mapy:\n{self.map_image_path}\n\nWybierz plik mapy.")
                self.load_map_image()
                # Jeśli użytkownik anulował wybór pliku, użyj pustego obrazu
                if not os.path.isfile(self.map_image_path):
                    messagebox.showinfo("Informacja", "Tworzenie pustej mapy.")
                    # Stwórz pusty obraz jako tło
                    self.bg_image = Image.new("RGB", (800, 600), "white")
                    self.world_width, self.world_height = self.bg_image.size
                    self.photo_bg = ImageTk.PhotoImage(self.bg_image)
                else:
                    # Wczytanie obrazu tła
                    self.bg_image = Image.open(self.map_image_path).convert("RGB")
                    self.world_width, self.world_height = self.bg_image.size
                    self.photo_bg = ImageTk.PhotoImage(self.bg_image)
            else:
                print(f"Plik mapy istnieje, ładowanie...")
                # Wczytanie obrazu tła
                self.bg_image = Image.open(self.map_image_path).convert("RGB")
                self.world_width, self.world_height = self.bg_image.size
                self.photo_bg = ImageTk.PhotoImage(self.bg_image)
                print(f"Mapa załadowana: {self.world_width}x{self.world_height}")
        except Exception as e:
            print(f"Błąd podczas sprawdzania/wczytywania mapy: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas wczytywania mapy:\n{str(e)}")
            self.load_map_image()
            if not os.path.isfile(self.map_image_path):
                self.bg_image = Image.new("RGB", (800, 600), "white")
                self.world_width, self.world_height = self.bg_image.size
                self.photo_bg = ImageTk.PhotoImage(self.bg_image)
            else:
                self.bg_image = Image.open(self.map_image_path).convert("RGB")
                self.world_width, self.world_height = self.bg_image.size
                self.photo_bg = ImageTk.PhotoImage(self.bg_image)
        
        self.create_interface()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def select_default_map_path(self):
        """Pozwala użytkownikowi wybrać domyślną ścieżkę do pliku mapy."""
        file_path = filedialog.askopenfilename(
            title="Wybierz domyślną mapę",
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp"), ("Wszystkie pliki", "*.*")]
        )
        if file_path:
            self.map_image_path = file_path
            self.config["map_image_path"] = file_path
            messagebox.showinfo("Sukces", f"Zaktualizowano domyślną ścieżkę mapy:\n{file_path}")
        else:
            messagebox.showinfo("Informacja", "Nie wybrano nowej domyślnej mapy. Używana będzie poprzednia ścieżka.")

    def create_interface(self):
        # Dane terenu – domyślnie puste, później uzupełniane domyślnym terenem płaskim
        self.hex_data = wczytaj_dane_hex()
        self.hex_centers = {}  # klucz: "kolumna_wiersz" -> (center_x, center_y)
        
        # Aktualnie wybrany heks
        self.selected_hex = None
        
        # Główna ramka interfejsu
        self.main_frame = tk.Frame(self.root, bg="darkolivegreen")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEWY PANEL – Canvas z scrollbarami i panningiem
        self.canvas_frame = tk.Frame(self.main_frame, bg="darkolivegreen")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.vbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800, height=600,
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, self.world_width, self.world_height)
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.hbar.config(command=self.canvas.xview)
        self.vbar.config(command=self.canvas.yview)
        
        # Wyświetlenie tła mapy
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
        
        # Bindings – obsługa kliknięć i panningu
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        
        # PRAWY PANEL – przyciski wyboru terenu i operacji na danych
        self.panel_frame = tk.Frame(self.main_frame, bg="darkolivegreen")
        self.panel_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Nagłówek
        header_frame = tk.Frame(self.panel_frame, bg="olivedrab", bd=5, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text="Edytor Mapy Heksagonalnej",
                               bg="olivedrab", fg="white", font=("Arial", 14, "bold"))
        header_label.pack(pady=5)
        
        # Usunąłem stąd przycisk "Otwórz mapę", który zostanie przeniesiony do sekcji "Operacje"
        
        # Przyciski terenów
        terrain_frame = tk.LabelFrame(self.panel_frame, text="Rodzaje terenu", bg="darkolivegreen", fg="white",
                                      font=("Arial", 10, "bold"))
        terrain_frame.pack(fill=tk.X, padx=5, pady=5)

        for terrain_name in TERRAIN_TYPES.keys():
            if terrain_name in ["teren_płaski", "las", "mała rzeka"]:
                btn = tk.Button(terrain_frame, text=terrain_name,
                                command=lambda t=terrain_name: self.apply_terrain(t),
                                bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
            else:
                btn = tk.Button(terrain_frame, text=terrain_name, state=tk.DISABLED,
                                bg="gray", fg="white", disabledforeground="lightgray")
            btn.pack(padx=5, pady=2, fill=tk.X)
        
        # Dodatkowe przyciski
        buttons_frame = tk.LabelFrame(self.panel_frame, text="Operacje", bg="darkolivegreen", fg="white",
                                      font=("Arial", 10, "bold"))
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        # Przycisk "Zapisz Mapę" – aktywny
        self.save_map_button = tk.Button(buttons_frame, text="Zapisz Mapę", command=self.save_map_as_image,
                                         bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
        self.save_map_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Otwórz Mapę" – aktywny
        self.load_map_button = tk.Button(buttons_frame, text="Otwórz Mapę", command=self.load_map_image,
                                         bg="saddlebrown", fg="white", activebackground="saddlebrown", activeforeground="white")
        self.load_map_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Zapisz dane" – nieaktywny
        self.save_button = tk.Button(buttons_frame, text="Zapisz dane", state=tk.DISABLED,
                                     bg="gray", fg="white", disabledforeground="lightgray")
        self.save_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Wczytaj dane" – nieaktywny
        self.load_button = tk.Button(buttons_frame, text="Wczytaj dane", state=tk.DISABLED,
                                     bg="gray", fg="white", disabledforeground="lightgray")
        self.load_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Reset dane" – nieaktywny
        self.clear_button = tk.Button(buttons_frame, text="Reset dane", state=tk.DISABLED,
                                      bg="gray", fg="white", disabledforeground="lightgray")
        self.clear_button.pack(padx=5, pady=5, fill=tk.X)

        # Przycisk "Dodaj kluczowy punkt" – nieaktywny
        self.add_key_point_button = tk.Button(buttons_frame, text="Dodaj kluczowy punkt", 
                                              command=self.add_key_point_dialog,
                                              state=tk.DISABLED,  # Ustawienie na nieaktywny
                                              bg="gray", fg="white", disabledforeground="lightgray")
        self.add_key_point_button.pack(padx=5, pady=5, fill=tk.X)

        # Dodanie sekcji kontrolnej w dolnym prawym rogu z przewijaniem
        self.control_panel_frame = tk.Frame(self.panel_frame, bg="darkolivegreen", relief=tk.RIDGE, bd=5)
        self.control_panel_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Canvas do przewijania
        self.control_canvas = tk.Canvas(self.control_panel_frame, bg="darkolivegreen", highlightthickness=0)
        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Suwak pionowy
        self.control_scrollbar = tk.Scrollbar(self.control_panel_frame, orient=tk.VERTICAL, command=self.control_canvas.yview)
        self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Konfiguracja przewijania
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)
        self.control_canvas.bind('<Configure>', lambda e: self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all")))

        # Ramka wewnętrzna do wyświetlania informacji
        self.control_content = tk.Frame(self.control_canvas, bg="darkolivegreen")
        self.control_canvas.create_window((0, 0), window=self.control_content, anchor="nw")

        # Nagłówek tabelki kontrolnej
        tk.Label(self.control_content, text="Informacje o heksie", bg="darkolivegreen", fg="white",
                 font=("Arial", 10, "bold")).pack()

        # Dodanie pól do wyświetlania danych
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

        # Dodanie obsługi zdarzenia Motion
        self.canvas.bind("<Motion>", self.on_canvas_hover)

        self.draw_grid()
    
    def draw_grid(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
        self.hex_centers.clear()
        
        s = self.hex_size
        hex_height = math.sqrt(3) * s
        horizontal_spacing = 1.5 * s
        
        grid_cols = self.config.get("grid_cols")
        grid_rows = self.config.get("grid_rows")
        
        # Rysujemy heksy – jeśli dla danego heksu nie ma przypisanego terenu, ustawiamy domyślne wartości
        for col in range(grid_cols):
            center_x = s + col * horizontal_spacing
            for row in range(grid_rows):
                center_y = (s * math.sqrt(3) / 2) + row * hex_height
                if col % 2 == 1:
                    center_y += hex_height / 2
                # Pomijamy heksy wychodzące poza tło
                if center_x + s > self.world_width or center_y + (s * math.sqrt(3) / 2) > self.world_height:
                    continue
                hex_id = f"{col}_{row}"
                self.hex_centers[hex_id] = (center_x, center_y)
                # Użyj domyślnych wartości, jeśli heks nie ma zdefiniowanych własnych
                terrain = self.hex_data.get(hex_id, self.hex_defaults)
                self.draw_hex(hex_id, center_x, center_y, s, terrain)
        
        if self.selected_hex is not None:
            self.highlight_hex(self.selected_hex)
        
        # Wypisanie skrajnych heksów w konsoli – przydatne do weryfikacji generacji mapy
        self.print_extreme_hexes()
    
    def draw_hex(self, hex_id, center_x, center_y, s, terrain=None):
        points = get_hex_vertices(center_x, center_y, s)
        self.canvas.create_polygon(points, outline="red", fill="", width=2, tags=hex_id)
        
        # Dodanie tekstu z wartościami modyfikatorów (nawet jeśli są domyślne)
        if terrain:
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            tekst = f"M:{move_mod} D:{defense_mod}"
        else:
            move_mod = self.hex_defaults.get('move_mod', 0)
            defense_mod = self.hex_defaults.get('defense_mod', 0)
            tekst = f"M:{move_mod} D:{defense_mod}"
            
        # Usunięcie starego tekstu i dodanie nowego
        self.canvas.delete(f"tekst_{hex_id}")
        self.canvas.create_text(center_x, center_y, text=tekst, fill="blue",
                                font=("Arial", 10), anchor="center", tags=f"tekst_{hex_id}")
    
    def on_canvas_click(self, event):
        # Używamy canvasx/canvasy, aby uwzględnić przesunięcie scrolla
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_hex = None
        # Sprawdzamy, czy kliknięty punkt leży wewnątrz któregoś heksagonu
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                clicked_hex = hex_id
                break
        if clicked_hex:
            self.selected_hex = clicked_hex
            self.highlight_hex(clicked_hex)
            
            # Wyświetl info o wybranym heksie
            terrain = self.hex_data.get(clicked_hex, self.hex_defaults)
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            messagebox.showinfo("Informacja o heksie", 
                f"Heks: {clicked_hex}\nModyfikator ruchu: {move_mod}\nModyfikator obrony: {defense_mod}")
        else:
            messagebox.showinfo("Informacja", "Kliknij wewnątrz heksagonu.")
    
    def highlight_hex(self, hex_id):
        self.canvas.delete("highlight")
        if (hex_id in self.hex_centers):
            cx, cy = self.hex_centers[hex_id]
            s = self.hex_size
            self.canvas.create_oval(cx - s, cy - s, cx + s, cy + s,
                                    outline="yellow", width=3, tags="highlight")
    
    def apply_terrain(self, terrain_key):
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return
        terrain = TERRAIN_TYPES.get(terrain_key)
        if terrain:
            # Sprawdź, czy teren jest domyślny
            if (terrain['move_mod'] == self.hex_defaults.get('move_mod', 0) and 
                terrain['defense_mod'] == self.hex_defaults.get('defense_mod', 0)):
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
            messagebox.showinfo("Zapisano", f"Dla heksu {self.selected_hex} ustawiono: {terrain_key}")
        else:
            messagebox.showerror("Błąd", "Niepoprawny rodzaj terenu.")
    
    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)
    
    def do_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    
    def get_working_data_path(self):
        """Zwraca ścieżkę do pliku roboczego w folderze mapa_cyfrowa"""
        # Zawsze używamy folderu mapa_cyfrowa w katalogu głównym aplikacji
        map_folder = DEFAULT_MAP_DIR
        
        # Sprawdź czy folder istnieje i czy mamy uprawnienia do zapisu
        if not os.path.exists(map_folder):
            try:
                os.makedirs(map_folder)
                print(f"Utworzono folder docelowy: {map_folder}")
            except Exception as e:
                print(f"Nie można utworzyć folderu mapa_cyfrowa: {e}")
                # Jeśli nie można utworzyć folderu, użyj katalogu skryptu
                return os.path.join(os.path.dirname(os.path.abspath(__file__)), "dane_terenow_hexow_working.json")
        
        if os.access(map_folder, os.W_OK):
            # Zwróć ścieżkę do pliku roboczego w folderze mapa_cyfrowa
            return os.path.join(map_folder, "dane_terenow_hexow_working.json")
        else:
            print(f"Brak uprawnień do zapisu w folderze {map_folder}")
            # W przypadku problemów, użyj domyślnej lokalizacji
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "dane_terenow_hexow_working.json")
    
    def save_data(self):
        # Zoptymalizowany zapis danych - tylko niestandardowe heksy
        optimized_data = {}
        for hex_id, terrain in self.hex_data.items():
            if (terrain.get('move_mod', 0) != self.hex_defaults.get('move_mod', 0) or 
                terrain.get('defense_mod', 0) != self.hex_defaults.get('defense_mod', 0)):
                optimized_data[hex_id] = terrain
        
        # Dodanie kluczowych punktów do danych
        map_data = {
            "terrain": optimized_data,
            "key_points": self.key_points  # Dodanie kluczowych punktów do zapisu
        }

        # Ustal ścieżkę do pliku danych w folderze mapa_cyfrowa
        self.current_working_file = self.get_working_data_path()
        print(f"Zapisywanie danych do: {self.current_working_file}")
        
        # Zapisz dane używając dynamicznej ścieżki
        zapisz_dane_hex(map_data, self.current_working_file)
        messagebox.showinfo("Zapisano", 
                          f"Dane mapy zostały zapisane w: {self.current_working_file}\n" + 
                          f"Liczba kluczowych punktów: {len(self.key_points)}")
    
    def load_data(self):
        # Ustal ścieżkę do pliku danych w folderze mapy
        self.current_working_file = self.get_working_data_path()
        print(f"Wczytywanie danych z: {self.current_working_file}")
        
        # Wczytaj dane używając dynamicznej ścieżki
        loaded_data = wczytaj_dane_hex(self.current_working_file)
        if loaded_data:
            self.hex_data = loaded_data.get("terrain", {})
            self.key_points = loaded_data.get("key_points", {})
            self.draw_grid()
            messagebox.showinfo("Wczytano", 
                              f"Dane mapy zostały wczytane z: {self.current_working_file}\n" + 
                              f"Liczba kluczowych punktów: {len(self.key_points)}")
        else:
            messagebox.showinfo("Informacja", f"Brak danych do wczytania lub plik {self.current_working_file} nie istnieje.")
    
    def clear_variables(self):
        answer = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zresetować mapę do domyślnego terenu płaskiego?")
        if answer:
            self.hex_data = {}  # Usunięcie wszystkich danych terrenu - będą używane domyślne wartości
            self.key_points = {}  # Usunięcie wszystkich kluczowych punktów
            zapisz_dane_hex({"terrain": self.hex_data, "key_points": self.key_points})
            self.draw_grid()
            messagebox.showinfo("Zresetowano", "Mapa została zresetowana do domyślnego terenu płaskiego.")
    
    def save_map_as_image(self):
        # Wyświetlenie okna dialogowego do wyboru folderu zapisu
        folder_path = filedialog.askdirectory(
            title="Wybierz folder do zapisu mapy"
        )
        
        if not folder_path:
            messagebox.showinfo("Anulowano", "Zapis mapy został anulowany.")
            return

        # Ustawienie domyślnej nazwy pliku
        image_path = os.path.join(folder_path, "mapa_hex.jpg")
        data_path = os.path.join(folder_path, "mapa_dane.json")

        try:
            # Opcja zapisu etykiet na obrazie (zawsze False zgodnie z wymaganiami)
            draw_labels = False  # Etykiety zawsze wyłączone
            
            img = self.bg_image.copy()
            draw = ImageDraw.Draw(img)
            s = self.hex_size
            hex_height = math.sqrt(3) * s
            horizontal_spacing = 1.5 * s
            grid_cols = self.config.get("grid_cols")
            grid_rows = self.config.get("grid_rows")
            
            # Rysowanie heksów na obrazie
            for col in range(grid_cols):
                center_x = s + col * horizontal_spacing
                for row in range(grid_rows):
                    center_y = (s * math.sqrt(3)/2) + row * hex_height
                    if col % 2 == 1:
                        center_y += hex_height / 2
                    if center_x + s > self.world_width or center_y + (s * math.sqrt(3)/2) > self.world_height:
                        continue
                    
                    # Rysowanie obrysu heksu
                    points = get_hex_vertices(center_x, center_y, s)
                    draw.polygon(points, outline="red")
                    
                    hex_id = f"{col}_{row}"
                    
                    # Rysowanie tekstu tylko jeśli opcja draw_labels jest włączona (obecnie zawsze False)
                    if draw_labels:
                        terrain = self.hex_data.get(hex_id, self.hex_defaults)
                        move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
                        defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
                        tekst = f"M:{move_mod} D:{defense_mod}"
                        text_width = 6 * len(tekst)  # Przybliżona szerokość tekstu
                        text_pos = (center_x - text_width/2, center_y - 5)  # Pozycja tekstu
                        draw.text(text_pos, tekst, fill="blue")
            
            # Rysowanie kluczowych punktów na obrazie
            try:
                font = ImageFont.truetype("arial.ttf", 10)
            except IOError:
                font = ImageFont.load_default()

            for hex_id, key_point in self.key_points.items():
                if hex_id in self.hex_centers:
                    cx, cy = self.hex_centers[hex_id]
                    draw.text((cx, cy), f"{key_point['type']}\n({key_point['value']})", fill="yellow", font=font)
            
            # Zapis obrazu
            img.save(image_path)

            # Zapis danych JSON
            map_data = {
                "terrain": self.hex_data,
                "key_points": self.key_points,
                "config": self.config
            }
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(map_data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Zapisano", f"Mapa została zapisana w:\n{image_path}\n{data_path}")
        
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać mapy:\n{str(e)}")
    
    def print_extreme_hexes(self):
        if not self.hex_centers:
            print("Brak heksów do analizy.")
            return
        xs = [coord[0] for coord in self.hex_centers.values()]
        ys = [coord[1] for coord in self.hex_centers.values()]
        leftmost = min(xs)
        rightmost = max(xs)
        topmost = min(ys)
        bottommost = max(ys)
        print("Skrajne heksy:")
        print("Lewy skrajny: (x =", leftmost, ")")
        print("Prawy skrajny: (x =", rightmost, ")")
        print("Górny skrajny: (y =", topmost, ")")
        print("Dolny skrajny: (y =", bottommost, ")")

    def load_map_image(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz plik mapy",
            filetypes=[
                ("Obrazy", "*.jpg *.jpeg *.png *.bmp"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.bg_image = Image.open(file_path).convert("RGB")
                self.world_width, self.world_height = self.bg_image.size
                self.photo_bg = ImageTk.PhotoImage(self.bg_image)
                
                # Sprawdź, czy self.canvas istnieje
                if hasattr(self, 'canvas'):
                    # Aktualizacja rozmiaru canvas
                    self.canvas.config(scrollregion=(0, 0, self.world_width, self.world_height))
                    
                    # Odświeżenie mapy
                    self.draw_grid()
                else:
                    print("Canvas nie został jeszcze zainicjalizowany.")
                
                # Aktualizacja ścieżki w konfiguracji
                self.map_image_path = file_path
                self.config["map_image_path"] = file_path
                
                # Aktualizacja ścieżki pliku roboczego po zmianie mapy
                self.current_working_file = self.get_working_data_path()
                print(f"Zaktualizowano ścieżkę pliku roboczego: {self.current_working_file}")
                
                messagebox.showinfo("Sukces", "Załadowano nową mapę.")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się załadować mapy:\n{str(e)}")
        else:
            # Jeśli użytkownik anulował, zachowaj poprzednią ścieżkę
            pass

    def add_key_point_dialog(self):
        """Okno dialogowe do dodawania kluczowego punktu."""
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return

        # Tworzymy nowe okno dialogowe
        dialog = tk.Toplevel(self.root)
        dialog.title("Dodaj kluczowy punkt")
        dialog.geometry("300x150")
        dialog.transient(self.root)  # Ustawienie jako okno modalne
        dialog.grab_set()

        # Etykieta i lista rozwijana dla typu punktu
        tk.Label(dialog, text="Wybierz typ punktu:", font=("Arial", 10)).pack(pady=10)
        selected_type = tk.StringVar(value=list(self.available_key_point_types.keys())[0])  # Domyślnie pierwszy typ
        tk.OptionMenu(dialog, selected_type, *self.available_key_point_types.keys()).pack()

        # Funkcja obsługująca zapis punktu
        def save_key_point():
            point_type = selected_type.get()
            value = self.available_key_point_types[point_type]  # Automatyczne przypisanie wartości
            self.key_points[self.selected_hex] = {"type": point_type, "value": value}
            self.save_data()
            self.draw_key_point(self.selected_hex, point_type, value)
            messagebox.showinfo("Sukces", f"Dodano kluczowy punkt '{point_type}' o wartości {value} na heksie {self.selected_hex}.")
            dialog.destroy()

        # Przycisk zapisu
        tk.Button(dialog, text="Zapisz", command=save_key_point, bg="green", fg="white").pack(pady=10)

        # Przycisk anulowania
        tk.Button(dialog, text="Anuluj", command=dialog.destroy, bg="red", fg="white").pack(pady=5)

    def draw_key_point(self, hex_id, point_type, value):
        """Rysuje kluczowy punkt na mapie."""
        if hex_id in self.hex_centers:
            cx, cy = self.hex_centers[hex_id]
            self.canvas.create_text(cx, cy, text=f"{point_type}\n({value})", fill="yellow", 
                                    font=("Arial", 10, "bold"), tags=f"key_point_{hex_id}")

    def on_canvas_hover(self, event):
        """Obsługuje zdarzenie najechania myszką na heks."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        hovered_hex = None

        # Sprawdzamy, czy punkt znajduje się wewnątrz któregoś heksagonu
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                hovered_hex = hex_id
                break

        if hovered_hex:
            # Pobierz dane heksu
            terrain = self.hex_data.get(hovered_hex, self.hex_defaults)
            move_mod = terrain.get('move_mod', self.hex_defaults.get('move_mod', 0))
            defense_mod = terrain.get('defense_mod', self.hex_defaults.get('defense_mod', 0))
            key_point = self.key_points.get(hovered_hex, None)

            # Aktualizuj tabelkę kontrolną
            self.hex_info_label.config(text=f"Heks: {hovered_hex}")
            self.terrain_info_label.config(text=f"Teren: {terrain}")
            self.modifiers_info_label.config(text=f"Modyfikatory: Ruch: {move_mod}, Obrona: {defense_mod}")
            if key_point:
                self.key_point_info_label.config(text=f"Kluczowy punkt: {key_point['type']} ({key_point['value']})")
            else:
                self.key_point_info_label.config(text="Kluczowy punkt: brak")
        else:
            # Jeśli nie najeżdżamy na żaden heks, wyczyść tabelkę
            self.hex_info_label.config(text="Heks: brak")
            self.terrain_info_label.config(text="Teren: brak")
            self.modifiers_info_label.config(text="Modyfikatory: brak")
            self.key_point_info_label.config(text="Kluczowy punkt: brak")

    def on_close(self):
        answer = messagebox.askyesno("Zamykanie programu", "Czy chcesz zapisać mapę przed zamknięciem?")
        if answer:
            self.save_map_as_image()
        self.root.destroy()

# ----------------------------
# Uruchomienie interfejsu
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Interaktywny Edytor Mapy Heksagonalnej")
    root.geometry("1024x768")  # Dodane ustawienie domyślnego rozmiaru okna
    editor = MapEditor(root, CONFIG)
    root.protocol("WM_DELETE_WINDOW", editor.on_close)
    root.mainloop()
