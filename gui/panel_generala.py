import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_ekonomiczny import PanelEkonomiczny
from gui.panel_gracza import PanelGracza
from gui.zarzadzanie_punktami_ekonomicznymi import ZarzadzaniePunktamiEkonomicznymi
from model.mapa import Mapa
from gui.panel_mapa import PanelMapa
from model.zetony import ZetonyMapy
import os
import json
import shutil

class DraggableTokenLabel(tk.Label):
    def start_drag(self, event):
        self._drag_data = {'x': event.x, 'y': event.y}
        self.lift()
        self._dragging = True
        self._drag_window = None

    def do_drag(self, event):
        if not getattr(self, '_dragging', False):
            return
        # Przesuwanie labela w oknie rezerwy (opcjonalnie: ghost)
        # Można dodać efekt podążania kursora, ale uproszczone:
        x = self.winfo_pointerx() - self.winfo_rootx() - self._drag_data['x']
        y = self.winfo_pointery() - self.winfo_rooty() - self._drag_data['y']
        self.place(x=x, y=y)

    def do_drop(self, event):
        if not getattr(self, '_dragging', False):
            return
        self._dragging = False
        # Przekazanie token_meta do PanelMapa
        # Znajdź główne okno i PanelMapa
        root = self.winfo_toplevel()
        # PanelMapa jest przekazany przez master.master.panel_mapa
        try:
            panel_generala = root.panel_generala  # Dodaj referencję w __init__
            panel_mapa = panel_generala.panel_mapa
        except Exception:
            panel_mapa = None
        if panel_mapa:
            # Przekaż event i token_meta do drop
            # Przelicz globalne współrzędne kursora na lokalne PanelMapa
            x = self.winfo_pointerx() - panel_mapa.winfo_rootx()
            y = self.winfo_pointery() - panel_mapa.winfo_rooty()
            class DummyEvent:
                pass
            dummy_event = DummyEvent()
            dummy_event.x = x
            dummy_event.y = y
            panel_mapa.drop(dummy_event, self.token_meta)
        # Przywróć pozycję labela
        self.place_forget()
        self.pack(pady=2)

class PanelGenerala:
    def __init__(self, turn_number, ekonomia, gracz, gracze):
        self.turn_number = turn_number
        self.ekonomia = ekonomia
        self.gracz = gracz
        self.gracze = gracze

        # Tworzenie głównego okna
        self.root = tk.Tk()
        self.root.title(f"Panel Generała - {self.gracz.nacja}")
        self.root.state("zoomed")

        # Wyświetlanie numeru tury
        self.turn_label = tk.Label(self.root, text=f"Tura: {self.turn_number}", font=("Arial", 14), bg="lightgray")
        self.turn_label.pack(pady=5)

        # Główna ramka podziału
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel (przyciski)
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="olive")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)

        # Panel gracza
        panel_gracza = PanelGracza(self.left_frame, self.gracz.name, self.gracz.image_path)
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        minutes = self.gracz.czas
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {minutes}:00", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na ramkę z czasem jako przycisk zakończenia tury
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty ekonomiczne
        self.points_frame = tk.Label(self.left_frame, text="Punkty ekonomiczne: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)
        # Dodanie obsługi kliknięcia na "Punkty ekonomiczne" do otwierania suwaków wsparcia
        self.points_frame.bind("<Button-1>", lambda e: self.show_support_sliders())

        # Dodanie przycisku "Kup nowy żeton"
        self.buy_button = tk.Button(
            self.left_frame,
            text="Kup nowy żeton",
            font=("Arial", 12, "bold"),
            bg="#6B8E23",
            fg="white",
            command=self.buy_token
        )
        self.buy_button.pack(pady=5, fill=tk.X)

        # Dodanie sekcji raportu ekonomicznego
        self.economy_panel = PanelEkonomiczny(self.left_frame)
        self.economy_panel.pack_forget()
        self.economy_panel.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH, expand=False)
        self.economy_panel.config(width=300)  # Ustawia stałą szerokość panelu ekonomicznego na 300 pikseli

        # Panel pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack_forget()
        self.weather_panel.pack(side=tk.BOTTOM, pady=1, fill=tk.BOTH, expand=False)

        # Inicjalizacja suwaków wsparcia dowódców
        commanders = [gracz for gracz in self.gracze if gracz.nacja == self.gracz.nacja and gracz.rola == "Dowódca"]
        self.zarzadzanie_punktami_widget = ZarzadzaniePunktamiEkonomicznymi(
            self.left_frame,
            available_points=self.ekonomia.get_points()['economic_points'],
            commanders=[dowodca.numer for dowodca in commanders]
        )
        self.zarzadzanie_punktami_widget.pack_forget()  # Ukrycie suwaków na początku

        # Prawy panel (mapa)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Pobranie żetonów dla nacji generała
        zetony = ZetonyMapy()
        tokens_to_draw = zetony.get_tokens_for_nation(self.gracz.nacja)

        # Wczytaj wszystkie definicje z generated_by_general/index.json
        gen_index_path = os.path.join("assets", "tokens", "generated_by_general", "index.json")
        # upewnij się, że katalog istnieje
        os.makedirs(os.path.dirname(gen_index_path), exist_ok=True)
        # jeśli plik nie istnieje lub jest pusty, stwórz go z pustą listą
        if not os.path.exists(gen_index_path) or os.path.getsize(gen_index_path) == 0:
            with open(gen_index_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        # bezpieczne wczytanie JSONa
        with open(gen_index_path, 'r', encoding='utf-8') as f:
            try:
                all_defs = json.load(f)
            except json.JSONDecodeError:
                all_defs = []
        self._old_def_ids = [d['id'] for d in all_defs]

        # Wczytaj rozmieszczone żetony z placed_tokens.json
        placed_path = os.path.join("assets", "placed_tokens.json")
        placed_tokens = []
        if os.path.exists(placed_path):
            with open(placed_path, "r", encoding="utf-8") as f:
                try:
                    placed_tokens = json.load(f)
                except Exception:
                    placed_tokens = []
        # Dodaj rozmieszczone żetony do mapy i usuń z rezerwy
        placed_ids = {t['id'] for t in placed_tokens}
        tokens_to_draw += placed_tokens

        # Inicjalizacja modelu mapy i panelu mapy
        self.mapa_model = Mapa("assets/mapa_dane.json")
        self.panel_mapa = PanelMapa(
            parent=self.map_frame,
            map_model=self.mapa_model,
            bg_path="assets/mapa_globalna.jpg",
            player_nation=self.gracz.nacja,  # Przekazanie nacji gracza
            tokens_to_draw=tokens_to_draw,
            width=800, height=600
        )
        self.panel_mapa.pack(fill="both", expand=True)
        self.panel_mapa.bind_click_callback(self.on_map_click)

        # Usuń rozmieszczone żetony z rezerwy
        if hasattr(self, 'available_tokens'):
            self.available_tokens = [t for t in self.available_tokens if t['id'] not in placed_ids]
            self._render_available_tokens()

        # Przeliczenie czasu z minut na sekundy i zapisanie w zmiennej remaining_time
        self.remaining_time = self.gracz.czas * 60

        # Uruchomienie timera
        self.update_timer()

        # --- USUŃ stary reserve_frame (jeśli istnieje) ---
        if hasattr(self, 'reserve_frame'):
            self.reserve_frame.destroy()
            del self.reserve_frame
        # --- NOWA RAMKA REZERWY WEWNĄTRZ OKNA ---
        # ramka rezerwy po lewej stronie
        self.reserve_frame = tk.Frame(self.left_frame)
        self.reserve_frame.pack(side=tk.BOTTOM, fill="y", expand=False, pady=10)
        # ustawiamy w niej Canvas + Scrollbar
        self._reserve_canvas = tk.Canvas(self.reserve_frame, height=200)
        vsb = tk.Scrollbar(self.reserve_frame, orient="vertical", command=self._reserve_canvas.yview)
        self._reserve_inner = tk.Frame(self._reserve_canvas)
        self._reserve_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._reserve_canvas.pack(side="left", fill="both", expand=True)
        self._reserve_canvas.create_window((0,0), window=self._reserve_inner, anchor="nw")
        self._reserve_inner.bind("<Configure>", lambda e: self._reserve_canvas.configure(scrollregion=self._reserve_canvas.bbox("all")))
        # self.root.panel_generala = self  # NIEPOTRZEBNE już dla Toplevel

        # stan drag-&-drop
        self.current_drag_token = None
        self.drag_preview = None

    def start_drag(self, event, token):
        parent = self.winfo_toplevel()
        self.current_drag_token = token
        img = event.widget.image
        self.drag_preview = tk.Label(parent, image=img, borderwidth=0)
        self.drag_preview.image = img
        parent.bind("<Motion>", self.on_drag_motion)
        parent.bind("<ButtonRelease-1>", self.on_drag_release)

    def on_drag_motion(self, event):
        if self.drag_preview:
            self.drag_preview.place(x=event.x, y=event.y)

    def on_drag_release(self, event):
        if not self.current_drag_token:
            return
        canvas = self.panel_mapa.canvas
        x = event.x - canvas.winfo_x()
        y = event.y - canvas.winfo_y()
        q, r = self.panel_mapa.coords_to_hex(x, y)
        self.on_map_click(q, r, self.current_drag_token)
        self.drag_preview.destroy()
        self.drag_preview = None
        self.current_drag_token = None
        parent = self.winfo_toplevel()
        parent.unbind("<Motion>")
        parent.unbind("<ButtonRelease-1>")

    def on_map_click(self, q, r, token_meta=None):
        # --- WARUNEK SPAWN-HEKS ---
        tile = self.panel_mapa.map_model.get_tile(q, r)
        import tkinter.messagebox as messagebox
        if not hasattr(self, 'gracz') or not hasattr(self.gracz, 'nacja'):
            nation = getattr(self, 'nation', None)
        else:
            nation = self.gracz.nacja
        if not hasattr(tile, 'spawn_nation') or tile.spawn_nation != nation:
            messagebox.showwarning('Nie możesz tu postawić', 'Możesz wystawiać żetony tylko na własnych spawn-heksach.')
            return
        # --- KONIEC WARUNKU ---
        # Tryb deploy przez drag & drop lub kliknięcie na rezerwę
        if token_meta:
            token_meta['q'], token_meta['r'] = q, r
            if not hasattr(self, 'start_tokens'):
                self.start_tokens = []
            self.start_tokens.append(token_meta)
            # usuń z rezerwy
            if hasattr(self, 'available_tokens'):
                self.available_tokens = [t for t in self.available_tokens if t['id'] != token_meta['id']]
                self._render_available_tokens()
            if hasattr(self, 'panel_mapa'):
                self.panel_mapa.add_token(token_meta)
                self.panel_mapa.save_placed_token(token_meta)
            # zachowaj w stanie gry
            try:
                import game_state
                if hasattr(game_state, 'placed_tokens'):
                    game_state.placed_tokens.append(token_meta)
                    game_state.save_state()
            except ImportError:
                pass
            messagebox.showinfo("Rozmieszczono", f"Żeton {token_meta['id']} na ({q},{r})")
            return
        # --- ELSE: klik poza trybem deploy ---
        # Sprawdź, czy na tym hexie stoi żeton
        if hasattr(self.panel_mapa.map_model, 'get_token_at'):
            token = self.panel_mapa.map_model.get_token_at(q, r)
            if token:
                info = '\n'.join(f"{k}: {v}" for k, v in token.items() if k not in ('q', 'r'))
                messagebox.showinfo('Właściwości jednostki', info)
                return
        # Oryginalne zachowanie: info o heksie
        tile = self.mapa_model.get_tile(q, r)
        additional_info = f"\nSpawn: {tile.spawn_nation}" if tile.spawn_nation else ""
        tk.messagebox.showinfo(
            "Płytka",
            f"Hex: ({q},{r})\nTyp: {tile.terrain_key}\nRuch: {tile.move_mod}\nObrona: {tile.defense_mod}{additional_info}"
        )

    def update_weather(self, weather_report):
        self.weather_panel.update_weather(weather_report)

    def update_economy(self, points=None):
        """Aktualizuje sekcję raportu ekonomicznego w panelu."""
        if points is None:
            points = self.ekonomia.get_points()['economic_points']
        special_points = self.ekonomia.get_points()['special_points']

        # Aktualizacja tekstu w panelu ekonomicznym
        economy_report = f"Punkty ekonomiczne: {points}\nPunkty specjalne: {special_points}"
        self.economy_panel.update_economy(economy_report)

        # Aktualizacja tekstu w sekcji punktów ekonomicznych
        self.points_frame.config(text=f"Punkty ekonomiczne: {points}")

    def zarzadzanie_punktami(self, available_points):
        """Zarządza punktami ekonomicznymi i aktualizuje interfejs."""
        if not hasattr(self, 'zarzadzanie_punktami_widget'):
            # Inicjalizacja widgetu zarządzania punktami, jeśli nie istnieje
            self.zarzadzanie_punktami_widget = ZarzadzaniePunktamiEkonomicznymi(
                self.left_frame,
                available_points=available_points,
                commanders=[gracz.numer for gracz in self.gracze if gracz.nacja == self.gracz.nacja and gracz.rola == "Dowódca"]
            )
            self.zarzadzanie_punktami_widget.pack(pady=10, fill=tk.BOTH, expand=False)
        else:
            # Aktualizacja dostępnych punktów w istniejącym widgetcie
            self.zarzadzanie_punktami_widget.refresh_available_points(available_points)

    def show_support_sliders(self):
        """Wyświetla suwaki do zarządzania punktami wsparcia dowódców."""
        # Ukrycie klawisza "Wsparcie dowódców"
        if hasattr(self, 'support_button'):
            self.support_button.pack_forget()

        # Resetowanie wartości suwaków do 0 przy każdym otwarciu sekcji
        if hasattr(self, 'zarzadzanie_punktami_widget'):
            for commander in self.zarzadzanie_punktami_widget.commander_points.keys():
                slider = getattr(self.zarzadzanie_punktami_widget, f"{commander}_slider", None)
                if slider:
                    slider.set(0)
                self.zarzadzanie_punktami_widget.commander_points[commander] = 0

            # Wyświetlenie suwaków
            self.zarzadzanie_punktami_widget.pack(pady=10, fill=tk.BOTH, expand=False)

        # Dodanie przycisku "Akceptuj" tylko raz
        if not hasattr(self, 'accept_button'):
            self.accept_button = tk.Button(self.zarzadzanie_punktami_widget, text="Akceptuj", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", command=self.accept_support)
            self.accept_button.pack(pady=10, fill=tk.BOTH, expand=False)

    def accept_support(self):
        """Akceptuje przydzielone punkty wsparcia i aktualizuje ekonomię."""
        # Przekazanie punktów do dowódców
        for commander_id, pts in self.zarzadzanie_punktami_widget.commander_points.items():
            if pts > 0:
                for player in self.gracze:  # Iteracja po liście graczy
                    if player.numer == commander_id and player.rola == "Dowódca":
                        player.economy.economic_points += pts

        # Aktualizacja raportu ekonomicznego po rozdysponowaniu punktów
        self.ekonomia.subtract_points(sum(self.zarzadzanie_punktami_widget.commander_points.values()))
        self.update_economy()

        # Ukrycie suwaków
        self.zarzadzanie_punktami_widget.pack_forget()

        # Przywrócenie klawisza "Wsparcie dowódców"
        if hasattr(self, 'support_button'):
            self.support_button.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

    def update_timer(self):
        """Aktualizuje odliczanie czasu."""
        if self.root.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                minutes = self.remaining_time // 60
                seconds = self.remaining_time % 60
                self.timer_frame.config(text=f"Pozostały czas: {minutes}:{seconds:02d}")
                self.timer_id = self.root.after(1000, self.update_timer)
            else:
                self.end_turn()  # Automatyczne zakończenie tury po upływie czasu

    def reset_support_sliders(self):
        """Resetuje suwaki wsparcia dowódców po zakończeniu tury."""
        if hasattr(self, 'zarzadzanie_punktami_widget'):
            for commander in self.zarzadzanie_punktami_widget.commander_points.keys():
                slider = getattr(self.zarzadzanie_punktami_widget, f"{commander}_slider", None)
                if slider:
                    slider.set(0)
                self.zarzadzanie_punktami_widget.commander_points[commander] = 0

    def end_turn(self):
        """Kończy podturę i zamyka panel."""
        self.reset_support_sliders()  # Resetowanie suwaków wsparcia
        self.destroy()  # Zamiast self.root.destroy()

    def confirm_end_turn(self, event=None):
        """Potwierdza zakończenie tury."""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zakończyć turę przed czasem?"):
            self.end_turn()

    def destroy(self):
        """Anuluje timer i niszczy okno."""
        if hasattr(self, 'timer_id') and self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None  # Resetowanie identyfikatora timera
            except Exception as e:
                print(f"[ERROR] Nie udało się anulować timera: {e}")
        self.root.destroy()

    def buy_token(self):
        """Otwiera edytor żetonu w nowym oknie."""
        import sys
        import os
        from pathlib import Path
        # Dodaj katalog edytory do sys.path jeśli nie ma go na liście
        edytory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../edytory'))
        if edytory_path not in sys.path:
            sys.path.append(edytory_path)
        import importlib
        token_editor_prototyp = importlib.import_module('token_editor_prototyp')

        # 1) Ustawiamy osobny katalog dla nowych żetonów:
        token_editor_prototyp.TOKENS_ROOT = Path("assets/tokens/generated_by_general")
        token_editor_prototyp.TOKENS_ROOT.mkdir(parents=True, exist_ok=True)
        # 2) Uruchamiamy edytor w nowym oknie:
        win = tk.Toplevel(self.root)
        win.title("Edytor żetonów")
        editor = token_editor_prototyp.TokenEditor(win)
        win.grab_set()
        win.wait_window()
        # 3) Po zamknięciu okna – weryfikacja ekonomii:
        self._finalize_purchase()

    def _finalize_purchase(self):
        """Weryfikuje ekonomię po zakupie żetonu."""
        # 1) Wczytaj wszystkie nowe wpisy z katalogu generated_by_general
        gen_root = "assets/tokens/generated_by_general"
        index_path = os.path.join(gen_root, "index.json")
        with open(index_path, encoding="utf-8") as f:
            all_defs = json.load(f)
        # 2) Pobierz ID nowych żetonów (np. porównując z wcześniejszą listą w self._old_def_ids)
        new_defs = [t for t in all_defs if t["id"] not in getattr(self, "_old_def_ids", [])]
        total_cost = sum(int(d.get("price", 0)) for d in new_defs)
        # Zadbajmy, by _old_def_ids rosło o nowe tokeny
        self._old_def_ids.extend(d['id'] for d in new_defs)
        pts = self.ekonomia.get_points()['economic_points']
        if total_cost > pts:
            tk.messagebox.showwarning("Brak punktów", f"Potrzebujesz {total_cost}, masz {pts}.")
            # usuń katalog z nowymi żetonami
            for d in new_defs:
                shutil.rmtree(os.path.join(gen_root, d["nation"], d["id"]), ignore_errors=True)
            # --- AKTUALIZACJA INDEX.JSON ---
            gen_index_path = os.path.join(gen_root, "index.json")
            with open(gen_index_path, encoding="utf-8") as f:
                all_defs = json.load(f)
            valid_defs = []
            for d in all_defs:
                path = os.path.join(gen_root, d['nation'], d['id'])
                if os.path.isdir(path):
                    valid_defs.append(d)
            with open(gen_index_path, 'w', encoding="utf-8") as f:
                json.dump(valid_defs, f, indent=2, ensure_ascii=False)
            return
        # 3) Odejmij punkty i odśwież UI
        self.ekonomia.subtract_points(total_cost)
        self.update_economy()
        self.zarzadzanie_punktami(self.ekonomia.get_points()['economic_points'])
        tk.messagebox.showinfo("Zakup udany", f"Kupiono {len(new_defs)} żeton(ów) za {total_cost} pkt.")
        # 4) Zaktualizuj pulę dostępnych żetonów
        self.available_tokens = new_defs
        self._old_def_ids = [d["id"] for d in all_defs]
        self._render_available_tokens()
        # --- Zapisz stan rozmieszczonych żetonów ---
        try:
            import game_state
            game_state.save_state()
        except ImportError:
            pass

    def _render_available_tokens(self):
        """Rysuje miniaturki kupionych żetonów w panelu rezerwy (lewa ramka)."""
        # Czyść zawartość ramki rezerwy
        for widget in self._reserve_inner.winfo_children():
            widget.destroy()
        if not hasattr(self, 'available_tokens') or not self.available_tokens:
            label = tk.Label(self._reserve_inner, text="Brak żetonów w rezerwie", bg='lightgray')
            label.pack(pady=10)
            return
        for token in self.available_tokens:
            img_path = os.path.join('assets/tokens/generated_by_general', token['nation'], token['id'], 'token.png')
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((64, 64))
                photo = ImageTk.PhotoImage(img)
                lbl = DraggableTokenLabel(self._reserve_inner, image=photo, cursor="hand2")
                lbl.image = photo
                lbl.token_meta = token  # zachowaj dane tokena
                lbl.pack(pady=2)
                lbl.bind("<ButtonPress-1>", lambda e, t=token: self.start_drag(e, t))
            else:
                lbl = tk.Label(self._reserve_inner, text=token['id'], bg='lightgray')
                lbl.pack(pady=2)

    def _start_placing_token(self, token):
        self.placing_token = token
        tk.messagebox.showinfo("Rozmieszczanie", f"Kliknij na mapę, aby rozmieścić żeton: {token['id']}")

    def mainloop(self):
        self.root.mainloop()
