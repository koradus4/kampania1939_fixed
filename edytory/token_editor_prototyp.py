import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json, os, math, shutil, sys
from PIL import Image, ImageDraw, ImageTk, ImageFont
from pathlib import Path

# ───────── SCIEŻKI WZGLĘDNE ─────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # katalog główny repo
ASSET_ROOT   = PROJECT_ROOT / "assets"
TOKENS_ROOT  = ASSET_ROOT / "tokens"
TOKENS_ROOT.mkdir(parents=True, exist_ok=True)

# Dodanie biblioteki do odtwarzania dźwięków
try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    messagebox.showwarning("Brak biblioteki dźwięku", 
                           "Biblioteka 'playsound' nie jest zainstalowana. "
                           "Podgląd dźwięków nie będzie dostępny.\n\n"
                           "Aby zainstalować bibliotekę, użyj komendy:\n"
                           "pip install playsound")

# Funkcja do określania katalogu aplikacji (działa zarówno dla .py jak i .exe)
def get_application_path():
    if getattr(sys, 'frozen', False):
        # Jeśli uruchomione jako plik wykonawczy (.exe)
        return os.path.dirname(sys.executable)
    else:
        # Jeśli uruchomione jako skrypt
        return os.path.dirname(os.path.abspath(__file__))

def create_flag_background(nation, width, height):
    """Generates a flag image for the given nation, filling the entire area."""
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bg)
    if nation == "Polska":
        draw.rectangle([0, 0, width, height / 2], fill="white")
        draw.rectangle([0, height / 2, width, height], fill="red")
    elif nation == "Japonia":
        draw.rectangle([0, 0, width, height], fill="white")
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 4
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="red")
    elif nation == "Niemcy":
        stripe_height = height / 3
        draw.rectangle([0, 0, width, stripe_height], fill="black")
        draw.rectangle([0, stripe_height, width, 2 * stripe_height], fill="red")
        draw.rectangle([0, 2 * stripe_height, width, height], fill="gold")
    elif nation == "Francja":
        stripe_width = width / 3
        draw.rectangle([0, 0, stripe_width, height], fill="blue")
        draw.rectangle([stripe_width, 0, 2 * stripe_width, height], fill="white")
        draw.rectangle([2 * stripe_width, 0, width, height], fill="red")
    elif nation == "Stany Zjednoczone":
        stripe_height = height / 13
        for i in range(13):
            color = "red" if i % 2 == 0 else "white"
            draw.rectangle([0, i * stripe_height, width, (i + 1) * stripe_height], fill=color)
        draw.rectangle([0, 0, width * 0.4, 7 * stripe_height], fill="blue")
    elif nation == "Wielka Brytania":
        draw.rectangle([0, 0, width, height], fill="blue")
        line_width = int(width * 0.1)
        draw.line([(0, 0), (width, height)], fill="red", width=line_width)
        draw.line([(width, 0), (0, height)], fill="red", width=line_width)
        line_width2 = int(width * 0.05)
        draw.line([(0, 0), (width, height)], fill="white", width=line_width2)
        draw.line([(width, 0), (0, height)], fill="white", width=line_width2)
    elif nation == "Związek Radziecki":
        draw.rectangle([0, 0, width, height], fill="red")
    else:
        draw.rectangle([0, 0, width, height], fill="gray")
    return bg

class TokenEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Edytor Żetonów")
        self.root.geometry("800x600")  # Adjusted window size for better visibility on a tablet
        self.root.configure(bg="darkolivegreen")

        # Nagłówek
        header_frame = tk.Frame(root, bg="olivedrab", bd=5, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text="Generator żetonów do HISTORYCZNEJ GRY BITEWNEJ WRZESIEŃ 1939",
                                bg="olivedrab", fg="white", font=("Arial", 20, "bold"))
        header_label.pack(pady=10)

        # Rozmiar tokena
        self.hex_token_size_var = tk.IntVar(value=240)
        self.square_token_size_var = tk.IntVar(value=240)

        # Ustawienie kształtu – opcje "Heks" (aktywny) i "Prostokąt" (aktywny)
        self.shape = tk.StringVar(value="Prostokąt")
        self.nation = tk.StringVar(value="Polska")
        self.unit_type = tk.StringVar(value="P")
        self.unit_size = tk.StringVar(value="Pluton")
        
        self.movement_points = tk.StringVar()
        self.attack_range = tk.StringVar()
        self.attack_value = tk.StringVar()
        self.combat_value = tk.StringVar()
        self.unit_maintenance = tk.StringVar()
        self.purchase_value = tk.StringVar()
        self.sight_range = tk.StringVar()  # Nowa zmienna dla zasięgu widzenia
        self.defense_value = tk.StringVar()  # Nowa zmienna dla wartości obrony
        # Usuwamy obsługę maxMovePoints i currentMovePoints z edytora
        # self.max_move_points = tk.StringVar()
        # self.current_move_points = tk.StringVar()
        # self._max_mp_manual = False  # Flaga: czy użytkownik ręcznie ustawił maxMovePoints

        self.custom_bg_path = None

        # Parametry transformacji tła
        self.bg_rotation = 0      
        self.bg_scale = 1.0       
        self.bg_translate_x = 0   
        self.bg_translate_y = 0   

        # Kolor napisów – domyślnie ustawiony dla "Polska" (black)
        self.variable_text_color = "black"

        # Katalog zapisu
        self.save_directory = str(TOKENS_ROOT)      # start w assets/tokens        # ─── Domyślne wartości żywotności (strength) dla unitType__unitSize ───
        self.default_strengths = {
            # Piechota - wzmocniona
            "P__Pluton": 12, "P__Kompania": 36, "P__Batalion": 72,
            # Kawaleria  
            "K__Pluton": 6, "K__Kompania": 18, "K__Batalion": 36,
            # Czołgi ciężkie - osłabione
            "TC__Pluton": 8, "TC__Kompania": 24, "TC__Batalion": 48,
            # Czołgi średnie
            "TŚ__Pluton": 7, "TŚ__Kompania": 21, "TŚ__Batalion": 42,
            # Czołgi lekkie
            "TL__Pluton": 6, "TL__Kompania": 18, "TL__Batalion": 36,
            # Samochody pancerne
            "TS__Pluton": 5, "TS__Kompania": 15, "TS__Batalion": 30,
            # Artyleria ciężka - wzmocniona
            "AC__Pluton": 8, "AC__Kompania": 24, "AC__Batalion": 48,
            # Artyleria lekka
            "AL__Pluton": 7, "AL__Kompania": 21, "AL__Batalion": 42,
            # Artyleria plot
            "AP__Pluton": 6, "AP__Kompania": 18, "AP__Batalion": 36,
            # Zaopatrzenie
            "Z__Pluton": 4, "Z__Kompania": 12, "Z__Batalion": 24,
            # Dowództwo
            "D__Pluton": 3, "D__Kompania": 9, "D__Batalion": 18,
            # Generał
            "G__Pluton": 2, "G__Kompania": 6, "G__Batalion": 12
        }

        # Dodanie modyfikatorów obrony do wsparć
        self.support_upgrades = {
            "drużyna granatników": {
                "movement": -1,
                "range": 1,
                "attack": 2,
                "combat": 0,
                "unit_maintenance": 1,
                "purchase": 10,
                "defense": 1
            },
            "sekcja km.ppanc": {
                "movement": -1,
                "range": 1,
                "attack": 2,
                "combat": 0,
                "unit_maintenance": 2,
                "purchase": 10,
                "defense": 2
            },
            "sekcja ckm": {
                "movement": -1,
                "range": 1,
                "attack": 2,
                "combat": 0,
                "unit_maintenance": 2,
                "purchase": 10,
                "defense": 2
            },
            "przodek dwukonny": {
                "movement": 2,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "unit_maintenance": 1,
                "purchase": 5,
                "defense": 0
            },
            "sam. ciezarowy Fiat 621": {
                "movement": 5,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "unit_maintenance": 3,
                "purchase": 8,
                "defense": 0
            },
            "sam.ciezarowy Praga Rv": {
                "movement": 5,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "unit_maintenance": 3,
                "purchase": 8,
                "defense": 0
            },
            "ciagnik altyleryjski": {
                "movement": 3,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "unit_maintenance": 4,
                "purchase": 12,
                "defense": 0
            },
            "obserwator": {
                "movement": 0,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "unit_maintenance": 1,
                "purchase": 5,
                "defense": 0
            }
        }
        self.selected_support = tk.StringVar(value="")  # Przechowuje wybrane wsparcie

        # Dodajemy słownik określający dozwolone wsparcie dla każdego typu jednostki        
        self.allowed_support = {
            "P": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", 
                 "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"],
            "K": ["sekcja ckm"],
            "TC": ["obserwator"],
            "TŚ": ["obserwator"],
            "TL": ["obserwator"],
            "TS": ["obserwator"],
            "AC": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc",
                  "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", 
                  "ciagnik altyleryjski", "obserwator"],
            "AL": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc",
                  "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv",
                  "ciagnik altyleryjski", "obserwator"],
            "AP": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc",
                  "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv",
                  "ciagnik altyleryjski", "obserwator"],
            "Z": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "obserwator"],
            "D": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", 
                 "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"],
            "G": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", 
                 "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"]
        }

        # Te atrybuty muszą być zainicjowane PRZED wywołaniem update_numeric_fields()
        self.selected_supports = set()  # Zbiór dla wielu wybranych wsparć
        self.selected_transport = tk.StringVar(value="")  # Dla pojedynczego transportu
        self.transport_types = ["przodek dwukonny", "sam. ciezarowy Fiat 621", 
                              "sam.ciezarowy Praga Rv", "ciagnik altyleryjski"]
        
        self.selected_support = tk.StringVar(value="")  # Stary atrybut - można usunąć później
        
        self.update_numeric_fields()  # Teraz to wywołanie będzie działać poprawnie

        main_container = tk.Frame(root, bg="darkolivegreen")
        main_container.pack(fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(main_container, bg="darkolivegreen")
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_frame = tk.Frame(main_container, bd=2, relief=tk.RIDGE, bg="darkolivegreen")
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.build_controls()

        self.preview_canvas = tk.Canvas(self.preview_frame, width=240, height=240, bg="dimgray")  # Adjusted canvas size
        self.preview_canvas.pack(padx=10, pady=10)
        self.dim_label = tk.Label(self.preview_frame, text="", font=("Arial", 12), bg="darkolivegreen", fg="white")
        self.dim_label.pack(padx=10, pady=(0,10))
        self.preview_image = None

        # Dodanie przycisków do podglądu dźwięków
        self.sound_frame = tk.Frame(self.preview_frame, bg="darkolivegreen")
        self.sound_frame.pack(padx=10, pady=(0,10))
        
        # Etykieta dla sekcji dźwięków
        tk.Label(self.sound_frame, text="Podgląd dźwięków:", 
                 bg="darkolivegreen", fg="white", font=("Arial", 10, "bold")).pack(pady=(0,5))
        
        # Ramka na przyciski dźwięków
        sound_buttons_frame = tk.Frame(self.sound_frame, bg="darkolivegreen")
        sound_buttons_frame.pack()
        
        # Przyciski do odtwarzania dźwięków
        self.attack_button = tk.Button(sound_buttons_frame, text="Atak", command=lambda: self.play_sound(self.sound_attack),
                                       bg="saddlebrown", fg="white", width=8, state=tk.DISABLED)
        self.attack_button.pack(side=tk.LEFT, padx=5)
        
        self.move_button = tk.Button(sound_buttons_frame, text="Ruch", command=lambda: self.play_sound(self.sound_move),
                                    bg="saddlebrown", fg="white", width=8, state=tk.DISABLED)
        self.move_button.pack(side=tk.LEFT, padx=5)
        
        self.destroy_button = tk.Button(sound_buttons_frame, text="Likwidacja", command=lambda: self.play_sound(self.sound_destroy),
                                       bg="saddlebrown", fg="white", width=8, state=tk.DISABLED)
        self.destroy_button.pack(side=tk.LEFT, padx=5)

        # Pasek transformacji tła
        self.transformation_frame = tk.Frame(self.preview_frame, bg="darkolivegreen")
        self.transformation_frame.pack(padx=10, pady=10)
        tk.Button(self.transformation_frame, text="⟵", command=self.translate_left,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="↑", command=self.translate_up,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="-", command=self.scale_down,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="+", command=self.scale_up,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="↓", command=self.translate_down,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="⟶", command=self.translate_right,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="Kolor napisów+", command=self.toggle_color_frame,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="l", command=self.rotate_left,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="p", command=self.rotate_right,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        
        self.color_frame_visible = False
        self.color_frame = tk.Frame(self.preview_frame, bg="darkolivegreen")
        
        self.preview_canvas.bind("<Enter>", self.on_mouse_enter)
        self.preview_canvas.bind("<Motion>", self.on_mouse_motion)
        self.preview_canvas.bind("<Leave>", self.on_mouse_leave)
        self.tooltip = None

        # Przyciski zapisu i wyboru tła
        btn_frame = tk.Frame(self.control_frame, bg="darkolivegreen")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Podgląd", command=self.update_preview,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Wgraj dźwięki", command=self.load_sounds,
                  bg="gray", fg="white", state=tk.DISABLED).pack(side=tk.LEFT, padx=5)  # Nieaktywny

        tk.Button(btn_frame, text="Wczytaj token", command=self.load_token,
                  bg="gray", fg="white", state=tk.DISABLED).pack(side=tk.LEFT, padx=5)  # Nieaktywny

        tk.Button(btn_frame, text="Zapisz Żeton", command=self.save_token,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Wyczyść bazę żetonów", command=self.clear_database,
                  bg="gray", fg="white", state=tk.DISABLED).pack(side=tk.LEFT, padx=5)  # Nieaktywny

        tk.Button(btn_frame, text="Pobieranie tła", command=self.load_background,
                  bg="gray", fg="white", state=tk.DISABLED).pack(side=tk.LEFT, padx=5)  # Nieaktywny
        
        # Wybór katalogu zapisu
        save_dir_frame = tk.Frame(self.control_frame, bg="darkolivegreen")
        save_dir_frame.pack(pady=5)
        tk.Button(save_dir_frame, text="Wybierz katalog zapisu", command=self.select_save_directory,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)
        self.save_dir_label = tk.Label(save_dir_frame, text=f"Katalog zapisu: {self.save_directory}",
                                       bg="darkolivegreen", fg="white")
        self.save_dir_label.pack(side=tk.LEFT, padx=5)
        
        # Klawisze sterujące (alternatywne)
        self.root.bind("<Left>", self.on_key_left)
        self.root.bind("<Right>", self.on_key_right)
        self.root.bind("<Up>", self.on_key_up)
        self.root.bind("<Down>", self.on_key_down)
        self.root.bind("+", self.on_key_plus)
        self.root.bind("-", self.on_key_minus)
        self.root.bind("l", self.on_key_l)
        self.root.bind("p", self.on_key_p)

        # Dodajemy nowy atrybut dla przechowywania wielu wybranych wsparć
        self.selected_supports = set()
        # Osobny atrybut dla wybranego transportu
        self.selected_transport = tk.StringVar(value="")
        # Lista typów transportu
        self.transport_types = ["przodek dwukonny", "sam. ciezarowy Fiat 621", 
                              "sam.ciezarowy Praga Rv", "ciagnik altyleryjski"]

        # Dźwięki jednostki
        self.sound_attack = None
        self.sound_move = None
        self.sound_destroy = None

        # Dodajemy flagę dla tła
        self.custom_bg_copied = False

    def set_default_text_color(self):
        defaults = {
            "Polska": "black",
            "Niemcy": "blue",
            "Wielka Brytania": "black",  # zmieniono z blue na black
            "Japonia": "black",
            "Stany Zjednoczone": "black",
            "Francja": "black",
            "Związek Radziecki": "white"
        }
        self.variable_text_color = defaults.get(self.nation.get(), "black")

    def build_controls(self):
        container = tk.Frame(self.control_frame, bg="darkolivegreen")
        container.pack(fill=tk.X, padx=5, pady=5)

        left_frame = tk.Frame(container, bg="darkolivegreen")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        # Sekcja wyboru kształtu
        shape_frame = tk.LabelFrame(left_frame, text="Kształt Żetonu", bg="darkolivegreen", 
                                    fg="white", font=("Arial", 10, "bold"))
        shape_frame.pack(fill=tk.X, padx=5, pady=5)
        for text, val, state in [("Heks", "Heks", tk.DISABLED), ("Prostokąt", "Prostokąt", tk.NORMAL)]:
            tk.Radiobutton(shape_frame, text=text, variable=self.shape, value=val,
                          command=self.update_preview, state=state, 
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=20, pady=2).pack(anchor=tk.W)

        # Sekcja wyboru nacji
        nation_frame = tk.LabelFrame(left_frame, text="Nacja", bg="darkolivegreen", fg="white",
                                     font=("Arial", 10, "bold"))
        nation_frame.pack(fill=tk.X, padx=5, pady=5)

        # Lista nacji z aktywnymi tylko Polska i Niemcy
        for n, state in [("Polska", tk.NORMAL), 
                         ("Niemcy", tk.NORMAL), 
                         ("Wielka Brytania", tk.DISABLED), 
                         ("Japonia", tk.DISABLED), 
                         ("Stany Zjednoczone", tk.DISABLED), 
                         ("Francja", tk.DISABLED), 
                         ("Związek Radziecki", tk.DISABLED)]:
            tk.Radiobutton(nation_frame, text=n, variable=self.nation, value=n,
                           command=lambda n=n: [self.set_default_text_color(), self.update_preview()],
                           bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                           activebackground="saddlebrown", activeforeground="white",
                           indicatoron=False, width=20, pady=2, state=state).pack(anchor=tk.W)

        # Sekcja "Dostępne Punkty Ekonomiczne"
        economic_points_frame = tk.LabelFrame(left_frame, text="Dostępne Punkty Ekonomiczne", 
                                              bg="darkolivegreen", fg="white", font=("Arial", 10, "bold"))
        economic_points_frame.pack(fill=tk.X, padx=5, pady=5)

        # Pole do wyświetlania wartości (zmienna zostanie zdefiniowana później)
        tk.Label(economic_points_frame, text="Punkty:", bg="darkolivegreen", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Entry(economic_points_frame, state=tk.DISABLED, width=10).pack(side=tk.RIGHT, padx=5)

        # --- Sekcja wyboru dowódcy ---
        commander_frame = tk.LabelFrame(left_frame, text="Dowódca (właściciel żetonu)", bg="darkolivegreen", fg="white", font=("Arial", 10, "bold"))
        commander_frame.pack(fill=tk.X, padx=5, pady=5)
        # Lista dowódców: (numer, nacja)
        self.commanders = [
            (2, "Polska"),
            (3, "Polska"),
            (5, "Niemcy"),
            (6, "Niemcy")
        ]
        self.selected_commander = tk.StringVar(value="")
        commander_options = [f"{num} ({nation})" for num, nation in self.commanders]
        tk.Label(commander_frame, text="Wybierz dowódcę:", bg="darkolivegreen", fg="white").pack(side=tk.LEFT, padx=5)
        self.commander_menu = tk.OptionMenu(commander_frame, self.selected_commander, *commander_options)
        self.commander_menu.config(bg="saddlebrown", fg="white", width=18)
        self.commander_menu.pack(side=tk.LEFT, padx=5)

        # Pozostałe elementy w układzie grid
        unit_frame = tk.LabelFrame(container, text="Rodzaj Jednostki", bg="darkolivegreen", fg="white",
                                   font=("Arial", 9, "bold"))  # zmniejszona czcionka z 10 na 9
        unit_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")
          # Lista jednostek z typami czołgów i artylerią
        unit_types = [
            ("Piechota (P)", "P", tk.NORMAL),
            ("Kawaleria (K)", "K", tk.NORMAL),
            ("Czołg ciężki (TC)", "TC", tk.NORMAL),
            ("Czołg średni (TŚ)", "TŚ", tk.NORMAL),
            ("Czołg lekki (TL)", "TL", tk.NORMAL),
            ("Sam. pancerny (TS)", "TS", tk.NORMAL),
            ("Artyleria ciężka (AC)", "AC", tk.NORMAL),
            ("Artyleria lekka (AL)", "AL", tk.NORMAL),
            ("Artyleria plot (AP)", "AP", tk.NORMAL),
            ("Zaopatrzenie (Z)", "Z", tk.NORMAL),
            ("Dowództwo (D)", "D", tk.NORMAL),
            ("Generał (G)", "G", tk.NORMAL)
        ]

        for text, val, state in unit_types:
            tk.Radiobutton(unit_frame, text=text, variable=self.unit_type, value=val,
                          command=lambda: [self.update_numeric_fields(), 
                                           self.update_support_buttons(), 
                                           self.update_preview()],
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=20, pady=2, state=state).pack(anchor=tk.W)  # Zmieniono width z 12 na 20

        # Stworzenie kontenera dla modułów ustawionych pionowo
        vertical_container = tk.Frame(container, bg="darkolivegreen")
        vertical_container.grid(row=0, column=2, padx=5, pady=5, sticky="n")

        # Moduł Wielkość Jednostki (na górze)
        size_frame = tk.LabelFrame(vertical_container, text="Wielkość Jednostki", bg="darkolivegreen", fg="white",
                                font=("Arial", 9, "bold"))
        size_frame.pack(fill=tk.X, padx=0, pady=(0,5))  # Dodane pady aby odsunąć od następnego modułu
        for size in ["Pluton", "Kompania", "Batalion"]:
            tk.Radiobutton(size_frame, text=size, variable=self.unit_size, value=size,
                          command=lambda: [self.update_numeric_fields(), self.update_preview()],
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=12, pady=2).pack(anchor=tk.W)

        # Moduł Wsparcie jednostki (na dole)
        support_frame = tk.LabelFrame(vertical_container, text="Wsparcie jednostki", bg="darkolivegreen", fg="white",
                                    font=("Arial", 9, "bold"))
        support_frame.pack(fill=tk.X, padx=0, pady=(5,0))  # Dodane pady aby odsunąć od poprzedniego modułu
        
        # Słownik skróconych nazw dla wsparcia
        shortened_names = {
            "drużyna granatników": "granatniki",
            "sekcja km.ppanc": "km ppanc",
            "sekcja ckm": "ckm",
            "przodek dwukonny": "przodek 2k",
            "sam. ciezarowy Fiat 621": "Fiat 621",
            "sam.ciezarowy Praga Rv": "Praga Rv",
            "ciagnik altyleryjski": "ciągnik art.",
            "obserwator": "obserwator"
        }
        
        # Słownik do przechowywania przycisków wsparcia
        self.support_buttons = {}

        # Zmodyfikowana funkcja pomocnicza do obsługi kliknięcia przycisku wsparcia
        def create_toggle_command(name, button):
            def toggle():
                if (name in self.transport_types):
                    # Obsługa przycisków transportu (tryb radio)
                    if (self.selected_transport.get() == name):
                        self.selected_transport.set("")
                        button.configure(bg="darkolivegreen")
                    else:
                        # Odznacz poprzedni transport
                        if (self.selected_transport.get()):
                            old_btn = self.support_buttons[self.selected_transport.get()]
                            old_btn.configure(bg="darkolivegreen")
                        self.selected_transport.set(name)
                        button.configure(bg="saddlebrown")
                else:
                    # Obsługa pozostałych przycisków (mogą być wielokrotnie wybrane)
                    if (name in self.selected_supports):
                        self.selected_supports.remove(name)
                        button.configure(bg="darkolivegreen")
                    else:
                        self.selected_supports.add(name)
                        button.configure(bg="saddlebrown")
                
                self.update_numeric_fields()
                self.update_preview()
            return toggle

        # Przyciski dla wszystkich rodzajów wsparcia
        for support_name in self.support_upgrades.keys():
            display_name = shortened_names.get(support_name, support_name)
            btn = tk.Button(support_frame, text=display_name,
                         bg="darkolivegreen", fg="white",
                         activebackground="saddlebrown", activeforeground="white",
                         width=15, pady=2)
            # Najpierw tworzymy przycisk i dodajemy do słownika
            self.support_buttons[support_name] = btn
            # Potem ustawiamy komendę
            btn.configure(command=create_toggle_command(support_name, btn))
            btn.pack(fill=tk.X, padx=2, pady=1)

        # Dodajemy wywołanie aktualizacji stanu przycisków
        self.update_support_buttons()

        # Kontener dla wyboru rozmiaru i wartości liczbowych
        right_frame = tk.Frame(container, bg="darkolivegreen")
        right_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky="n")

        # Wybór rozmiaru tokena
        size_choice_frame = tk.LabelFrame(right_frame, text="Wybór Rozmiaru Tokena", 
                                        bg="darkolivegreen", fg="white", font=("Arial", 10, "bold"))
        size_choice_frame.pack(fill=tk.X, padx=5, pady=5)
        
        hex_size_frame = tk.Frame(size_choice_frame, bg="darkolivegreen")
        hex_size_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(hex_size_frame, text="Heks", bg="darkolivegreen", fg="white", font=("Arial", 9)).pack()  # zmniejszona czcionka
        tk.Radiobutton(hex_size_frame, text="240x240", variable=self.hex_token_size_var, value=240,
                      command=self.update_preview, state=tk.NORMAL,
                      bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                      activebackground="saddlebrown", activeforeground="white",
                      indicatoron=False, width=8, pady=2).pack(anchor=tk.W)  # zmniejszono width z 8 na 6

        square_size_frame = tk.Frame(size_choice_frame, bg="darkolivegreen")
        square_size_frame.pack(side=tk.RIGHT, padx=5)
        tk.Label(square_size_frame, text="Kwadrat", bg="darkolivegreen", fg="white", font=("Arial", 9)).pack()  # zmniejszona czcionka
        tk.Radiobutton(square_size_frame, text="240x240", variable=self.square_token_size_var, value=240,
                      command=self.update_preview, state=tk.DISABLED,
                      bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                      activebackground="saddlebrown", activeforeground="white",
                      indicatoron=False, width=8, pady=2).pack(anchor=tk.W)  # zmniejszono width z 8 na 6

        # Wartości liczbowe bezpośrednio pod wyborem rozmiaru
        numeric_frame = tk.LabelFrame(right_frame, text="Wartości Liczbowe", 
                                      bg="darkolivegreen", fg="white", font=("Arial", 10, "bold"))
        numeric_frame.pack(fill=tk.X, padx=5, pady=5)

        # Szersze pole entry dla wartości liczbowych
        entry_width = 8
        for label_text, var, fg_color, state in [
            ("Punkty Ruchu:", self.movement_points, "white", tk.NORMAL),
            ("Zasięg Ataku:", self.attack_range, "white", tk.NORMAL),
            ("Wartość Ataku:", self.attack_value, "white", tk.NORMAL),
            ("Wartość Bojowa:", self.combat_value, "gray", tk.NORMAL),  # Odblokowane pole
            ("Wartość Obrony:", self.defense_value, "blue", tk.NORMAL),  # NOWE POLE
            ("Zasięg Widzenia:", self.sight_range, "white", tk.NORMAL),
            ("Koszt Utrzymania:", self.unit_maintenance, "red", tk.NORMAL),
            ("Wartość Zakupu:", self.purchase_value, "white", tk.NORMAL)
        ]:
            entry_frame = tk.Frame(numeric_frame, bg="darkolivegreen")
            entry_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(entry_frame, text=label_text, bg="darkolivegreen", fg=fg_color).pack(side=tk.LEFT)
            entry = tk.Entry(entry_frame, textvariable=var, width=8, state=state)
            entry.pack(side=tk.RIGHT)
            # Obsługa ręcznej zmiany maxMovePoints
            # if var is self.max_move_points:
            #     def on_max_mp_change(*args):
            #         self._max_mp_manual = True
            #     self.max_move_points.trace_add('write', on_max_mp_change)

    def update_support_buttons(self):
        """Aktualizuje stan przycisków wsparcia na podstawie wybranego typu jednostki"""
        current_unit = self.unit_type.get()
        allowed = self.allowed_support.get(current_unit, [])
        
        # Resetujemy wybrane wsparcia jeśli nie są dozwolone dla nowej jednostki
        self.selected_supports = {s for s in self.selected_supports if s in allowed}
        if self.selected_transport.get() not in allowed:
            self.selected_transport.set("")
        
        # Aktualizujemy stan wszystkich przycisków
        for support_name, btn in self.support_buttons.items():
            if support_name in allowed:
                btn.configure(state=tk.NORMAL)
                # Ustawiamy kolor tła w zależności od stanu
                if support_name in self.transport_types:
                    btn.configure(bg="saddlebrown" if support_name == self.selected_transport.get() else "darkolivegreen")
                else:
                    btn.configure(bg="saddlebrown" if support_name in self.selected_supports else "darkolivegreen")
            else:
                btn.configure(state=tk.DISABLED, bg="gray")

    def update_numeric_fields(self):
        defaults = {
            "ruch": {
                "P": "7", "K": "15", 
                "TC": "8", "TŚ": "10", "TL": "12", "TS": "14",
                "AC": "6", "AL": "8", "AP": "10",
                "Z": "12", "D": "12", "G": "12"
            },
            "range": {
                "P": "1", "K": "1",
                "TC": "2", "TŚ": "2", "TL": "1", "TS": "2",
                "AC": "8", "AL": "6", "AP": "5",
                "Z": "1", "D": "0", "G": "0"
            },
            "attack": {
                "Pluton": {
                    "P": "3", "K": "3",
                    "TC": "5", "TŚ": "4", "TL": "3", "TS": "2",
                    "AC": "8", "AL": "6", "AP": "4",
                    "Z": "1", "D": "0", "G": "0"
                },
                "Kompania": {
                    "P": "6", "K": "6",
                    "TC": "10", "TŚ": "8", "TL": "6", "TS": "4",
                    "AC": "16", "AL": "12", "AP": "8",
                    "Z": "2", "D": "0", "G": "0"
                },
                "Batalion": {
                    "P": "9", "K": "9",
                    "TC": "15", "TŚ": "12", "TL": "9", "TS": "6",
                    "AC": "24", "AL": "18", "AP": "12",
                    "Z": "3", "D": "0", "G": "0"
                }
            },
            # Usuń wartość bojową z aktualizacji
            "combat": {},  # Pusta definicja, aby nie nadpisywać wartości
            "unit_maintenance": {
                "Pluton": {
                    "P": "2", "K": "3",
                    "TC": "8", "TŚ": "6", "TL": "4", "TS": "3",
                    "AC": "4", "AL": "3", "AP": "3",
                    "Z": "2", "D": "1", "G": "1"
                },
                "Kompania": {
                    "P": "4", "K": "6",
                    "TC": "16", "TŚ": "12", "TL": "8", "TS": "6",
                    "AC": "8", "AL": "6", "AP": "6",
                    "Z": "4", "D": "2", "G": "2"
                },
                "Batalion": {
                    "P": "8", "K": "9",
                    "TC": "24", "TŚ": "18", "TL": "12", "TS": "9",
                    "AC": "12", "AL": "9", "AP": "9",
                    "Z": "6", "D": "3", "G": "3"
                }
            },
            "purchase": {
                "Pluton": {
                    "P": "15", "K": "18",
                    "TC": "40", "TŚ": "32", "TL": "25", "TS": "20",
                    "AC": "35", "AL": "25", "AP": "20",
                    "Z": "16", "D": "80", "G": "120"
                },
                "Kompania": {
                    "P": "30", "K": "36",
                    "TC": "80", "TŚ": "64", "TL": "50", "TS": "40",
                    "AC": "70", "AL": "50", "AP": "40",
                    "Z": "32", "D": "80", "G": "120"
                },
                "Batalion": {
                    "P": "45", "K": "54",
                    "TC": "120", "TŚ": "96", "TL": "75", "TS": "60",
                    "AC": "105", "AL": "75", "AP": "60",
                    "Z": "48", "D": "80", "G": "120"
                }
            },
            "sight": {
                "P": "2", "K": "4",
                "TC": "2", "TŚ": "2", "TL": "2", "TS": "4",
                "AC": "2", "AL": "2", "AP": "3",
                "D": "5", "G": "6", "Z": "2"
            }
        }
        ut = self.unit_type.get()
        size = self.unit_size.get()
        self.movement_points.set(defaults["ruch"].get(ut, ""))
        # Synchronizacja maxMovePoints z movement_points jeśli nie było ręcznej zmiany
        # if not self._max_mp_manual:
        #     self.max_move_points.set(self.movement_points.get())
        # currentMovePoints zawsze domyślnie = maxMovePoints
        # self.current_move_points.set(self.max_move_points.get())
        self.attack_range.set(defaults["range"].get(ut, ""))
        self.attack_value.set(defaults["attack"][size].get(ut, ""))
        # Ustaw domyślną wartość bojową (żywotność)
        key = f"{ut}__{size}"
        self.combat_value.set(str(self.default_strengths.get(key, "")))
        self.unit_maintenance.set(defaults["unit_maintenance"][size].get(ut, ""))
        self.purchase_value.set(defaults["purchase"][size].get(ut, ""))
        self.sight_range.set(defaults["sight"].get(ut, ""))

        # Domyślne wartości obrony dla typów i wielkości jednostek
        defense_defaults = {
            "Pluton": {
                "P": "6", "K": "3", 
                "TC": "6", "TŚ": "5", "TL": "4", "TS": "3",
                "AC": "3", "AL": "4", "AP": "3",
                "Z": "2", "D": "1", "G": "1"
            },
            "Kompania": {
                "P": "15", "K": "8",
                "TC": "15", "TŚ": "12", "TL": "10", "TS": "8",
                "AC": "8", "AL": "10", "AP": "8",
                "Z": "5", "D": "2", "G": "2"
            },
            "Batalion": {
                "P": "30", "K": "16",
                "TC": "30", "TŚ": "25", "TL": "20", "TS": "16",
                "AC": "16", "AL": "20", "AP": "16",
                "Z": "10", "D": "4", "G": "4"
            }
        }
        self.defense_value.set(defense_defaults.get(size, {}).get(ut, ""))
        # Dodaj sumowanie modyfikatorów obrony ze wsparć
        current_defense = int(self.defense_value.get() or 0)
        for support in self.selected_supports:
            if support and support in self.support_upgrades:
                current_defense += self.support_upgrades[support].get("defense", 0)
        if self.selected_transport.get() in self.support_upgrades:
            current_defense += self.support_upgrades[self.selected_transport.get()].get("defense", 0)
        self.defense_value.set(str(current_defense))

        # After setting default values, apply support modifications
        all_selected = self.selected_supports | {self.selected_transport.get()} if self.selected_transport.get() else self.selected_supports
        
        # Zmienna do śledzenia czy już naliczono -1 do ruchu
        movement_penalty_applied = False
        
        # Znajdź najwyższy modyfikator zasięgu ataku wśród wsparcia
        max_range_bonus = 0
        for support in self.selected_supports:
            if support and support in self.support_upgrades:
                range_mod = self.support_upgrades[support].get("range", 0)
                max_range_bonus = max(max_range_bonus, range_mod)
        
        # Najpierw sprawdź transport, ponieważ ma priorytet
        if self.selected_transport.get():
            transport = self.support_upgrades[self.selected_transport.get()]
            current_movement = int(self.movement_points.get() or 0)
            self.movement_points.set(str(current_movement + transport["movement"]))
        
        # Następnie sprawdź pozostałe wsparcia
        for support in self.selected_supports:
            if support and support in self.support_upgrades:
                upgrade = self.support_upgrades[support]
                
                # Specjalna logika dla kary do ruchu
                if (upgrade["movement"] < 0 and not movement_penalty_applied):
                    current_movement = int(self.movement_points.get() or 0)
                    self.movement_points.set(str(current_movement - 1))
                    movement_penalty_applied = True
                
                # Pozostałe modyfikatory stosuj normalnie (oprócz zasięgu)
                current_attack = int(self.attack_value.get() or 0)
                current_combat = int(self.combat_value.get() or 0)
                current_unit_maintenance = int(self.unit_maintenance.get() or 0)
                current_purchase = int(self.purchase_value.get() or 0)
                
                self.attack_value.set(str(current_attack + upgrade["attack"]))
                self.combat_value.set(str(current_combat + upgrade["combat"]))
                self.unit_maintenance.set(str(current_unit_maintenance + upgrade["unit_maintenance"]))
                self.purchase_value.set(str(current_purchase + upgrade["purchase"]))
                
                # Apply sight range modification if present
                if "sight" in upgrade:
                    current_sight = int(self.sight_range.get() or 0)
                    self.sight_range.set(str(current_sight + upgrade["sight"]))
        
        # Zastosuj najwyższy bonus do zasięgu ataku
        if max_range_bonus > 0:
            current_range = int(self.attack_range.get() or 0)
            self.attack_range.set(str(current_range + max_range_bonus))

        # Obliczanie kosztu utrzymania z wybranych opcji wsparcia
        current_unit_maintenance = int(defaults["unit_maintenance"][size].get(ut, "0"))
        for support in self.selected_supports:
            if support in self.support_upgrades:
                current_unit_maintenance += self.support_upgrades[support].get("unit_maintenance", 0)
        if self.selected_transport.get() in self.support_upgrades:
            current_unit_maintenance += self.support_upgrades[self.selected_transport.get()].get("unit_maintenance", 0)
        self.unit_maintenance.set(str(current_unit_maintenance))

    def on_mouse_enter(self, event): 
        self.show_tooltip(event)
    def on_mouse_motion(self, event): 
        self.show_tooltip(event)
    def on_mouse_leave(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    def show_tooltip(self, event):
        text = (f"Punkty Ruchu: {self.movement_points.get()}\n"
                f"Zasięg Ataku: {self.attack_range.get()}\n"
                f"Wartość Ataku: {self.attack_value.get()}\n"
                f"Wartość Bojowa: {self.combat_value.get()}\n"
                f"Koszt Utrzymania: {self.unit_maintenance.get()}\n"
                f"Wartość Zakupu: {self.purchase_value.get()}")
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self.preview_canvas)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (event.x_root + 10, event.y_root + 10))
        tk.Label(self.tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 8)).pack()
    
    def update_preview(self):
        self.preview_canvas.delete("all")
        token_name = f"{self.nation.get()} {self.unit_type.get()} {self.unit_size.get()}"  # Generowanie nazwy żetonu

        if self.shape.get() == "Heks":
            token_size = self.hex_token_size_var.get()
            token_img = self.create_token_image(custom_size=token_size, token_name=token_name)
            self.preview_image = ImageTk.PhotoImage(token_img)
            self.preview_canvas.config(width=240, height=240)  # Zmiana z 300 na 240
            self.dim_label.config(text=f"Heks (oryginalnie {token_size}x{token_size})")
        else:
            token_size = self.square_token_size_var.get()
            token_img = self.create_token_image(custom_size=token_size, token_name=token_name)
            self.preview_image = ImageTk.PhotoImage(token_img)
            self.preview_canvas.config(width=240, height=240)  # Adjusted canvas size
            self.dim_label.config(text=f"Kwadrat (oryginalnie {token_size}x{token_size})")

        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)
    
    def load_background(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz obraz tła",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
        )
        if (file_path):
            self.custom_bg_path = file_path
            self.bg_rotation = 0
            self.bg_scale = 1.0
            self.bg_translate_x = 0
            self.bg_translate_y = 0
            self.custom_bg_copied = False  # Reset flagi przy wczytaniu nowego tła
            self.update_preview()
    
    def select_save_directory(self):
        dir_path = filedialog.askdirectory(title="Wybierz katalog zapisu")
        if dir_path:
            self.save_directory = dir_path
            self.save_dir_label.config(text=f"Katalog zapisu: {self.save_directory}")
    
    def toggle_color_frame(self):
        if self.color_frame_visible:
            self.color_frame.pack_forget()
            self.color_frame_visible = False
        else:
            self.color_frame.pack(padx=10, pady=5)
            for widget in self.color_frame.winfo_children():
                widget.destroy()
            for col in ["black", "white", "red", "green", "blue", "yellow"]:
                tk.Button(self.color_frame, text=col, bg=col, command=lambda c=col: self.change_text_color(c),
                          fg="white").pack(side=tk.LEFT, padx=5)
            self.color_frame_visible = True
    
    def change_text_color(self, color):
        self.variable_text_color = color
        self.update_preview()
    
    # Funkcje transformacji tła
    def translate_left(self):
        self.bg_translate_x -= 10
        self.update_preview()
    def translate_right(self):
        self.bg_translate_x += 10
        self.update_preview()
    def translate_up(self):
        self.bg_translate_y -= 10
        self.update_preview()
    def translate_down(self):
        self.bg_translate_y += 10
        self.update_preview()
    def scale_down(self):
        self.bg_scale = max(0.1, self.bg_scale - 0.1)
        self.update_preview()
    def scale_up(self):
        self.bg_scale += 0.1
        self.update_preview()
    
    # Funkcje obracania tła
    def rotate_left(self):
        self.bg_rotation = (self.bg_rotation - 10) % 360
        self.update_preview()
    def rotate_right(self):
        self.bg_rotation = (self.bg_rotation + 10) % 360
        self.update_preview()
    # Obsługa klawiatury
    def on_key_left(self, event):
        self.bg_translate_x -= 10
        self.update_preview()
    def on_key_right(self, event):
        self.bg_translate_x += 10
        self.update_preview()
    def on_key_up(self, event):
        self.bg_translate_y -= 10
        self.update_preview()
    def on_key_down(self, event):
        self.bg_translate_y += 10
        self.update_preview()
    def on_key_plus(self, event):
        self.bg_scale += 0.1
        self.update_preview()
    def on_key_minus(self, event):
        self.bg_scale = max(0.1, self.bg_scale - 0.1)
        self.update_preview()
    def on_key_l(self, event):
        self.rotate_left()
    def on_key_p(self, event):
        self.rotate_right()
    
    def create_token_image(self, custom_size=None, token_name=None):
        if custom_size is not None:
            width = height = custom_size
        else:
            width = height = (self.hex_token_size_var.get() if self.shape.get() == "Heks" 
                              else self.square_token_size_var.get())
        base_bg = create_flag_background(self.nation.get(), width, height)
        token_img = base_bg.copy()
        draw = ImageDraw.Draw(token_img)

        # Obramowanie
        if self.shape.get() == "Heks":
            pts = [
                (width * 0.25, 0),
                (width * 0.75, 0),
                (width,        height * 0.5),
                (width * 0.75, height),
                (width * 0.25, height),
                (0,            height * 0.5)
            ]
            mask = Image.new("L", (width, height), 0)
            ImageDraw.Draw(mask).polygon(pts, fill=255)
            token_img.putalpha(mask)
            draw.line(pts + [pts[0]], fill="black", width=3, joint="curve")
        else:
            draw.rectangle([0, 0, width, height], outline="black", width=3)

        # Przygotowanie tekstów
        nation = self.nation.get()
        unit_type_full = {
            "P": "Piechota",
            "K": "Kawaleria",
            "TC": "Czołg ciężki",
            "TŚ": "Czołg średni",
            "TL": "Czołg lekki",
            "TS": "Sam. pancerny",
            "AC": "Artyleria ciężka",
            "AL": "Artyleria lekka",
            "AP": "Artyleria plot",
            "Z": "Zaopatrzenie",
            "D": "Dowództwo",
            "G": "Generał"
        }.get(self.unit_type.get(), self.unit_type.get())
        unit_size = self.unit_size.get()
        unit_symbol = {"Pluton": "***", "Kompania": "I", "Batalion": "II"}.get(unit_size, "")

        # Czcionki
        try:
            # Nacja bardzo mała, typ bardzo duży, reszta jak dotąd
            font_nation = ImageFont.truetype("arial.ttf", int(width * 0.07))
            font_type = ImageFont.truetype("arialbd.ttf", int(width * 0.19))  # DUŻA, pogrubiona
            font_size = ImageFont.truetype("arial.ttf", int(width * 0.10))
            font_symbol = ImageFont.truetype("arialbd.ttf", int(width * 0.18))
        except Exception:
            font_nation = font_type = font_size = font_symbol = ImageFont.load_default()

        text_color = self.variable_text_color if self.variable_text_color else "black"

        margin = 8
        y = margin

        # Nacja – bardzo mała lub pomijana
        show_nation = False  # Możesz zmienić na True jeśli chcesz wyświetlać nację
        if show_nation:
            bbox_nation = draw.textbbox((0, 0), nation, font=font_nation)
            x_nation = (width - (bbox_nation[2] - bbox_nation[0])) / 2
            draw.text((x_nation, y), nation, fill=text_color, font=font_nation)
            y += bbox_nation[3] - bbox_nation[1] + int(margin/2)

        # Pełna nazwa rodzaju jednostki – DUŻA, centralna, z zawijaniem
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current = ""
            for word in words:
                test = current + (" " if current else "") + word
                if draw.textlength(test, font=font) <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
            return lines

        # Wyznacz linie zawinięte i ich łączną wysokość
        max_text_width = int(width * 0.9)
        type_lines = wrap_text(unit_type_full, font_type, max_text_width)
        total_type_height = sum(draw.textbbox((0,0), line, font=font_type)[3] - draw.textbbox((0,0), line, font=font_type)[1] for line in type_lines)
        total_type_height += (len(type_lines)-1) * 2  # odstęp między liniami

        bbox_size = draw.textbbox((0, 0), unit_size, font=font_size)
        size_height = bbox_size[3] - bbox_size[1]
        bbox_symbol = draw.textbbox((0, 0), unit_symbol, font=font_symbol)
        symbol_height = bbox_symbol[3] - bbox_symbol[1]
        margin = 8
        gap_type_to_size = margin * 2  # duży odstęp pod nazwą rodzaju jednostki
        gap_size_to_symbol = 2         # bardzo mały odstęp pod nazwą wielkości
        total_height = total_type_height + gap_type_to_size + size_height + gap_size_to_symbol + symbol_height

        # Wyśrodkuj całość pionowo
        y = (height - total_height) // 2

        # Rysuj linie nazwy rodzaju jednostki
        for line in type_lines:
            bbox = draw.textbbox((0, 0), line, font=font_type)
            x = (width - (bbox[2] - bbox[0])) / 2
            draw.text((x, y), line, fill=text_color, font=font_type)
            y += bbox[3] - bbox[1] + 2  # odstęp między liniami
        y += gap_type_to_size - 2  # po ostatniej linii, bo już +2 było dodane

        # Nazwa wielkości (Pluton/Kompania/Batalion) – bezpośrednio nad symbolem
        bbox_size = draw.textbbox((0, 0), unit_size, font=font_size)
        x_size = (width - (bbox_size[2] - bbox_size[0])) / 2
        draw.text((x_size, y), unit_size, fill=text_color, font=font_size)
        y += bbox_size[3] - bbox_size[1] + gap_size_to_symbol        # Symbol wielkości – bezpośrednio pod nazwą wielkości
        bbox_symbol = draw.textbbox((0, 0), unit_symbol, font=font_symbol)
        x_symbol = (width - (bbox_symbol[2] - bbox_symbol[0])) / 2
        draw.text((x_symbol, y), unit_symbol, fill=text_color, font=font_symbol)

        return token_img

    def save_token(self):
        """Zapisuje żeton w nowej strukturze + aktualizuje centralny indeks."""
        
        # Dodatkowe potwierdzenie przed rozpoczęciem procesu zapisu
        if not messagebox.askyesno("Potwierdzenie", 
                                   "Czy na pewno chcesz zapisać ten żeton?\n\n"
                                   "Kliknij 'Nie' aby anulować bez zapisywania."):
            return
        
        FINAL_SIZE = 240  # px – docelowy rozmiar png

        nation     = self.nation.get()
        unit_type  = self.unit_type.get()
        unit_size  = self.unit_size.get()
        # Pobierz numer dowódcy i skrót nacji
        commander_full = self.selected_commander.get()  # np. '2 (Polska)'
        if not commander_full:
            messagebox.showerror("Błąd", "Musisz wybrać dowódcę (właściciela żetonu) przed zapisem!")
            return
        commander_num = commander_full.split()[0] if commander_full else "?"

        nation_short = "PL" if nation == "Polska" else ("N" if nation == "Niemcy" else nation[:2].upper())
        base_id    = f"{unit_type}_{unit_size}".replace(" ", "_")        # np. P_Pluton        # ── 1. dodatkowa etykieta użytkownika ───────────────────────────
        default_label = f"{commander_num}_{nation_short}_{unit_type}_{unit_size}"
        user_label = simpledialog.askstring(
            "Nazwa wyświetlana",
            "Podaj nazwę oddziału (np. '1. Podhalański Pluton Czołgów')\n"
            "Możesz zostawić domyślną – wtedy grafika będzie miała nazwę domyślną.\n\n"
            "UWAGA: Kliknij 'Cancel' lub 'X' aby anulować zapisywanie żetonu.",
            initialvalue=default_label
        )
        
        # Jeśli użytkownik anulował dialog, przerwij zapisywanie
        if user_label is None:
            return
        
        # Jeśli pusty string, użyj domyślnej etykiety
        if not user_label.strip():
            user_label = default_label

        # ── 2. zrób slug z etykiety, aby nie nadpisywać poprzednich ──
        import re, datetime as _dt
        label_slug = re.sub(r"[^A-Za-z0-9]+", "_", user_label.strip())[:32] if user_label else ""
        token_id   = f"{base_id}__{label_slug}" if label_slug else base_id

        token_dir = TOKENS_ROOT / nation / token_id
        # jeżeli katalog już istnieje, dodaj znacznik czasu
        if token_dir.exists():
            ts = _dt.datetime.now().strftime("%Y%m%d%H%M%S")
            token_id  += f"_{ts}"
            token_dir  = TOKENS_ROOT / nation / token_id
        token_dir.mkdir(parents=True, exist_ok=True)

        # ---- PNG ---- – dodaj etykietę, jeśli ją wpisano
        token_name_on_img = user_label if user_label else f"{nation} {base_id}"
        img = self.create_token_image(custom_size=FINAL_SIZE,
                                      token_name=token_name_on_img)
        img.save(token_dir / "token.png")

        # Pobierz wybranego dowódzcę
        owner = commander_full  # np. '2 (Polska)'

        # Przygotuj pełną nazwę jednostki do zapisu w JSON
        unit_type_full = {
            "P": "Piechota",
            "K": "Kawaleria",
            "TC": "Czołg ciężki",
            "TŚ": "Czołg średni",
            "TL": "Czołg lekki",
            "TS": "Sam. pancerny",
            "AC": "Artyleria ciężka",
            "AL": "Artyleria lekka",
            "AP": "Artyleria plot",
            "Z": "Zaopatrzenie",
            "D": "Dowództwo",
            "G": "Generał"
        }.get(unit_type, unit_type)
        unit_symbol = {"Pluton": "***", "Kompania": "I", "Batalion": "II"}.get(unit_size, "")
        unit_full_name = f"{nation} {unit_type_full} {unit_size} {unit_symbol}".strip()

        # ---- JSON ----
        meta = {
            "id":   token_id,                      # unikalny klucz
            "nation":    nation,
            "unitType":  unit_type,
            "unitSize":  unit_size,
            "shape":     self.shape.get().lower(),   # "heks" lub "prostokąt"
            "label":     user_label,            # ← nowe pole
            "unit_full_name": unit_full_name,   # ← NOWE POLE
            "move":      int(self.movement_points.get() or 0),
            "attack":    { "range": int(self.attack_range.get() or 0),
                           "value": int(self.attack_value.get() or 0) },
            "combat_value": int(self.combat_value.get() or 0),  # Dodane pole
            "defense_value": int(self.defense_value.get() or 0),  # NOWE POLE
            "maintenance": int(self.unit_maintenance.get() or 0),
            "price":       int(self.purchase_value.get() or 0),
            "sight":       int(self.sight_range.get() or 0),
            "owner":       owner,
            # względna ścieżka do stałej nazwy pliku
            "image": str((Path('assets') / 'tokens' / nation / token_id / 'token.png')
                         .as_posix()),
            "w": FINAL_SIZE, "h": FINAL_SIZE
        }
        with open(token_dir / "token.json", "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2, ensure_ascii=False)

        self.build_index()
        messagebox.showinfo("✔", f"Zapisano żeton w  {token_dir}")

    def build_index(self):
        """Generuje assets/tokens/index.json zawierający wszystkie definicje."""
        all_defs = []
        for jf in TOKENS_ROOT.rglob("token.json"):
            try:
                all_defs.append(json.loads(jf.read_text(encoding="utf-8")))
            except Exception:
                pass
        (TOKENS_ROOT / "index.json").write_text(json.dumps(all_defs, indent=2, ensure_ascii=False),
                                               encoding="utf-8")

    def clear_database(self):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz wyczyścić bazę żetonów"):
            index_json_path = os.path.join(self.save_directory, "token_index.json")
            old_json_path = os.path.join(self.save_directory, "token_data.json")
            
            if os.path.exists(index_json_path):
                # Wczytaj dane indeksu aby znaleźć wszystkie podkatalogi
                try:
                    with open(index_json_path, "r", encoding="utf-8") as f:
                        index_data = json.load(f)
                    
                    # Usuń wszystkie podkatalogi żetonów
                    for token_name, token_info in index_data.items():
                        token_dir = os.path.join(self.save_directory, token_info.get("directory", token_name))
                        if os.path.exists(token_dir) and os.path.isdir(token_dir):
                            try:
                                shutil.rmtree(token_dir)
                            except Exception as e:
                                messagebox.showwarning("Ostrzeżenie", f"Nie można usunąć katalogu {token_dir}: {str(e)}")
                except Exception as e:
                    messagebox.showwarning("Ostrzeżenie", f"Błąd podczas czytania danych indeksu: {str(e)}")
                
                # Usuń plik JSON indeksu
                os.remove(index_json_path)
            
            # Sprawdź i usuń stary format danych
            if os.path.exists(old_json_path):
                try:
                    with open(old_json_path, "r", encoding="utf-8") as f:
                        saved_data = json.load(f)
                    
                    # Usuń wszystkie podkatalogi żetonów
                    for token_name, token_data in saved_data.items():
                        token_dir = os.path.join(self.save_directory, token_data.get("token_directory", token_name))
                        if os.path.exists(token_dir) and os.path.isdir(token_dir):
                            try:
                                shutil.rmtree(token_dir)
                            except Exception as e:
                                messagebox.showwarning("Ostrzeżenie", f"Nie można usunąć katalogu {token_dir}: {str(e)}")
                except Exception as e:
                    messagebox.showwarning("Ostrzeżenie", f"Błąd podczas czytania danych żetonów: {str(e)}")
                
                # Usuń plik JSON
                os.remove(old_json_path)
            
            # Usuń pliki PNG, które mogą zostać w głównym katalogu
            for file in os.listdir(self.save_directory):
                if file.endswith(".png"):
                    try:
                        os.remove(os.path.join(self.save_directory, file))
                    except Exception as e:
                        messagebox.showwarning("Ostrzeżenie", f"Nie można usunąć pliku {file}: {str(e)}")
            
            messagebox.showinfo("Baza wyczyszczona", "Baza żetonów oraz miniatury została wyczyszczona.")

    def load_sounds(self):
        """Wczytuje pliki dźwiękowe dla jednostki z wyjaśnieniami."""
        sound_info = [
            ("atak", "sound_attack", "Dźwięk odtwarzany, gdy jednostka atakuje"),
            ("ruch", "sound_move", "Dźwięk odtwarzany podczas ruchu jednostki"),
            ("likwidacja", "sound_destroy", "Dźwięk odtwarzany przy zniszczeniu jednostki")
        ]
        
        for label, attr, description in sound_info:
            if messagebox.askyesno("Wczytywanie dźwięku", 
                                  f"{description}\n\nCzy chcesz wczytać dźwięk dla: {label}?"):
                path = filedialog.askopenfilename(
                    title=f"Wybierz dźwięk dla: {label}",
                    filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav"), ("Wszystkie pliki", "*.*")]
                )
                if path:
                    setattr(self, attr, path)
                    messagebox.showinfo("Dźwięk wczytany", 
                                       f"Dźwięk '{os.path.basename(path)}' został wczytany dla akcji: {label}")
                else:
                    messagebox.showinfo("Anulowano", f"Nie wybrano dźwięku dla akcji: {label}")
        
        # Po załadowaniu dźwięków aktualizuj stan przycisków
        self.update_sound_buttons()
    
    def play_sound(self, sound_path):
        """Odtwarza dźwięk z podanej ścieżki."""
        if not SOUND_AVAILABLE:
            messagebox.showinfo("Brak biblioteki dźwięku", 
                               "Biblioteka 'playsound' nie jest zainstalowana. Nie można odtworzyć dźwięku.")
            return
            
        if sound_path and os.path.exists(sound_path):
            try:
                playsound(sound_path)
            except Exception as e:
                messagebox.showerror("Błąd odtwarzania", f"Nie można odtworzyć dźwięku: {str(e)}")
        else:
            messagebox.showinfo("Brak dźwięku", "Dźwięk nie został wczytany lub plik nie istnieje.")
    
    def update_sound_buttons(self):
        """Aktualizuje stan przycisków dźwięku w zależności od dostępności plików."""
        if not SOUND_AVAILABLE:
            return
            
        # Aktualizuj stan przycisków w zależności od dostępności dźwięków
        self.attack_button.config(state=tk.NORMAL if self.sound_attack and os.path.exists(self.sound_attack) else tk.DISABLED)
        self.move_button.config(state=tk.NORMAL if self.sound_move and os.path.exists(self.sound_move) else tk.DISABLED)
        self.destroy_button.config(state=tk.NORMAL if self.sound_destroy and os.path.exists(self.sound_destroy) else tk.DISABLED)

    def load_token(self):
        """Wczytuje istniejący token z pliku JSON w podkatalogu."""
        index_json_path = os.path.join(self.save_directory, "token_index.json")
        if not os.path.exists(index_json_path):
            messagebox.showerror("Błąd", "Nie znaleziono pliku indeksu tokenów (token_index.json) w katalogu zapisu.")
            return
        try:
            # Tutaj docelowo kod wczytywania tokena
            pass
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać tokena: {str(e)}")

    def load_token_old_format(self, json_path):
        """Wczytuje token ze starego formatu pliku JSON (kompatybilność wsteczna)."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                
            if not saved_data:
                messagebox.showinfo("Brak tokenów", "Baza tokenów jest pusta.")
                return
                
            # Stwórz listę dostępnych tokenów
            token_names = list(saved_data.keys())
            token_name = simpledialog.askstring("Wczytaj token", 
                                              "Wybierz nazwę tokena do wczytania:",
                                              initialvalue=token_names[0])
                
            if not token_name or token_name not in saved_data:
                return
                
            token_data = saved_data[token_name]
            
            # Określamy katalog tokena
            token_directory = os.path.join(self.save_directory, token_data.get("token_directory", token_name))
            if not os.path.exists(token_directory):
                token_directory = self.save_directory  # Jeśli podkatalog nie istnieje, użyj głównego katalogu
                
            # Wczytaj dane tokena
            self.shape.set(token_data.get("shape", "Prostokąt"))
            self.nation.set(token_data.get("nation", "Polska"))
            self.unit_type.set(token_data.get("unit_type", "P"))
            self.unit_size.set(token_data.get("unit_size", "Pluton"))
            self.movement_points.set(token_data.get("movement_points", ""))
            self.attack_range.set(token_data.get("attack_range", ""))
            self.attack_value.set(token_data.get("attack_value", ""))
            self.combat_value.set(token_data.get("combat_value", ""))
            self.unit_maintenance.set(token_data.get("unit_maintenance", ""))
            self.purchase_value.set(token_data.get("purchase_value", ""))
            self.sight_range.set(token_data.get("sight_range", ""))
            self.bg_rotation = token_data.get("bg_rotation", 0)
            self.bg_scale = token_data.get("bg_scale", 1.0)
            self.bg_translate_x = token_data.get("bg_translate_x", 0)
            self.bg_translate_y = token_data.get("bg_translate_y", 0)
            self.variable_text_color = token_data.get("variable_text_color", "black")
            # Usuwamy maxMovePoints i currentMovePoints z edytora
                
            # Wczytaj dźwięki z podkatalogu tokena
            for sound_type in ["sound_attack", "sound_move", "sound_destroy"]:
                file_key = f"{sound_type}_file"
                if token_data.get(file_key):
                    sound_path = os.path.join(token_directory, token_data.get(file_key))
                    if os.path.exists(sound_path):
                        setattr(self, sound_type, sound_path)
                    else:
                        setattr(self, sound_type, None)
                else:
                    setattr(self, sound_type, None)
                
            # Wczytaj tło z podkatalogu tokena
            if token_data.get("background_file") and os.path.exists(os.path.join(token_directory, token_data.get("background_file"))):
                self.custom_bg_path = os.path.join(token_directory, token_data.get("background_file"))
                self.custom_bg_copied = True
            else:
                self.custom_bg_path = None
                self.custom_bg_copied = False
                
            # Aktualizuj interfejs
            self.update_support_buttons()
            self.update_numeric_fields()
            self.update_preview()
            self.update_sound_buttons()
                
            messagebox.showinfo("Wczytano", f"Token '{token_name}' został wczytany.")
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać tokena: {str(e)}")

if __name__ == "__main__":
    import tkinter as tk
    from PIL import Image, ImageDraw, ImageTk, ImageFont
    root = tk.Tk()
    app = TokenEditor(root)
    root.mainloop()
