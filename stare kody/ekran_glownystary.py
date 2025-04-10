"""
Moduł zawierający główną klasę interfejsu gry (EkranGlowny).
Spaja wszystkie komponenty (mapa, panele żetonów, pasek stanu) i zarządza logiką gry.
"""
import os
import math
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json  # do obsługi zapisu/odczytu stanu gry
# Import modułów aplikacji
from model import zasoby
from model import mapa
from model import jednostka
from core.ekonomia import EconomySystem
from core import tura
from core import rozkazy
from gui.panel_generala import PanelGenerala
from gui.pasek_stanu import PasekStanu
from utils import loader

class EkranGlowny(tk.Tk):
    """
    Główne okno aplikacji gry. Inicjalizuje wszystkie elementy interfejsu i zarządza przebiegiem gry.
    """
    def __init__(self, player1_nation: str, player2_nation: str):
        super().__init__()
        self.title("Wrzesień 1939 – Główna Gra")
        self.geometry("1280x800")
        self.configure(bg="lightgray")

        # Przechowuj wybory graczy
        self.player1_choice = player1_nation
        self.player2_choice = player2_nation

        # Domyślnie zaczyna Gracz 1
        self.current_turn = "Gracz 1"
        self.current_turn_nation = self.player1_choice

        # Wyświetl wybory w konsoli (dla debugowania)
        print(f"Gracz 1 wybrał: {self.player1_choice}")
        print(f"Gracz 2 wybrał: {self.player2_choice}")

        # Ustawienia podstawowe okna
        self.resizable(True, True)
        # self.state('zoomed')  # Można odkomentować, aby uruchamiać w trybie pełnoekranowym
        self.configure(bg="darkolivegreen")
        # Atrybuty stanu gry
        # Inicjalizacja systemów gry
        self.economy_system = EconomySystem()           # System ekonomii (punkty ekonomiczne i zaopatrzenia)
        self.orders_manager = rozkazy.OrdersManager()   # Zarządzanie rozkazami (na przyszłość, np. ruch/atak jednostek)
        # Ustawienia mapy i danych
        self.hex_data = {}      # Dane dotyczące poszczególnych heksów (może być nadpisane danymi z pliku)
        self.hex_centers = {}   # Współrzędne środków heksów (mapa)
        self.terrain_types = {} # Słownik typów terenu (jeśli zdefiniowano w pliku mapy)
        self.hex_defaults = {"defense_mod": 0, "move_mod": 0}  # Domyślne modyfikatory heksów (np. brak wpływu)
        self.map_scale = 2      # Skala wyświetlania mapy (2x powiększenie względem oryginalnego rozmiaru)

        self.selected_hex = None              # Aktualnie wybrany (kliknięty) heks
        self.selected_hex_highlight = None    # Obiekt podświetlenia wybranego heksu (np. zmieniony obrys)

        # Wczytaj obraz mapy
        try:
            self.map_image = Image.open(zasoby.MAP_PATH)
        except FileNotFoundError:
            messagebox.showerror("Błąd krytyczny", f"Nie znaleziono pliku mapy: {zasoby.MAP_PATH}")
            self.quit()
            return
        # Przeskaluj obraz mapy zgodnie z map_scale
        self.map_zoomed = self.map_image.resize((self.map_image.width * self.map_scale,
                                                 self.map_image.height * self.map_scale),
                                                 Image.LANCZOS)
        self.tk_map = ImageTk.PhotoImage(self.map_zoomed)
        # Wczytaj dane mapy z pliku (jeśli istnieje)
        map_data = loader.load_map_data(zasoby.MAP_DATA_PATH)
        if map_data:
            self.hex_data = map_data.get("hex_data", {})
            self.terrain_types = map_data.get("terrain_types", {})
            self.hex_defaults = map_data.get("hex_defaults", self.hex_defaults)
            self.hex_centers = map_data.get("hex_centers", {})
            # Jeśli plik mapy zawiera konfigurację (np. hex_size), zastosuj ją
            if "config" in map_data and "hex_size" in map_data["config"]:
                s = map_data["config"]["hex_size"]
                self.hex_size = s
                self.hex_width = 2 * s
                self.hex_height = math.sqrt(3) * s
                self.hex_horiz_offset = 1.5 * s
                self.hex_vert_offset = math.sqrt(3) * s
            else:
                # Parametry domyślne (pasujące do generate_hex_positions, gdy brak danych)
                self.hex_size = 30
                self.hex_width = 2 * 30
                self.hex_height = math.sqrt(3) * 30
                self.hex_horiz_offset = 1.5 * 30
                self.hex_vert_offset = math.sqrt(3) * 30
        else:
            # Brak pliku danych mapy - użyj ustawień domyślnych i wygeneruj siatkę heksów
            self.hex_size = 30
            self.hex_width = 2 * 30
            self.hex_height = math.sqrt(3) * 30
            self.hex_horiz_offset = 1.5 * 30
            self.hex_vert_offset = math.sqrt(3) * 30
            self.hex_centers = mapa.generate_hex_positions()

        # Tworzenie elementów interfejsu
        # Górny pasek stanu (informacja o turze i przyciski sterujące)
        self.top_bar = PasekStanu(self)
        self.top_bar.pack(side="top", fill="x")
        # Prawy panel informacji (o heksie i ekonomii)
        self.right_frame = ttk.Frame(self, width=250, style="Panel.TFrame")
        self.right_frame.pack(side="right", fill="y")
        # Podpanel informacji o heksie
        self.hex_info_frame = ttk.LabelFrame(self.right_frame, text="Informacje o heksie", style="MilitaryLabel.TLabelframe")
        self.hex_info_frame.pack(side="top", fill="x", padx=5, pady=5)
        self.hex_info_container = ttk.Frame(self.hex_info_frame, height=200, style="Panel.TFrame")
        self.hex_info_container.pack(fill="x", expand=True)
        self.hex_info_container.pack_propagate(False)
        self.hex_info_text = tk.Text(self.hex_info_container, wrap="word", state="disabled", bg="#E1DBC5", fg="#333333")
        self.hex_info_scrollbar = ttk.Scrollbar(self.hex_info_container, orient="vertical", command=self.hex_info_text.yview)
        self.hex_info_text.configure(yscrollcommand=self.hex_info_scrollbar.set)
        self.hex_info_scrollbar.pack(side="right", fill="y")
        self.hex_info_text.pack(side="left", fill="both", expand=True)
        # Wyświetl początkowy brak zaznaczenia heksu
        self.update_hex_info(None)
        # Podpanel informacji ekonomicznych
        self.economic_info_frame = ttk.LabelFrame(self.right_frame, text="Informacje ekonomiczne", style="MilitaryLabel.TLabelframe")
        self.economic_info_frame.pack(side="top", fill="x", padx=5, pady=5)
        self.economic_info_container = ttk.Frame(self.economic_info_frame, height=200, style="Panel.TFrame")
        self.economic_info_container.pack(fill="x", expand=True)
        self.economic_info_container.pack_propagate(False)
        self.economic_info_text = tk.Text(self.economic_info_container, wrap="word", state="disabled", bg="#E1DBC5", fg="#333333")
        self.economic_info_scrollbar = ttk.Scrollbar(self.economic_info_container, orient="vertical", command=self.economic_info_text.yview)
        self.economic_info_text.configure(yscrollcommand=self.economic_info_scrollbar.set)
        self.economic_info_scrollbar.pack(side="right", fill="y")
        self.economic_info_text.pack(side="left", fill="both", expand=True)
        # Wyświetl początkowy raport ekonomiczny dla startowej nacji
        self.update_economic_info()
        # Centralna część - obszar mapy (canvas)
        self.center_frame = ttk.Frame(self, style="Panel.TFrame")
        self.center_frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(self.center_frame, bg="black",
                                scrollregion=(0, 0, self.tk_map.width(), self.tk_map.height()))
        self.hbar = ttk.Scrollbar(self.center_frame, orient="horizontal", command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.hbar.pack(side="bottom", fill="x")
        self.vbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        # Umieść obraz mapy na canvasie
        self.map_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_map)
        # Narysuj obrysy siatki heksów (opcjonalnie ID heksów dla celów debug)
        if self.hex_centers:
            for hex_id, (cx, cy) in self.hex_centers.items():
                x = cx * self.map_scale
                y = cy * self.map_scale
                vertices = mapa.get_hex_vertices(x, y, self.hex_size * self.map_scale)
                self.canvas.create_polygon(vertices, outline="red", fill="", width=1, tags=f"hex_{hex_id}")
                # Debug: wyświetlanie ID heksu na mapie (zakomentowane w wersji końcowej)
                # self.canvas.create_text(x, y, text=hex_id, fill="blue", font=("Arial", 8))
        # Inicjalizacja panelu żetonów dla Niemiec
        self.german_panel = PanelGenerala(self, title="Żetony Niemieckie", nation="niemieckie", initial_x=1070, initial_y=500)

        # Ustal początkowy stan blokady: tura Polaka - niemieckie zablokowane
        self.german_tokens_locked = True
        self.german_panel.lock_tokens()
        # Wczytaj żetony z folderów
        _, german_tokens = loader.load_tokens_from_folder(zasoby.TOKENS_PATH)
        for token in german_tokens:
            self.german_panel.add_token(token)

        # Inicjalizacja panelu żetonów dla Polski
        self.polish_panel = PanelGenerala(self, title="Żetony Polskie", nation="polskie", initial_x=10, initial_y=500)

        # Ustal początkowy stan blokady: tura Niemiec - polskie zablokowane
        self.polish_tokens_locked = True
        self.polish_panel.lock_tokens()

        # Wczytaj żetony z folderów
        polish_tokens, _ = loader.load_tokens_from_folder(zasoby.TOKENS_PATH)
        for token in polish_tokens:
            self.polish_panel.add_token(token)

        # Zmienne do obsługi przeciągania żetonów
        self.current_dragging_token = None       # dane żetonu przeciąganego z panelu
        self.current_dragging_map_token = None   # dane żetonu przeciąganego z mapy
        self.token_preview = None                # obiekt podglądu przeciąganego żetonu
        # Powiązanie kliknięć myszy na canvasie mapy
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def update_token_locks(self):
        """Aktualizuje blokady paneli żetonów na podstawie aktualnej tury."""
        print(f"[INFO] Aktualizacja blokad żetonów dla: {self.current_turn_nation}")
        if self.current_turn_nation == "Polska":
            self.german_panel.lock_tokens()
            self.german_tokens_locked = True
            self.polish_panel.unlock_tokens()
            self.polish_tokens_locked = False
        else:
            self.german_panel.unlock_tokens()
            self.german_tokens_locked = False
            self.polish_panel.lock_tokens()
            self.polish_tokens_locked = True

    def update_economic_info(self):
        """Odświeża panel informacji ekonomicznych dla bieżącej nacji."""
        self.economic_info_text.config(state="normal")
        self.economic_info_text.delete("1.0", tk.END)
        report = self.economy_system.generate_report(self.current_turn_nation)
        self.economic_info_text.insert(tk.END, report)
        self.economic_info_text.config(state="disabled")

    def update_hex_info(self, hex_info):
        """
        Aktualizuje panel informacji o heksie.
        hex_info: słownik informacji o heksie (lub None jeśli brak wyboru).
        """
        self.hex_info_text.config(state="normal")
        self.hex_info_text.delete("1.0", tk.END)
        if not hex_info:
            self.hex_info_text.insert(tk.END, "Brak wybranego heksu.")
        else:
            # Wypisz dostępne informacje o heksie
            name = hex_info.get("nazwa", "Nieznany")
            terrain = hex_info.get("teren", "Nieznany")
            obj = hex_info.get("obiekty", "Brak")
            units = hex_info.get("jednostki", "Brak")
            info_text = (f"Nazwa: {name}\\n"
                         f"Teren: {terrain}\\n"
                         f"Obiekty: {obj}\\n"
                         f"Jednostki: {units}")
            self.hex_info_text.insert(tk.END, info_text)
        self.hex_info_text.config(state="disabled")

    # Obsługa zdarzeń mapy (kliknięcia myszą na canvasie)
    def on_canvas_press(self, event):
        """Reakcja na naciśnięcie przycisku myszy na mapie (zapamiętanie pozycji)."""
        self.click_start = (event.x, event.y)

    def on_canvas_release(self, event):
        """Reakcja na puszczenie przycisku myszy na mapie (obsługa kliknięcia w heks)."""
        if not hasattr(self, 'click_start'):
            return
        # Jeśli mysz nie została poruszona (to kliknięcie statyczne, nie przeciągnięcie)
        if (abs(event.x - self.click_start[0]) < 5) and (abs(event.y - self.click_start[1]) < 5):
            # Znajdź heks kliknięty przez gracza
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            clicked_hex = mapa.find_hex_at_position(canvas_x, canvas_y, self.hex_centers, self.map_scale, getattr(self, "hex_size", 30))
            if clicked_hex:
                self.selected_hex = clicked_hex
                # Podświetl wybrany heks (zmień kolor jego obrysu)
                if self.selected_hex_highlight:
                    self.canvas.itemconfig(self.selected_hex_highlight, outline="red")
                self.selected_hex_highlight = self.canvas.find_withtag(f"hex_{clicked_hex}")
                if self.selected_hex_highlight:
                    for item in self.selected_hex_highlight:
                        self.canvas.itemconfig(item, outline="yellow")
                # Zaktualizuj informacje o heksie w panelu
                hex_info = self.hex_data.get(clicked_hex, self.hex_defaults)
                self.update_hex_info(hex_info)
        # Wyczyść zapamiętaną pozycję kliknięcia
        self.click_start = None

    # Obsługa przeciągania żetonów z panelu na mapę
    def start_place_token(self, token):
        """Rozpoczyna proces przenoszenia żetonu z panelu na mapę."""
        if self.is_nation_locked(token.get("nation", "")):
            messagebox.showerror("Blokada", f"Żetony {token.get('nation', '')} są zablokowane w tej turze.")
            return
        if not self.is_turn_active(token.get("nation", "")):
            messagebox.showerror("Niewłaściwa tura", f"Nie jest teraz tura nacji: {token.get('nation', '')}")
            return
        self.current_dragging_token = token
        try:
            # Przygotuj podgląd obrazu żetonu do przeciągania na mapę
            img = Image.open(token["path"])
            token_size = getattr(self, "hex_size", 30) * self.map_scale * 1.5
            img = img.resize((int(token_size), int(token_size)), Image.LANCZOS)
            self.token_preview_img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Błąd inicjacji przeciągania tokena: {e}")

    def drag_place_token(self, event):
        """Aktualizuje pozycję podglądu żetonu podczas przeciągania."""
        if not self.current_dragging_token:
            return
        x = event.x
        y = event.y
        # Usuń poprzedni podgląd jeśli istnieje
        if self.token_preview:
            self.canvas.delete(self.token_preview)
        if hasattr(self, 'token_preview_img'):
            self.token_preview = self.canvas.create_image(x, y, image=self.token_preview_img, tags="token_preview")

    def place_token_on_hex(self, event):
        """Upuszczenie przeciąganego żetonu na mapę - umieszczenie go na heksie."""
        if not self.current_dragging_token:
            return
        # Usuń podgląd
        if self.token_preview:
            self.canvas.delete(self.token_preview)
            self.token_preview = None
        # Znajdź heks docelowy pod kursorem
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        target_hex = mapa.find_hex_at_position(canvas_x, canvas_y, self.hex_centers, self.map_scale, getattr(self, "hex_size", 30))
        if target_hex:
            # Sprawdź, czy docelowy heks jest wolny
            if target_hex in getattr(self, "placed_token_images", {}):
                self.show_hex_occupied_message(target_hex)
                # Zwróć żeton do panelu (ponieważ miejsce zajęte)
                token_nation = self.current_dragging_token.get("nation", "")
                if token_nation == "polskie":
                    self.polish_panel.add_token(self.current_dragging_token)
                elif token_nation == "niemieckie":
                    self.german_panel.add_token(self.current_dragging_token)
                self.current_dragging_token = None
                return
            # Umieść żeton na mapie
            try:
                img = Image.open(self.current_dragging_token["path"])
                token_size = getattr(self, "hex_size", 30) * self.map_scale * 1.5
                img = img.resize((int(token_size), int(token_size)), Image.LANCZOS)
                token_img = ImageTk.PhotoImage(img)
                if not hasattr(self, 'placed_token_images'):
                    self.placed_token_images = {}
                # Dodaj obraz żetonu na canvas
                image_id = self.canvas.create_image(self.hex_centers[target_hex][0] * self.map_scale,
                                                    self.hex_centers[target_hex][1] * self.map_scale,
                                                    image=token_img, tags=f"token_{target_hex}")
                self.placed_token_images[target_hex] = {
                    "image": token_img,
                    "image_id": image_id,
                    "token_data": self.current_dragging_token,
                    "hex_id": target_hex
                }
                # Powiąż możliwość podniesienia żetonu z mapy (przeciąganie z mapy)
                self.canvas.tag_bind(image_id, "<ButtonPress-1>", lambda e, hid=target_hex: self.start_drag_token_from_map(e, hid))
                # Aktualizuj dane heksu o umieszczonej jednostce
                self.hex_data.setdefault(target_hex, {})["jednostki"] = self.current_dragging_token["name"]
                print(f"Umieszczono {self.current_dragging_token['name']} na heksie {target_hex}")
                # Usuń żeton z panelu źródłowego
                if self.current_dragging_token["nation"] == "polskie":
                    self.polish_panel.remove_token_by_name(self.current_dragging_token["name"])
                else:
                    self.german_panel.remove_token_by_name(self.current_dragging_token["name"])
            except Exception as e:
                print(f"Błąd podczas umieszczania żetonu: {e}")
        else:
            print("Żaden heks nie został wybrany przy upuszczeniu żetonu.")
        # Zakończ przeciąganie
        self.current_dragging_token = None

    # Obsługa przeciągania żetonów z mapy z powrotem do panelu
    def start_drag_token_from_map(self, event, hex_id):
        """Rozpocznij przeciąganie żetonu już umieszczonego na mapie."""
        token_info = getattr(self, "placed_token_images", {}).get(hex_id)
        if not token_info:
            return
        nation = token_info["token_data"]["nation"]
        # Nie pozwól przeciągać, jeśli żetony tej nacji są zablokowane
        if self.is_nation_locked(nation):
            print(f"Żetony {nation} są zablokowane - nie można ich przesuwać.")
            # Aktualizuj informacje o heksie
            self.selected_hex = hex_id
            hex_data = self.hex_data.get(hex_id, self.hex_defaults)
            self.update_hex_info(hex_data)
            # (Opcjonalnie: podświetl heks lub pokaż komunikat)
            return "break"
        # Przygotuj dane żetonu do przeciągania
        self.current_dragging_map_token = {
            "name": token_info["token_data"]["name"],
            "path": token_info["token_data"]["path"],
            "nation": token_info["token_data"]["nation"],
            "hex_id": hex_id,
            "data": token_info["token_data"].get("data", {})
        }
        try:
            # Przygotuj podgląd obrazu
            img = Image.open(token_info["token_data"]["path"])
            token_size = getattr(self, "hex_size", 30) * self.map_scale * 1.5
            img = img.resize((int(token_size), int(token_size)), Image.LANCZOS)
            self.token_preview_img = ImageTk.PhotoImage(img)
            # Od razu pokaż podgląd w miejscu kliknięcia
            x, y = event.x, event.y
            self.token_preview = self.canvas.create_image(x, y, image=self.token_preview_img, tags="token_preview")
            # Powiąż ruch myszy i puszczenie przycisku do obsługi przenoszenia
            self.canvas.bind("<B1-Motion>", self.drag_map_token)
            self.canvas.bind("<ButtonRelease-1>", self.drop_map_token)
            print(f"Podjęto żeton {token_info['token_data']['name']} z heksu {hex_id}")
            return "break"
        except Exception as e:
            print(f"Błąd podczas przygotowania podglądu żetonu: {e}")
            self.current_dragging_map_token = None

    def drag_map_token(self, event):
        """Aktualizuje położenie podglądu podczas przeciągania żetonu z mapy."""
        if not self.current_dragging_map_token:
            return
        if self.token_preview:
            self.canvas.delete(self.token_preview)
        self.token_preview = self.canvas.create_image(event.x, event.y, image=self.token_preview_img, tags="token_preview")

    def drop_map_token(self, event):
        """Upuszczenie żetonu przeciąganego z mapy (może wrócić do panelu lub zostać przeniesiony na inny heks)."""
        if not self.current_dragging_map_token:
            return
        # Usuń podgląd
        if self.token_preview:
            self.canvas.delete(self.token_preview)
            self.token_preview = None
        token_nation = self.current_dragging_map_token["nation"]
        token_name = self.current_dragging_map_token["name"]
        # Sprawdź, czy upuszczono nad panelem dowódcy
        if token_nation == "polskie" and self.is_over_panel(self.polish_panel):
            if not self.polish_panel.token_exists(token_name):
                token_obj = {
                    "name": token_name,
                    "path": self.current_dragging_map_token["path"],
                    "nation": "polskie",
                    "data": self.current_dragging_map_token.get("data", {})
                }
                self.polish_panel.add_token(token_obj)
                print(f"Zwrócono żeton {token_name} do panelu polskiego")
            self.remove_token_from_map(self.current_dragging_map_token["hex_id"])
            self.current_dragging_map_token = None
            return
        # Sprawdź, czy upuszczono nad panelem generała
        elif token_nation == "niemieckie" and self.is_over_panel(self.german_panel):
            if not self.german_panel.token_exists(token_name):
                token_obj = {
                    "name": token_name,
                    "path": self.current_dragging_map_token["path"],
                    "nation": "niemieckie",
                    "data": self.current_dragging_map_token.get("data", {})
                }
                self.german_panel.add_token(token_obj)
                print(f"Zwrócono żeton {token_name} do panelu niemieckiego")
            self.remove_token_from_map(self.current_dragging_map_token["hex_id"])
            self.current_dragging_map_token = None
            return
        # Jeżeli upuszczono w innym miejscu mapy, spróbuj przenieść żeton na inny heks
        new_hex = mapa.find_hex_at_position(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y),
                                            self.hex_centers, self.map_scale, getattr(self, "hex_size", 30))
        old_hex = self.current_dragging_map_token["hex_id"]
        if new_hex and new_hex != old_hex:
            if new_hex in getattr(self, "placed_token_images", {}):
                self.show_hex_occupied_message(new_hex)
                # Jeżeli nowy heks jest zajęty, zwróć żeton do panelu macierzystego
                token_obj = {
                    "name": token_name,
                    "path": self.current_dragging_map_token["path"],
                    "nation": token_nation,
                    "data": self.current_dragging_map_token.get("data", {})
                }
                self.remove_token_from_map(old_hex)
                if token_nation == "polskie":
                    self.polish_panel.add_token(token_obj)
                else:
                    self.german_panel.add_token(token_obj)
                self.current_dragging_map_token = None
                return
            # Przenieś żeton na nowy heks (zwolnienie starego)
            self.remove_token_from_map(old_hex)
            # Przygotuj dane tak, aby można było użyć istniejącej funkcji place_token_on_hex
            self.current_dragging_token = {
                "name": token_name,
                "path": self.current_dragging_map_token["path"],
                "nation": token_nation,
                "data": self.current_dragging_map_token.get("data", {})
            }
            # Umieść żeton na nowym heksie
            dummy_event = type("Ev", (), {"x": event.x, "y": event.y})()  # tymczasowy obiekt event z polami x, y
            self.place_token_on_hex(dummy_event)
        # Zakończ operację
        self.current_dragging_map_token = None

    def remove_token_from_map(self, hex_id):
        """Usuwa żeton z mapy (canvas) i czyści informacje z hex_data."""
        if hex_id in getattr(self, "placed_token_images", {}):
            try:
                self.canvas.delete(self.placed_token_images[hex_id]["image_id"])
            except Exception as e:
                print(f"Błąd przy usuwaniu obrazu żetonu z heksu {hex_id}: {e}")
            # Usuń dane jednostki z heksu
            if hex_id in self.hex_data and "jednostki" in self.hex_data[hex_id]:
                del self.hex_data[hex_id]["jednostki"]
                if not self.hex_data[hex_id]:
                    del self.hex_data[hex_id]
            # Usuń z listy umieszczonych tokenów
            del self.placed_token_images[hex_id]
            if self.selected_hex == hex_id:
                self.update_hex_info(self.hex_data.get(hex_id, self.hex_defaults))
            print(f"Usunięto żeton z heksu {hex_id}")
            return True
        return False

    def is_over_panel(self, panel):
        """Sprawdza, czy kursor myszy jest aktualnie nad obszarem podanego panelu z żetonami."""
        if not hasattr(panel, 'frame'):
            return False
        px = panel.frame.winfo_x()
        py = panel.frame.winfo_y()
        pw = panel.frame.winfo_width()
        ph = panel.frame.winfo_height()
        # Pozycja kursora względem głównego okna
        cursor_x = self.winfo_pointerx() - self.winfo_rootx()
        cursor_y = self.winfo_pointery() - self.winfo_rooty()
        return (px <= cursor_x <= px + pw) and (py <= cursor_y <= py + ph)

    def show_hex_occupied_message(self, hex_id):
        """Wyświetla tymczasowy komunikat nad heksagonem informujący o zajętym polu (żeton wraca do panelu)."""
        if hex_id in self.hex_centers:
            cx, cy = self.hex_centers[hex_id]
            sx = cx * self.map_scale
            sy = cy * self.map_scale
            message_id = self.canvas.create_text(sx, sy - 20, text="Pole zajęte - żeton wraca", fill="red", font=("Arial", 12, "bold"))
            # Prostą metodą wywołujemy miganie tekstu (kilka razy)
            def flash(count=0):
                if count >= 6:
                    self.canvas.delete(message_id)
                    return
                self.canvas.itemconfig(message_id, state=("hidden" if count % 2 else "normal"))
                self.after(300, lambda c=count+1: flash(c))
            flash()

    def end_turn(self):
        """Kończy bieżącą turę: przetwarza ekonomię i przełącza na następną nację."""
        # Wykonaj działania końca tury (ekonomia) i przełącz gracza
        next_nation, next_player = tura.end_turn(self.economy_system, self.current_turn_nation,
                                                unit_count=len(getattr(self, "placed_token_images", {})),
                                                income=100, cost_per_unit=10)
        # Zapisz nowe wartości tury i nacji
        self.current_turn_nation = next_nation
        self.current_turn = next_player
        # Zaktualizuj blokady żetonów zgodnie z nową turą
        self.update_token_locks()
        # Zaktualizuj informacje ekonomiczne dla nowej nacji
        self.update_economic_info()
        # Zaktualizuj etykietę tury na pasku stanu
        if hasattr(self.top_bar, "update_turn_label"):
            self.top_bar.update_turn_label(self.current_turn_nation)

    def save_game(self):
        """Zapisuje stan gry do pliku (np. save_game.json) wraz z obrazami żetonów."""
        save_folder = os.path.join(os.getcwd(), "saves")
        os.makedirs(save_folder, exist_ok=True)
        save_file = os.path.join(save_folder, "save_game.json")
        # Zapisz informacje o rozstawieniu żetonów i hex_data
        placed_tokens_data = {}
        for hex_id, info in getattr(self, "placed_token_images", {}).items():
            token = info["token_data"]
            placed_tokens_data[hex_id] = {
                "name": token["name"],
                "nation": token["nation"],
                "path": token["path"]
            }
        game_state = {
            "current_turn": self.current_turn,
            "current_turn_nation": self.current_turn_nation,
            "hex_data": self.hex_data,
            "placed_tokens": placed_tokens_data
        }
        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Zapis gry", f"Gra została zapisana do pliku: {save_file}")
            print(f"[INFO] Gra zapisana w {save_file}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać gry: {e}")
            print(f"[BŁĄD] Nie udało się zapisać gry: {e}")

    def load_game(self) -> None:
        """Wczytuje stan gry z pliku zapisu."""
        save_file = os.path.join(os.getcwd(), "saves", "save_game.json")
        if not os.path.exists(save_file):
            messagebox.showerror("Błąd", f"Brak pliku zapisu: {save_file}")
            return

        try:
            with open(save_file, "r", encoding="utf-8") as f:
                game_state = json.load(f)

            self._clear_map()
            self._restore_turn_state(game_state)
            self._restore_hex_data(game_state)
            self._restore_tokens(game_state)
            self.update_token_locks()
            self.update_economic_info()

            messagebox.showinfo("Wczytano grę", "Stan gry został przywrócony z zapisu.")
            print(f"[INFO] Gra wczytana z {save_file}")
        except FileNotFoundError:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku zapisu: {save_file}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowy format pliku zapisu: {e}")
            print(f"[BŁĄD] Nieprawidłowy format pliku zapisu: {e}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas wczytywania gry: {e}")
            print(f"[BŁĄD] Błąd wczytywania gry: {e}")

    def _clear_map(self) -> None:
        """Czyści mapę z istniejących żetonów."""
        if hasattr(self, "placed_token_images"):
            for hex_id in list(self.placed_token_images.keys()):
                self.remove_token_from_map(hex_id)

    def _restore_turn_state(self, game_state: dict) -> None:
        """Przywraca stan tury z zapisanego stanu gry."""
        self.current_turn = game_state.get("current_turn", "Gracz 1")
        self.current_turn_nation = game_state.get("current_turn_nation", "Polska")
        self.top_bar.update_turn_label(self.current_turn_nation)

    def _restore_hex_data(self, game_state: dict) -> None:
        """Przywraca dane heksów z zapisanego stanu gry."""
        self.hex_data = game_state.get("hex_data", {})

    def _restore_tokens(self, game_state: dict) -> None:
        """Przywraca żetony na mapę z zapisanego stanu gry."""
        for hex_id, token_data in game_state.get("placed_tokens", {}).items():
            if hex_id in self.hex_centers:
                self._place_token_from_save(hex_id, token_data)

    def _place_token_from_save(self, hex_id: str, token_data: dict) -> None:
        """Umieszcza żeton na mapie na podstawie danych z zapisu."""
        self.current_dragging_token = {
            "name": token_data["name"],
            "path": token_data["path"],
            "nation": token_data["nation"],
            "data": {}
        }
        dummy_event = type("Ev", (), {
            "x": self.hex_centers[hex_id][0] * self.map_scale,
            "y": self.hex_centers[hex_id][1] * self.map_scale
        })()
        self.place_token_on_hex(dummy_event)

    def get_current_turn_nation(self):
        """Zwraca nazwę nacji, która ma aktualnie turę."""
        return self.current_turn_nation

if __name__ == '__main__':
    # Przykładowe nacje dla graczy
    player1_nation = "Polska"
    player2_nation = "Niemcy"

    # Tworzenie i uruchamianie głównego okna gry
    app = EkranGlowny(player1_nation, player2_nation)
    app.mainloop()
