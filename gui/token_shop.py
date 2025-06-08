import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os
from pathlib import Path
from PIL import ImageFont
from edytory.token_editor_prototyp import create_flag_background
import traceback

class TokenShop(tk.Toplevel):
    def __init__(self, parent, ekonomia, dowodcy, on_purchase_callback=None, nation=None):
        super().__init__(parent)
        # --- INICJALIZACJA ZMIENNYCH STANU (musi być przed budową GUI!) ---
        if nation is not None:
            self.nation = tk.StringVar(value=nation)
        else:
            self.nation = tk.StringVar(value="Polska")
        self.unit_type = tk.StringVar(value="P")
        self.unit_size = tk.StringVar(value="Pluton")
        self.selected_supports = set()
        self.selected_transport = tk.StringVar(value="")
        self.transport_types = ["przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski"]
        self.support_upgrades = {
            "drużyna granatników": {"movement": -1, "range": 1, "attack": 2, "combat": 0, "unit_maintenance": 1, "purchase": 10, "defense": 1},
            "sekcja km.ppanc": {"movement": -1, "range": 1, "attack": 2, "combat": 0, "unit_maintenance": 2, "purchase": 10, "defense": 2},
            "sekcja ckm": {"movement": -1, "range": 1, "attack": 2, "combat": 0, "unit_maintenance": 2, "purchase": 10, "defense": 2},
            "przodek dwukonny": {"movement": 2, "range": 0, "attack": 0, "combat": 0, "unit_maintenance": 1, "purchase": 5, "defense": 0},
            "sam. ciezarowy Fiat 621": {"movement": 5, "range": 0, "attack": 0, "combat": 0, "unit_maintenance": 3, "purchase": 8, "defense": 0},
            "sam.ciezarowy Praga Rv": {"movement": 5, "range": 0, "attack": 0, "combat": 0, "unit_maintenance": 3, "purchase": 8, "defense": 0},
            "ciagnik altyleryjski": {"movement": 3, "range": 0, "attack": 0, "combat": 0, "unit_maintenance": 4, "purchase": 12, "defense": 0},
            "obserwator": {"movement": 0, "range": 0, "attack": 0, "combat": 0, "unit_maintenance": 1, "purchase": 5, "defense": 0}
        }
        self.allowed_support = {
            "P": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"],
            "K": ["sekcja ckm"],
            "TC": ["obserwator"],
            "TŚ": ["obserwator"],
            "TL": ["obserwator"],
            "TS": ["obserwator"],
            "AC": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski", "obserwator"],
            "AL": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc", "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski", "obserwator"],
            "AP": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc", "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski", "obserwator"],
            "Z": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "obserwator"],
            "D": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"],
            "G": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"]
        }
        # Lista typów jednostek jak w starym edytorze
        self.unit_type_order = [
            ("Piechota (P)", "P", True),
            ("Kawaleria (K)", "K", False),
            ("Czołg ciężki (TC)", "TC", True),
            ("Czołg średni (TŚ)", "TŚ", False),
            ("Czołg lekki (TL)", "TL", False),
            ("Sam. pancerny (TS)", "TS", False),
            ("Artyleria ciężka (AC)", "AC", True),
            ("Artyleria lekka (AL)", "AL", False),
            ("Artyleria plot (AP)", "AP", True),
            ("Zaopatrzenie (Z)", "Z", False),
            ("Dowództwo (D)", "D", False),
            ("Generał (G)", "G", False)
        ]
        self.unit_type_map = {v: k for k, v, _ in self.unit_type_order}
        self.unit_type_reverse_map = {k: v for v, k, _ in self.unit_type_order}
        self.unit_type_display = tk.StringVar(value=self.unit_type_reverse_map[self.unit_type.get()])
        self._last_valid_unit_type = self.unit_type_display.get()

        # --- USTAWIENIA OKNA ---
        self.title("Zakup nowych jednostek")
        self.geometry("800x600")
        self.configure(bg="darkolivegreen")
        self.ekonomia = ekonomia
        self.dowodcy = dowodcy
        self.on_purchase_callback = on_purchase_callback
        self.selected_commander = tk.StringVar()
        self.points_var = tk.IntVar(value=self.ekonomia.get_points()['economic_points'])

        # --- Nagłówek w ramce ---
        header_frame = tk.Frame(self, bg="olivedrab", bd=5, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text="SKLEP GENERAŁA – Zakup nowych jednostek", bg="olivedrab", fg="white", font=("Arial", 20, "bold"))
        header_label.pack(pady=10)

        # --- Główne kontenery ---
        main_container = tk.Frame(self, bg="darkolivegreen")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Lewy panel: formularz wyboru
        self.control_frame = tk.Frame(main_container, bg="darkolivegreen")
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Prawy panel: podgląd/statystyki
        self.preview_frame = tk.Frame(main_container, bd=2, relief=tk.RIDGE, bg="darkolivegreen")
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Punkty ekonomiczne ---
        points_box = tk.Frame(self.control_frame, bg="olivedrab", bd=3, relief=tk.GROOVE)
        points_box.pack(fill=tk.X, pady=5)
        self.points_label = tk.Label(points_box, text=f"Dostępne punkty ekonomiczne: {self.points_var.get()}", font=("Arial", 13, "bold"), bg="olivedrab", fg="white")
        self.points_label.pack(pady=5)

        # --- Dowódca ---
        commander_box = tk.Frame(self.control_frame, bg="darkolivegreen")
        commander_box.pack(fill=tk.X, pady=5)
        tk.Label(commander_box, text="Wybierz dowódcę:", bg="darkolivegreen", fg="white", font=("Arial", 12, "bold")).pack(anchor="w")
        dowodcy_ids = [str(d.id) for d in self.dowodcy]
        if dowodcy_ids:
            self.selected_commander.set(dowodcy_ids[0])
        tk.OptionMenu(commander_box, self.selected_commander, *dowodcy_ids).pack(anchor="w", pady=2)

        # --- Formularz wyboru jednostki ---
        form_box = tk.Frame(self.control_frame, bg="darkolivegreen", bd=2, relief=tk.GROOVE)
        form_box.pack(fill=tk.BOTH, expand=True, pady=5)
        # Nacja (tylko label, bez wyboru)
        tk.Label(form_box, text="Nacja:", bg="darkolivegreen", fg="white", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(form_box, textvariable=self.nation, bg="darkolivegreen", fg="white", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w", pady=2)
        # Typ jednostki (pełna nazwa w OptionMenu) – tylko aktywne typy
        tk.Label(form_box, text="Typ jednostki:", bg="darkolivegreen", fg="white", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=2)
        # Lista tylko aktywnych typów
        active_unit_types = [name for name, _, active in self.unit_type_order if active]
        unit_type_menu = tk.OptionMenu(form_box, self.unit_type_display, *active_unit_types)
        unit_type_menu.grid(row=1, column=1, sticky="w", pady=2)
        # Synchronizacja wyboru pełnej nazwy z logiką (skrót)
        def on_unit_type_change(*_):
            val = self.unit_type_display.get()
            # Ustaw kod typu na podstawie pełnej nazwy
            for name, code, active in self.unit_type_order:
                if name == val:
                    self.unit_type.set(code)
                    self._last_valid_unit_type = val
                    self.update_stats()
                    break
        self.unit_type_display.trace_add('write', on_unit_type_change)
        # Wielkość
        tk.Label(form_box, text="Wielkość:", bg="darkolivegreen", fg="white", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=2)
        tk.OptionMenu(form_box, self.unit_size, "Pluton", "Kompania", "Batalion").grid(row=2, column=1, sticky="w", pady=2)
        # Nazwa (usunięcie pola edytowalnego, automatyczna generacja)
        tk.Label(form_box, text="Nazwa jednostki:", bg="darkolivegreen", fg="white", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=2)
        self.unit_label_var = tk.StringVar()
        self.unit_full_name_var = tk.StringVar()
        tk.Label(form_box, textvariable=self.unit_label_var, bg="darkolivegreen", fg="yellow", font=("Arial", 11, "bold")).grid(row=3, column=1, sticky="w", pady=2)
        # --- Wsparcie (w tym transport jako radio, z walidacją allowed_support) ---
        tk.Label(form_box, text="Wsparcie:", bg="darkolivegreen", fg="white", font=("Arial", 11)).grid(row=4, column=0, sticky="nw", pady=2)
        self.support_vars = {}
        support_frame = tk.Frame(form_box, bg="darkolivegreen")
        support_frame.grid(row=4, column=1, sticky="w", pady=2)
        # Słownik allowed_support jak w TokenEditor
        self.allowed_support = {
            "P": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"],
            "K": ["sekcja ckm"],
            "TC": ["obserwator"],
            "TŚ": ["obserwator"],
            "TL": ["obserwator"],
            "TS": ["obserwator"],
            "AC": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski", "obserwator"],
            "AL": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc", "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski", "obserwator"],
            "AP": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc", "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski", "obserwator"],
            "Z": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "obserwator"],
            "D": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"],
            "G": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"]
        }
        self.transport_types = ["przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "ciagnik altyleryjski"]
        def update_support_state(*_):
            ut = self.unit_type.get()
            allowed = self.allowed_support.get(ut, [])
            # Resetuj niedozwolone wsparcia i transporty
            for sup, var in self.support_vars.items():
                if sup not in allowed:
                    var.set(0)
            # Jeśli wybrany transport nie jest już dozwolony, odznacz go
            for t in self.transport_types:
                if t not in allowed and self.support_vars[t].get():
                    self.support_vars[t].set(0)
            # Dezaktywuj niedozwolone wsparcia/transporty
            for i, sup in enumerate(self.support_upgrades.keys()):
                cb = self.support_checkbuttons[sup]
                if sup in allowed:
                    cb.config(state="normal")
                else:
                    cb.config(state="disabled")
        self.support_checkbuttons = {}
        for i, sup in enumerate(self.support_upgrades.keys()):
            var = tk.IntVar()
            def make_cmd(sup=sup, var=var):
                def cmd():
                    # Transporty jako radio
                    if sup in self.transport_types:
                        # Jeśli kliknięto już wybrany transport, odznacz
                        if var.get():
                            # Odznacz wszystkie inne transporty
                            for t in self.transport_types:
                                if t != sup and t in self.support_vars:
                                    self.support_vars[t].set(0)
                    self.update_stats()
                return cmd
            cb = tk.Checkbutton(support_frame, text=sup, variable=var, command=make_cmd(), bg="darkolivegreen", fg="white", selectcolor="olivedrab", font=("Arial", 10))
            cb.grid(row=i//2, column=i%2, sticky="w")
            self.support_vars[sup] = var
            self.support_checkbuttons[sup] = cb
        # Automatyczna walidacja wsparcia przy zmianie typu jednostki
        self.unit_type.trace_add('write', update_support_state)
        update_support_state()

        # --- Przycisk kupna ---
        self.buy_btn = tk.Button(self.control_frame, text="Kup jednostkę", command=self.buy_unit, font=("Arial", 13, "bold"), bg="#6B8E23", fg="white", bd=3, relief=tk.RAISED)
        self.buy_btn.pack(pady=10)
        self.info_label = tk.Label(self.control_frame, text="", fg="red", bg="darkolivegreen", font=("Arial", 11, "bold"))
        self.info_label.pack()

        # --- Prawy panel: podgląd flagi i statystyki ---
        preview_title = tk.Label(self.preview_frame, text="Podgląd i statystyki jednostki", bg="olivedrab", fg="white", font=("Arial", 15, "bold"))
        preview_title.pack(fill=tk.X, pady=5)
        # Podgląd flagi
        self.flag_canvas = tk.Canvas(self.preview_frame, width=120, height=120, bg="dimgray", bd=2, relief=tk.SUNKEN)
        self.flag_canvas.pack(pady=10)
        self.flag_img = None
        # Przycisk zapisu podglądu jako PNG
        save_btn = tk.Button(self.preview_frame, text="Zapisz podgląd jako PNG", command=self.save_token_preview_as_png, font=("Arial", 10), bg="#556B2F", fg="white")
        save_btn.pack(pady=2)
        # Statystyki
        stats_box = tk.Frame(self.preview_frame, bg="darkolivegreen", bd=2, relief=tk.GROOVE)
        stats_box.pack(fill=tk.BOTH, expand=True, pady=5)
        self.stats_labels = {}
        stats_names = ["Ruch", "Zasięg ataku", "Siła ataku", "Wartość bojowa", "Obrona", "Utrzymanie", "Cena", "Zasięg widzenia"]
        for i, stat in enumerate(stats_names):
            tk.Label(stats_box, text=stat+":", bg="darkolivegreen", fg="white", font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="e", pady=2, padx=5)
            lbl = tk.Label(stats_box, text="0", width=10, anchor="w", bg="darkolivegreen", fg="white", font=("Arial", 12))
            lbl.grid(row=i, column=1, sticky="w", pady=2)
            self.stats_labels[stat] = lbl

        # --- Automatyczna aktualizacja statystyk i flagi oraz nazw ---
        def update_all(*_):
            self.update_stats()
            self.update_token_preview()
            self.update_unit_names()
        self.nation.trace_add('write', update_all)
        self.unit_type.trace_add('write', update_all)
        self.unit_size.trace_add('write', update_all)
        self.selected_commander.trace_add('write', update_all)
        self.update_unit_names()
        self.update_stats()

    def update_unit_names(self):
        # Generuje label i unit_full_name jak w TokenEditor, z dodanym słowem 'nowy'
        nation = self.nation.get()
        unit_type = self.unit_type.get()
        unit_size = self.unit_size.get()
        dowodca_id = self.selected_commander.get()
        nation_short = "PL" if nation == "Polska" else ("N" if nation == "Niemcy" else nation[:2].upper())
        label = f"nowy_{dowodca_id}_{nation_short}_{unit_type}_{unit_size}"
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
        self.unit_label_var.set(label)
        self.unit_full_name_var.set(unit_full_name)

    def update_stats(self):
        # Pełna logika jak w update_numeric_fields z token_editor_prototyp.py
        ut = self.unit_type.get()
        size = self.unit_size.get()
        # Domyślne wartości (pełne, jak w edytorze)
        defaults = {
            "ruch": {
                "P": 5, "K": 16, "TC": 18, "TŚ": 20, "TL": 22, "TS": 24,
                "AC": 12, "AL": 14, "AP": 16, "Z": 20, "D": 16, "G": 16
            },
            "range": {
                "P": 1, "K": 1, "TC": 3, "TŚ": 3, "TL": 2, "TS": 2,
                "AC": 6, "AL": 4, "AP": 4, "Z": 1, "D": 0, "G": 0
            },
            "attack": {
                "Pluton": {"P": 2, "K": 3, "TC": 6, "TŚ": 5, "TL": 4, "TS": 3, "AC": 6, "AL": 4, "AP": 3, "Z": 1, "D": 0, "G": 0},
                "Kompania": {"P": 4, "K": 6, "TC": 10, "TŚ": 8, "TL": 7, "TS": 6, "AC": 9, "AL": 7, "AP": 6, "Z": 2, "D": 0, "G": 0},
                "Batalion": {"P": 8, "K": 9, "TC": 18, "TŚ": 15, "TL": 12, "TS": 10, "AC": 12, "AL": 10, "AP": 9, "Z": 3, "D": 0, "G": 0}
            },
            "combat": {"P__Pluton": 8, "P__Kompania": 24, "P__Batalion": 48, "AC__Pluton": 6, "AC__Kompania": 18, "AC__Batalion": 36, "TC__Pluton": 10, "TC__Kompania": 30, "TC__Batalion": 60, "AL__Pluton": 7, "AL__Kompania": 21, "AL__Batalion": 42, "AP__Pluton": 5, "AP__Kompania": 15, "AP__Batalion": 30},
            "unit_maintenance": {
                "Pluton": {"P": 2, "K": 3, "TC": 5, "TŚ": 4, "TL": 3, "TS": 2, "AC": 3, "AL": 3, "AP": 3, "Z": 2, "D": 0, "G": 0},
                "Kompania": {"P": 4, "K": 6, "TC": 10, "TŚ": 8, "TL": 6, "TS": 5, "AC": 6, "AL": 6, "AP": 6, "Z": 4, "D": 0, "G": 0},
                "Batalion": {"P": 8, "K": 9, "TC": 15, "TŚ": 12, "TL": 10, "TS": 8, "AC": 12, "AL": 10, "AP": 9, "Z": 6, "D": 0, "G": 0}
            },
            "purchase": {
                "Pluton": {"P": 18, "K": 20, "TC": 24, "TŚ": 22, "TL": 20, "TS": 18, "AC": 22, "AL": 20, "AP": 18, "Z": 16, "D": 60, "G": 60},
                "Kompania": {"P": 36, "K": 40, "TC": 48, "TŚ": 44, "TL": 40, "TS": 36, "AC": 44, "AL": 40, "AP": 36, "Z": 32, "D": 60, "G": 60},
                "Batalion": {"P": 54, "K": 60, "TC": 72, "TŚ": 66, "TL": 60, "TS": 54, "AC": 66, "AL": 60, "AP": 54, "Z": 48, "D": 60, "G": 60}
            },
            "sight": {"P": 3, "K": 3, "TC": 2, "TŚ": 2, "TL": 2, "TS": 3, "AC": 3, "AL": 3, "AP": 3, "D": 4, "G": 4, "Z": 2}
        }
        # Domyślne wartości
        ruch = int(defaults["ruch"].get(ut, 0))
        zasieg = int(defaults["range"].get(ut, 0))
        atak = int(defaults["attack"][size].get(ut, 0))
        combat = int(defaults["combat"].get(f"{ut}__{size}", 0))
        # Obrona
        defense_defaults = {
            "Pluton": {"P": 4, "TC": 7, "AC": 2, "AL": 3, "AP": 2},
            "Kompania": {"P": 10, "TC": 18, "AC": 6, "AL": 7, "AP": 5},
            "Batalion": {"P": 20, "TC": 36, "AC": 12, "AL": 14, "AP": 10}
        }
        obrona = int(defense_defaults.get(size, {}).get(ut, 0))
        # Maintenance i cena
        maintenance = int(defaults["unit_maintenance"][size].get(ut, 0))
        cena = int(defaults["purchase"][size].get(ut, 0))
        sight = int(defaults["sight"].get(ut, 0))
        # --- Modyfikatory wsparcia i transportu ---
        # Transport (priorytet)
        transport = None
        for t in self.transport_types:
            if t in self.support_vars and self.support_vars[t].get():
                transport = t
                break
        if transport:
            upg = self.support_upgrades[transport]
            ruch += upg["movement"]
        # Pozostałe wsparcia
        movement_penalty_applied = False
        max_range_bonus = 0
        for sup, var in self.support_vars.items():
            if var.get() and sup not in self.transport_types:
                upg = self.support_upgrades[sup]
                # Kara do ruchu tylko raz
                if upg["movement"] < 0 and not movement_penalty_applied:
                    ruch -= 1
                    movement_penalty_applied = True
                atak += upg["attack"]
                combat += upg["combat"]
                cena += upg["purchase"]
                maintenance += upg["unit_maintenance"]
                # Bonus do zasięgu ataku (najwyższy)
                max_range_bonus = max(max_range_bonus, upg["range"])
                # Bonus do obrony
                obrona += upg["defense"]
        # Zastosuj najwyższy bonus do zasięgu ataku
        if max_range_bonus > 0:
            zasieg += max_range_bonus
        # Dolicz maintenance za transport
        if transport:
            maintenance += self.support_upgrades[transport]["unit_maintenance"]
            cena += self.support_upgrades[transport]["purchase"]
            obrona += self.support_upgrades[transport]["defense"]
        # Dolicz obronę za transport
        # Dolicz sight za wsparcia jeśli mają (w przyszłości)
        # --- Aktualizacja labeli ---
        self.stats_labels["Ruch"].config(text=str(ruch))
        self.stats_labels["Zasięg ataku"].config(text=str(zasieg))
        self.stats_labels["Siła ataku"].config(text=str(atak))
        self.stats_labels["Wartość bojowa"].config(text=str(combat))
        self.stats_labels["Obrona"].config(text=str(obrona))
        self.stats_labels["Utrzymanie"].config(text=str(maintenance))
        self.stats_labels["Cena"].config(text=str(cena))
        self.stats_labels["Zasięg widzenia"].config(text=str(sight))
        # Blokada przycisku kupna jeśli brak punktów
        self.buy_btn.config(state="normal" if self.points_var.get() >= cena else "disabled")
        self.current_stats = dict(ruch=ruch, zasieg=zasieg, atak=atak, combat=combat, obrona=obrona, maintenance=maintenance, cena=cena, sight=sight)
        self.update_token_preview()

    def update_token_preview(self):
        # Generuje miniaturę żetonu identyczną jak w TokenEditor (wzorowane na create_token_image)
        width, height = 120, 120
        nation = self.nation.get()
        unit_type = self.unit_type.get()
        unit_size = self.unit_size.get()
        # Flaga
        base_bg = create_flag_background(nation, width, height)
        token_img = base_bg.copy()
        draw = ImageDraw.Draw(token_img)
        # Obramowanie prostokątne
        draw.rectangle([0, 0, width, height], outline="black", width=3)
        # Przygotowanie tekstów
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
        # Czcionki
        try:
            font_type = ImageFont.truetype("arialbd.ttf", 19)
            font_size = ImageFont.truetype("arial.ttf", 11)
            font_symbol = ImageFont.truetype("arialbd.ttf", 18)
        except Exception:
            font_type = font_size = font_symbol = ImageFont.load_default()
        # Wyśrodkowanie i rysowanie (identycznie jak w TokenEditor)
        margin = 6
        # Pełna nazwa rodzaju jednostki – DUŻA, centralna, z zawijaniem
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            line = ""
            for w in words:
                test = line + (" " if line else "") + w
                if draw.textlength(test, font=font) <= max_width:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = w
            if line:
                lines.append(line)
            return lines
        max_text_width = int(width * 0.9)
        type_lines = wrap_text(unit_type_full, font_type, max_text_width)
        total_type_height = sum(draw.textbbox((0,0), line, font=font_type)[3] - draw.textbbox((0,0), line, font=font_type)[1] for line in type_lines)
        total_type_height += (len(type_lines)-1) * 2  # odstęp między liniami
        bbox_size = draw.textbbox((0,0), unit_size, font=font_size)
        size_height = bbox_size[3] - bbox_size[1]
        bbox_symbol = draw.textbbox((0,0), unit_symbol, font=font_symbol)
        symbol_height = bbox_symbol[3] - bbox_symbol[1]
        gap_type_to_size = margin * 2
        gap_size_to_symbol = 2
        total_height = total_type_height + gap_type_to_size + size_height + gap_size_to_symbol + symbol_height
        y = (height - total_height) // 2
        # Nazwa typu (zawijanie)
        for line in type_lines:
            bbox = draw.textbbox((0, 0), line, font=font_type)
            x = (width - (bbox[2] - bbox[0])) / 2
            draw.text((x, y), line, fill="black", font=font_type)
            y += bbox[3] - bbox[1] + 2
        y += gap_type_to_size - 2
        # Wielkość
        bbox_size = draw.textbbox((0, 0), unit_size, font=font_size)
        x_size = (width - (bbox_size[2] - bbox_size[0])) / 2
        draw.text((x_size, y), unit_size, fill="black", font=font_size)
        y += bbox_size[3] - bbox_size[1] + gap_size_to_symbol
        # Symbol wielkości
        bbox_symbol = draw.textbbox((0, 0), unit_symbol, font=font_symbol)
        x_symbol = (width - (bbox_symbol[2] - bbox_symbol[0])) / 2
        draw.text((x_symbol, y), unit_symbol, fill="black", font=font_symbol)
        # Wyświetl na canvasie
        self.flag_img = ImageTk.PhotoImage(token_img)
        self.flag_canvas.delete("all")
        self.flag_canvas.create_image(width // 2, height // 2, image=self.flag_img)

    def buy_unit(self):
        label = self.unit_label_var.get()
        unit_full_name = self.unit_full_name_var.get()
        dowodca_id = self.selected_commander.get()
        cena = self.current_stats["cena"]
        if cena > self.points_var.get():
            self.info_label.config(text="Za mało punktów!")
            return
        # --- Generuj unikalny id ---
        import datetime
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unit_id = f"nowy_{self.unit_type.get()}_{self.unit_size.get()}__{dowodca_id}_{label}_{now}"
        folder = Path("assets/tokens") / f"nowe_dla_{dowodca_id}" / unit_id
        folder.mkdir(parents=True, exist_ok=True)
        # Zamiast: "image": "token.png",
        # Ustal ścieżkę względną do pliku PNG względem katalogu głównego projektu
        # np. assets/tokens/nowe_dla_{dowodca_id}/{unit_id}/token.png
        rel_img_path = str(folder / "token.png").replace("\\", "/")
        token_json = {
            "id": unit_id,
            "nation": self.nation.get(),
            "unitType": self.unit_type.get(),
            "unitSize": self.unit_size.get(),
            "shape": "prostokąt",
            "label": label,
            "unit_full_name": unit_full_name,
            "move": self.current_stats["ruch"],
            "attack": {"range": self.current_stats["zasieg"], "value": self.current_stats["atak"]},
            "combat_value": self.current_stats["combat"],
            "defense_value": self.current_stats["obrona"],
            "maintenance": self.current_stats["maintenance"],
            "price": cena,
            "sight": self.current_stats["sight"],
            "owner": f"{dowodca_id}",
            "image": rel_img_path,
            "w": 240,
            "h": 240
        }
        import json
        with open(folder / "token.json", "w", encoding="utf-8") as f:
            json.dump(token_json, f, indent=2, ensure_ascii=False)
        # --- Obrazek: żeton jak w podglądzie ---
        width, height = 240, 240
        nation = self.nation.get()
        unit_type = self.unit_type.get()
        unit_size = self.unit_size.get()
        base_bg = create_flag_background(nation, width, height)
        token_img = base_bg.copy()
        draw = ImageDraw.Draw(token_img)
        draw.rectangle([0, 0, width, height], outline="black", width=6)
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
        try:
            font_type = ImageFont.truetype("arialbd.ttf", 38)
            font_size = ImageFont.truetype("arial.ttf", 22)
            font_symbol = ImageFont.truetype("arialbd.ttf", 36)
        except Exception:
            font_type = font_size = font_symbol = ImageFont.load_default()
        margin = 12
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            line = ""
            for w in words:
                test = line + (" " if line else "") + w
                if draw.textlength(test, font=font) <= max_width:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = w
            if line:
                lines.append(line)
            return lines
        max_text_width = int(width * 0.9)
        type_lines = wrap_text(unit_type_full, font_type, max_text_width)
        total_type_height = sum(draw.textbbox((0,0), line, font=font_type)[3] - draw.textbbox((0,0), line, font=font_type)[1] for line in type_lines)
        total_type_height += (len(type_lines)-1) * 4
        bbox_size = draw.textbbox((0,0), unit_size, font=font_size)
        size_height = bbox_size[3] - bbox_size[1]
        bbox_symbol = draw.textbbox((0,0), unit_symbol, font=font_symbol)
        symbol_height = bbox_symbol[3] - bbox_symbol[1]
        gap_type_to_size = margin * 2
        gap_size_to_symbol = 4
        total_height = total_type_height + gap_type_to_size + size_height + gap_size_to_symbol + symbol_height
        y = (height - total_height) // 2
        for line in type_lines:
            bbox = draw.textbbox((0, 0), line, font=font_type)
            x = (width - (bbox[2] - bbox[0])) / 2
            draw.text((x, y), line, fill="black", font=font_type)
            y += bbox[3] - bbox[1] + 4
        y += gap_type_to_size - 4
        bbox_size = draw.textbbox((0, 0), unit_size, font=font_size)
        x_size = (width - (bbox_size[2] - bbox_size[0])) / 2
        draw.text((x_size, y), unit_size, fill="black", font=font_size)
        y += bbox_size[3] - bbox_size[1] + gap_size_to_symbol
        bbox_symbol = draw.textbbox((0, 0), unit_symbol, font=font_symbol)
        x_symbol = (width - (bbox_symbol[2] - bbox_symbol[0])) / 2
        draw.text((x_symbol, y), unit_symbol, fill="black", font=font_symbol)
        token_img.save(folder / "token.png")
        # Odejmij punkty
        self.points_var.set(self.points_var.get() - cena)
        self.points_label.config(text=f"Dostępne punkty ekonomiczne: {self.points_var.get()}")
        self.ekonomia.subtract_points(cena)
        self.info_label.config(text=f"Zakupiono: {unit_full_name} (koszt: {cena})", fg="green")
        if self.on_purchase_callback:
            self.on_purchase_callback()

    def save_token_preview_as_png(self):
        try:
            from tkinter import filedialog
            # Generuj aktualny obrazek podglądu
            width, height = 120, 120
            nation = self.nation.get()
            unit_type = self.unit_type.get()
            unit_size = self.unit_size.get()
            base_bg = create_flag_background(nation, width, height)
            token_img = base_bg.copy()
            draw = ImageDraw.Draw(token_img)
            draw.rectangle([0, 0, width, height], outline="black", width=3)
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
            font = ImageFont.truetype("arial.ttf", 16) if os.path.exists("arial.ttf") else ImageFont.load_default()
            draw.text((10, 10), unit_type_full, fill="black", font=font)
            draw.text((10, 40), unit_size, fill="black", font=font)
            draw.text((10, 70), unit_symbol, fill="black", font=font)
            # Okno dialogowe do wyboru ścieżki
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")], title="Zapisz podgląd żetonu jako PNG")
            if file_path:
                token_img.save(file_path, format="PNG")
                messagebox.showinfo("Zapisano", f"Podgląd żetonu zapisany jako: {file_path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać pliku PNG:\n{e}\n{traceback.format_exc()}")
