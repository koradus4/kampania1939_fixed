"""
KREATOR ARMII - Profesjonalna aplikacja do tworzenia armii
Pełna automatyzacja, GUI, kontrola parametrów, inteligentne balansowanie
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import sys
import json
import random
import threading
import time
from unittest.mock import patch

# Dodaj ścieżkę do edytorów (z głównego folderu projektu)
project_root = Path(__file__).parent
sys.path.append(str(project_root / "edytory"))

class ArmyCreatorStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("🎖️ Kreator Armii - Kampania 1939")
        self.root.geometry("800x700")
        self.root.configure(bg="#556B2F")  # Dark olive green jak w grze
        self.root.resizable(True, True)
        
        # Ikona i style
        self.setup_styles()
        
        # Dane aplikacji (POPRAWIONE - po 2 dowódców na nację)
        self.nations = ["Polska", "Niemcy"]
        self.commanders = {
            "Polska": ["1 (Polska)", "2 (Polska)"],
            "Niemcy": ["5 (Niemcy)", "6 (Niemcy)"]
        }
        
        # Typy jednostek z bazowymi kosztami i statystykami
        self.unit_templates = {
            "P": {"name": "Piechota", "base_cost": 25, "weight": 0.4},
            "K": {"name": "Kawaleria", "base_cost": 30, "weight": 0.1},
            "TL": {"name": "Czołg Lekki", "base_cost": 35, "weight": 0.15},
            "TŚ": {"name": "Czołg Średni", "base_cost": 45, "weight": 0.1},
            "TC": {"name": "Czołg Ciężki", "base_cost": 60, "weight": 0.05},
            "TS": {"name": "Sam. Pancerny", "base_cost": 35, "weight": 0.1},
            "AL": {"name": "Artyleria Lekka", "base_cost": 35, "weight": 0.15},
            "AC": {"name": "Artyleria Ciężka", "base_cost": 55, "weight": 0.1},
            "AP": {"name": "Art. Przeciwlotnicza", "base_cost": 30, "weight": 0.05},
            "Z": {"name": "Zaopatrzenie/Rozpoznanie", "base_cost": 20, "weight": 0.1},
            "D": {"name": "Dowództwo", "base_cost": 40, "weight": 0.05}
        }
        
        self.unit_sizes = ["Pluton", "Kompania", "Batalion"]
        
        # Zmienne GUI
        self.selected_nation = tk.StringVar(value="Polska")
        self.selected_commander = tk.StringVar(value="1 (Polska)")
        self.army_size = tk.IntVar(value=10)
        self.army_budget = tk.IntVar(value=500)
        self.creating_army = False
        
        # Lista utworzonych jednostek
        self.created_units = []
        
        # Token Editor (zainicjalizowany później)
        self.token_editor = None
        
        self.create_gui()
        self.update_commander_options()
    
    def setup_styles(self):
        """Konfiguracja stylów TTK."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Kolory motywu wojskowego (jak w grze)
        style.configure('Title.TLabel', 
                       foreground='white', 
                       background='#556B2F',  # Dark olive green
                       font=('Arial', 20, 'bold'))
        
        style.configure('Header.TLabel',
                       foreground='white',
                       background='#556B2F',  # Dark olive green
                       font=('Arial', 12, 'bold'))
        
        style.configure('Military.TButton',
                       font=('Arial', 11, 'bold'),
                       foreground='#556B2F')
        
        style.configure('Success.TButton',
                       font=('Arial', 12, 'bold'),
                       foreground='#6B8E23')  # Olive green jak w grze
        
        style.configure('Danger.TButton',
                       font=('Arial', 12, 'bold'),
                       foreground='#8B0000')
    
    def create_gui(self):
        """Tworzy główny interfejs aplikacji."""
        
        # Nagłówek
        header_frame = tk.Frame(self.root, bg="#6B8E23", height=80)  # Olive green jak w grze
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, 
                               text="🎖️ KREATOR ARMII", 
                               style='Title.TLabel')
        title_label.pack(expand=True)
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Profesjonalne tworzenie armii dla Kampanii 1939",
                                  style='Header.TLabel')
        subtitle_label.pack()
        
        # Główny kontener
        main_frame = tk.Frame(self.root, bg="#556B2F")  # Dark olive green
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Lewa kolumna - Parametry
        left_frame = tk.Frame(main_frame, bg="#6B8E23", width=350)  # Olive green jak w grze
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        self.create_parameters_panel(left_frame)
        
        # Prawa kolumna - Podgląd i kontrola
        right_frame = tk.Frame(main_frame, bg="#6B8E23")  # Olive green jak w grze
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_preview_panel(right_frame)
        
        # Status bar na dole
        self.create_status_bar()
    
    def create_parameters_panel(self, parent):
        """Tworzy panel parametrów armii."""
        
        # Tytuł sekcji
        ttk.Label(parent, text="⚙️ PARAMETRY ARMII", style='Header.TLabel').pack(pady=10)
        
        # Nacja
        nation_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        nation_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(nation_frame, text="🏴 Nacja:", style='Header.TLabel').pack(anchor='w')
        nation_combo = ttk.Combobox(nation_frame, textvariable=self.selected_nation,
                                   values=self.nations, state='readonly', width=25)
        nation_combo.pack(fill=tk.X, pady=2)
        nation_combo.bind('<<ComboboxSelected>>', self.on_nation_change)
        
        # Dowódca
        commander_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        commander_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(commander_frame, text="👨‍✈️ Dowódca:", style='Header.TLabel').pack(anchor='w')
        self.commander_combo = ttk.Combobox(commander_frame, textvariable=self.selected_commander,
                                           state='readonly', width=25)
        self.commander_combo.pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=20, pady=15)
        
        # Rozmiar armii
        size_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        size_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(size_frame, text="📊 Ilość żetonów:", style='Header.TLabel').pack(anchor='w')
        self.size_scale = tk.Scale(size_frame, from_=5, to=25, orient=tk.HORIZONTAL,
                                  variable=self.army_size, bg="#6B8E23", fg="white",
                                  highlightbackground="#6B8E23", command=self.update_preview)
        self.size_scale.pack(fill=tk.X, pady=2)
        
        # Budżet VP
        budget_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        budget_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(budget_frame, text="💰 Budżet VP:", style='Header.TLabel').pack(anchor='w')
        self.budget_scale = tk.Scale(budget_frame, from_=250, to=1000, orient=tk.HORIZONTAL,
                                    variable=self.army_budget, bg="#6B8E23", fg="white",
                                    highlightbackground="#6B8E23", command=self.update_preview)
        self.budget_scale.pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=20, pady=15)
        
        # Przyciski akcji
        action_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(action_frame, text="🎲 Losowa Armia", 
                  command=self.generate_random_army,
                  style='Military.TButton').pack(fill=tk.X, pady=2)
        
        ttk.Button(action_frame, text="⚖️ Zbalansuj Auto",
                  command=self.auto_balance_army,
                  style='Military.TButton').pack(fill=tk.X, pady=2)
        
        ttk.Button(action_frame, text="🗑️ Wyczyść",
                  command=self.clear_army,
                  style='Danger.TButton').pack(fill=tk.X, pady=2)
        
        # Główny przycisk tworzenia
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        self.create_button = ttk.Button(action_frame, text="💾 UTWÓRZ ARMIĘ",
                                       command=self.create_army_thread,
                                       style='Success.TButton')
        self.create_button.pack(fill=tk.X, pady=10)
    
    def create_preview_panel(self, parent):
        """Tworzy panel podglądu armii."""
        
        # Tytuł sekcji
        ttk.Label(parent, text="👁️ PODGLĄD ARMII", style='Header.TLabel').pack(pady=10)
        
        # Informacje o armii
        info_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="Wybierz parametry aby zobaczyć podgląd",
                                   style='Header.TLabel')
        self.info_label.pack()
        
        # Lista jednostek
        list_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(list_frame, text="📋 Skład armii:", style='Header.TLabel').pack(anchor='w')
        
        # Scrolled text dla listy jednostek
        self.units_text = scrolledtext.ScrolledText(list_frame, height=15, width=40,
                                                   bg="white", fg="#556B2F",  # Tekst w kolorze dark olive
                                                   font=('Consolas', 10))
        self.units_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Progress bar
        self.progress_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        self.progress_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(self.progress_frame, text="Postęp tworzenia:", style='Header.TLabel').pack(anchor='w')
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Gotowy do pracy",
                                       style='Header.TLabel')
        self.progress_label.pack()
    
    def create_status_bar(self):
        """Tworzy pasek statusu."""
        status_frame = tk.Frame(self.root, bg="#556B2F", height=30)  # Dark olive green
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = ttk.Label(status_frame, 
                                     text="⚡ Kreator Armii - Gotowy",
                                     style='Header.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Informacja o autorze
        author_label = ttk.Label(status_frame,
                                text="Kampania 1939 © 2025",
                                style='Header.TLabel')
        author_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def on_nation_change(self, event=None):
        """Obsługuje zmianę nacji."""
        self.update_commander_options()
        self.update_preview()
    
    def update_commander_options(self):
        """Aktualizuje opcje dowódców dla wybranej nacji."""
        nation = self.selected_nation.get()
        commanders = self.commanders.get(nation, [])
        
        self.commander_combo['values'] = commanders
        if commanders:
            self.selected_commander.set(commanders[0])
    
    def update_preview(self, event=None):
        """Aktualizuje podgląd armii."""
        if self.creating_army:
            return
            
        size = self.army_size.get()
        budget = self.army_budget.get()
        nation = self.selected_nation.get()
        
        # Aktualizuj informacje
        avg_cost = budget // size if size > 0 else 0
        self.info_label.config(text=f"📊 {size} żetonów | 💰 {budget} VP | ⚖️ ~{avg_cost} VP/żeton")
        
        # Wygeneruj przykładową armię do podglądu
        preview_army = self.generate_balanced_army_preview(size, budget)
        
        # Wyświetl w text widget
        self.units_text.delete(1.0, tk.END)
        total_cost = 0
        
        for i, unit in enumerate(preview_army, 1):
            unit_text = f"{i:2}. {unit['type']} {unit['size']} - {unit['cost']} VP\n"
            self.units_text.insert(tk.END, unit_text)
            total_cost += unit['cost']
        
        # Podsumowanie
        self.units_text.insert(tk.END, f"\n{'='*30}\n")
        self.units_text.insert(tk.END, f"SUMA: {total_cost} VP\n")
        self.units_text.insert(tk.END, f"BUDŻET: {budget} VP\n")
        self.units_text.insert(tk.END, f"POZOSTAŁO: {budget - total_cost} VP\n")
        
        # Analiza balansu
        self.analyze_army_balance(preview_army)
    
    def generate_balanced_army_preview(self, size, budget):
        """Generuje zbalansowaną armię do podglądu."""
        army = []
        remaining_budget = budget
        remaining_slots = size
        
        # Sortuj typy według wagi (od najważniejszych)
        sorted_types = sorted(self.unit_templates.items(), 
                             key=lambda x: x[1]['weight'], reverse=True)
        
        for unit_type, template in sorted_types:
            if remaining_slots <= 0 or remaining_budget <= 0:
                break
                
            # Oblicz ile jednostek tego typu chcemy
            desired_count = max(1, int(size * template['weight']))
            actual_count = min(desired_count, remaining_slots, 
                             remaining_budget // template['base_cost'])
            
            for _ in range(actual_count):
                if remaining_slots <= 0 or remaining_budget < template['base_cost']:
                    break
                    
                # Wybierz losowy rozmiar jednostki
                unit_size = random.choice(self.unit_sizes)
                
                # Dostosuj koszt w zależności od rozmiaru
                size_multiplier = {"Pluton": 1.0, "Kompania": 1.5, "Batalion": 2.2}
                unit_cost = int(template['base_cost'] * size_multiplier.get(unit_size, 1.0))
                
                # Dodaj losową wariację ±20%
                variation = random.uniform(0.8, 1.2)
                unit_cost = int(unit_cost * variation)
                
                if unit_cost <= remaining_budget:
                    army.append({
                        'type': template['name'],
                        'size': unit_size,
                        'cost': unit_cost,
                        'unit_type': unit_type
                    })
                    remaining_budget -= unit_cost
                    remaining_slots -= 1
        
        # Wypełnij pozostałe sloty tanimi jednostkami
        while remaining_slots > 0 and remaining_budget >= 15:
            cheap_types = [('Z', 'Rozpoznanie'), ('P', 'Piechota')]
            unit_type, type_name = random.choice(cheap_types)
            unit_size = 'Pluton'
            unit_cost = min(remaining_budget, random.randint(15, 25))
            
            army.append({
                'type': type_name,
                'size': unit_size, 
                'cost': unit_cost,
                'unit_type': unit_type
            })
            remaining_budget -= unit_cost
            remaining_slots -= 1
        
        return army
    
    def analyze_army_balance(self, army):
        """Analizuje balans armii i wyświetla statystyki."""
        if not army:
            return
            
        # Policz typy jednostek
        type_counts = {}
        total_cost = sum(unit['cost'] for unit in army)
        
        for unit in army:
            unit_type = unit['unit_type']
            type_counts[unit_type] = type_counts.get(unit_type, 0) + 1
        
        # Wyświetl analizę
        self.units_text.insert(tk.END, f"\n📊 ANALIZA BALANSU:\n")
        
        for unit_type, count in sorted(type_counts.items()):
            template = self.unit_templates.get(unit_type, {})
            type_name = template.get('name', unit_type)
            percentage = (count / len(army)) * 100
            self.units_text.insert(tk.END, f"  {type_name}: {count} ({percentage:.0f}%)\n")
    
    def generate_random_army(self):
        """Generuje losową armię."""
        size = random.randint(8, 20)
        budget = random.randint(300, 800)
        
        self.army_size.set(size)
        self.army_budget.set(budget)
        self.update_preview()
        
        self.status_label.config(text="🎲 Wygenerowano losową armię")
    
    def auto_balance_army(self):
        """Automatycznie balansuje armię według optymalnych proporcji."""
        size = self.army_size.get()
        budget = self.army_budget.get()
        
        # Optymalne proporcje dla różnych rozmiarów armii
        if size <= 8:
            # Mała armia - skupiona
            optimal_budget = min(budget, size * 45)
        elif size <= 15:
            # Średnia armia - zbalansowana
            optimal_budget = min(budget, size * 35)
        else:
            # Duża armia - tańsze jednostki
            optimal_budget = min(budget, size * 30)
        
        self.army_budget.set(optimal_budget)
        self.update_preview()
        
        self.status_label.config(text="⚖️ Armia została automatycznie zbalansowana")
    
    def clear_army(self):
        """Czyści podgląd armii."""
        self.units_text.delete(1.0, tk.END)
        self.units_text.insert(tk.END, "Armia została wyczyszczona.\n\nWybierz parametry aby zobaczyć nowy podgląd.")
        self.status_label.config(text="🗑️ Armia wyczyszczona")
    
    def create_army_thread(self):
        """Uruchamia tworzenie armii w głównym wątku GUI (nieblokujące)."""
        if self.creating_army:
            return
            
        self.creating_army = True
        
        try:
            # Aktualizuj GUI
            self.create_button.config(state='disabled', text="⏳ TWORZENIE...")
            self.status_label.config(text="🏭 Tworzenie armii w toku...")
            
            # Wygeneruj finalną armię
            size = self.army_size.get()
            budget = self.army_budget.get()
            self.final_army = self.generate_final_army(size, budget)
            
            # Inicjalizuj Token Editor
            self.progress_label.config(text="Inicjalizacja Token Editor...")
            self.initialize_token_editor()
            
            # Rozpocznij sekwencyjne tworzenie żetonów
            self.current_unit_index = 0
            self.total_units = len(self.final_army)
            self.root.after(100, self.create_next_token)
            
        except Exception as e:
            self.creation_failed(str(e))
    
    def create_next_token(self):
        """Tworzy kolejny żeton w sekwencji (nieblokujące)."""
        if self.current_unit_index >= self.total_units:
            # Wszystkie żetony utworzone
            self.creation_completed(self.total_units)
            return
            
        unit = self.final_army[self.current_unit_index]
        progress = ((self.current_unit_index + 1) / self.total_units) * 100
        
        # Aktualizuj progress
        self.update_creation_progress(progress, f"Tworzenie: {unit['name']}")
        
        # Utwórz żeton
        try:
            self.create_single_token(unit)
            self.current_unit_index += 1
            # Zaplanuj następny żeton za 500ms
            self.root.after(500, self.create_next_token)
        except Exception as e:
            print(f"Błąd tworzenia żetonu {unit['name']}: {e}")
            self.current_unit_index += 1
            # Kontynuuj mimo błędu
            self.root.after(500, self.create_next_token)
    
    def generate_final_army(self, size, budget):
        """Generuje finalną armię z dokładnymi nazwami jednostek."""
        nation = self.selected_nation.get()
        commander_full = self.selected_commander.get()
        commander_num = commander_full.split()[0]
        
        # Bazowa armia
        base_army = self.generate_balanced_army_preview(size, budget)
        
        # Konwertuj na finalne jednostki z nazwami
        final_army = []
        for i, unit in enumerate(base_army, 1):
            unit_data = self.convert_to_final_unit(unit, nation, commander_num, i)
            final_army.append(unit_data)
        
        return final_army
    
    def convert_to_final_unit(self, preview_unit, nation, commander_num, index):
        """Konwertuje jednostkę podglądu na finalną jednostkę z pełnymi danymi."""
        
        # Słowniki nazw dla różnych nacji
        if nation == "Polska":
            unit_names = {
                "P": [f"{commander_num}. Pułk Piechoty", f"{commander_num}. Batalion Strzelców", f"{commander_num}. Kompania Grenadierów"],
                "K": [f"{commander_num}. Pułk Ułanów", f"{commander_num}. Szwadron Kawalerii", f"{commander_num}. Oddział Jazdy"],
                "TL": [f"{commander_num}. Pluton Tankietek", f"{commander_num}. Kompania Czołgów Lekkich", f"{commander_num}. Batalion Pancerny"],
                "TŚ": [f"{commander_num}. Pluton Czołgów", f"{commander_num}. Kompania Pancerna", f"{commander_num}. Batalion Czołgów"],
                "AL": [f"{commander_num}. Bateria Artylerii", f"{commander_num}. Dywizjon Artylerii", f"{commander_num}. Pułk Artylerii"],
                "AC": [f"{commander_num}. Bateria Ciężka", f"{commander_num}. Dywizjon Ciężki", f"{commander_num}. Pułk Artylerii Ciężkiej"],
                "Z": [f"{commander_num}. Oddział Rozpoznawczy", f"{commander_num}. Kompania Zaopatrzeniowa", f"{commander_num}. Batalion Wsparcia"]
            }
        else:  # Niemcy
            unit_names = {
                "P": [f"{commander_num}. Infanterie Regiment", f"{commander_num}. Grenadier Bataillon", f"{commander_num}. Schützen Kompanie"],
                "TL": [f"{commander_num}. Panzer Zug", f"{commander_num}. Panzer Kompanie", f"{commander_num}. Panzer Abteilung"],
                "TŚ": [f"{commander_num}. schwere Panzer", f"{commander_num}. Panzer Regiment", f"{commander_num}. Panzer Brigade"],
                "AL": [f"{commander_num}. Artillerie Batterie", f"{commander_num}. Artillerie Abteilung", f"{commander_num}. Artillerie Regiment"],
                "AC": [f"{commander_num}. schwere Artillerie", f"{commander_num}. Haubitze Abteilung", f"{commander_num}. schwere Artillerie Regiment"],
                "Z": [f"{commander_num}. Aufklärungs Zug", f"{commander_num}. Versorgungs Kompanie", f"{commander_num}. Unterstützungs Bataillon"]
            }
        
        unit_type = preview_unit['unit_type']
        names_list = unit_names.get(unit_type, [f"{commander_num}. {preview_unit['type']} Einheit"])
        unit_name = random.choice(names_list)
        
        # Generuj statystyki na podstawie kosztu i typu
        cost = preview_unit['cost']
        base_stats = self.generate_unit_stats(unit_type, preview_unit['size'], cost)
        
        return {
            "name": unit_name,
            "nation": nation,
            "unit_type": unit_type,
            "unit_size": preview_unit['size'],
            "movement_points": str(base_stats['movement']),
            "attack_range": str(base_stats['attack_range']),
            "attack_value": str(base_stats['attack_value']),
            "combat_value": str(base_stats['combat_value']),
            "defense_value": str(base_stats['defense_value']),
            "unit_maintenance": str(base_stats['maintenance']),
            "purchase_value": str(cost),
            "sight_range": str(base_stats['sight']),
            "support": base_stats.get('support', "")
        }
    
    def generate_unit_stats(self, unit_type, unit_size, cost):
        """Generuje statystyki jednostki na podstawie typu, rozmiaru i kosztu."""
        
        # Bazowe statystyki dla typów jednostek
        base_stats = {
            "P": {"movement": 3, "attack_range": 1, "attack_value": 8, "combat_value": 8, "defense_value": 10, "sight": 3},
            "K": {"movement": 6, "attack_range": 1, "attack_value": 6, "combat_value": 6, "defense_value": 8, "sight": 5},
            "TL": {"movement": 5, "attack_range": 1, "attack_value": 10, "combat_value": 10, "defense_value": 12, "sight": 3},
            "TŚ": {"movement": 4, "attack_range": 2, "attack_value": 14, "combat_value": 14, "defense_value": 16, "sight": 3},
            "TC": {"movement": 3, "attack_range": 2, "attack_value": 18, "combat_value": 18, "defense_value": 22, "sight": 3},
            "TS": {"movement": 5, "attack_range": 1, "attack_value": 8, "combat_value": 8, "defense_value": 10, "sight": 4},
            "AL": {"movement": 3, "attack_range": 3, "attack_value": 12, "combat_value": 6, "defense_value": 6, "sight": 4},
            "AC": {"movement": 2, "attack_range": 4, "attack_value": 18, "combat_value": 8, "defense_value": 8, "sight": 5},
            "AP": {"movement": 2, "attack_range": 2, "attack_value": 10, "combat_value": 6, "defense_value": 8, "sight": 4},
            "Z": {"movement": 6, "attack_range": 1, "attack_value": 4, "combat_value": 4, "defense_value": 6, "sight": 6},
            "D": {"movement": 4, "attack_range": 1, "attack_value": 6, "combat_value": 8, "defense_value": 12, "sight": 5}
        }
        
        stats = base_stats.get(unit_type, base_stats["P"]).copy()
        
        # Modyfikatory na podstawie rozmiaru jednostki
        size_multipliers = {
            "Pluton": 1.0,
            "Kompania": 1.4,
            "Batalion": 1.8
        }
        
        multiplier = size_multipliers.get(unit_size, 1.0)
        
        # Skaluj statystyki bojowe
        stats["attack_value"] = int(stats["attack_value"] * multiplier)
        stats["combat_value"] = int(stats["combat_value"] * multiplier)
        stats["defense_value"] = int(stats["defense_value"] * multiplier)
        
        # Utrzymanie na podstawie kosztu
        stats["maintenance"] = max(1, cost // 15)
        
        # Dodaj losową wariację ±15%
        for key in ["attack_value", "combat_value", "defense_value"]:
            variation = random.uniform(0.85, 1.15)
            stats[key] = max(1, int(stats[key] * variation))
        
        return stats
    
    def initialize_token_editor(self):
        """Inicjalizuje Token Editor w dedykowanym oknie."""
        if self.token_editor is None:
            from token_editor_prototyp import TokenEditor
            
            # Utwórz dedykowane okno dla Token Editor
            token_window = tk.Toplevel(self.root)
            token_window.title("Token Editor - Tryb Automatyczny")
            token_window.geometry("400x300")  # Mniejsze okno
            token_window.configure(bg="darkolivegreen")
            
            # Przesuń okno poza główny obszar
            token_window.geometry("+50+50")
            
            # Zminimalizuj okno ale nie ukrywaj go całkowicie
            token_window.iconify()
            
            self.token_editor = TokenEditor(token_window)
            
            # Dodaj informację o trybie automatycznym
            info_label = tk.Label(token_window, 
                                text="🤖 TRYB AUTOMATYCZNY\nToken Editor pracuje w tle...", 
                                bg="darkolivegreen", fg="white", 
                                font=("Arial", 12, "bold"))
            info_label.pack(expand=True)
    
    def create_single_token(self, unit):
        """Tworzy pojedynczy żeton używając Token Editor."""
        try:
            # Ustaw parametry w Token Editor
            commander = self.selected_commander.get()
            
            if hasattr(self.token_editor, 'selected_commander'):
                self.token_editor.selected_commander.set(commander)
            
            self.token_editor.nation.set(unit["nation"])
            self.token_editor.unit_type.set(unit["unit_type"])
            self.token_editor.unit_size.set(unit["unit_size"])
            
            # Ustaw statystyki
            self.token_editor.movement_points.set(unit["movement_points"])
            self.token_editor.attack_range.set(unit["attack_range"])
            self.token_editor.attack_value.set(unit["attack_value"])
            self.token_editor.combat_value.set(unit["combat_value"])
            self.token_editor.defense_value.set(unit["defense_value"])
            self.token_editor.unit_maintenance.set(unit["unit_maintenance"])
            self.token_editor.purchase_value.set(unit["purchase_value"])
            self.token_editor.sight_range.set(unit["sight_range"])
            
            # Wsparcie
            if unit["support"] and hasattr(self.token_editor, 'selected_support'):
                self.token_editor.selected_support.set(unit["support"])
            
            # Wygeneruj podgląd
            self.token_editor.update_preview()
            
            # Zapisz żeton z mockami dialogów
            with patch('tkinter.messagebox.askyesno', return_value=True), \
                 patch('tkinter.simpledialog.askstring', return_value=unit['name']):
                self.token_editor.save_token()
            
            return True
            
        except Exception as e:
            print(f"Błąd tworzenia żetonu {unit['name']}: {e}")
            return False
    
    def update_creation_progress(self, progress, message):
        """Aktualizuje progress bar i wiadomość."""
        self.progress_bar['value'] = progress
        self.progress_label.config(text=message)
        self.status_label.config(text=f"🏭 {message}")
    
    def creation_completed(self, units_created):
        """Obsługuje zakończenie tworzenia armii."""
        self.creating_army = False
        self.progress_bar['value'] = 100
        self.progress_label.config(text=f"✅ Utworzono {units_created} żetonów!")
        self.status_label.config(text=f"🎉 Armia ukończona! Utworzono {units_created} żetonów")
        
        self.create_button.config(state='normal', text="💾 UTWÓRZ ARMIĘ")
        
        # Wyświetl podsumowanie
        messagebox.showinfo("🎉 Sukces!", 
                           f"Armia została pomyślnie utworzona!\n\n"
                           f"📊 Utworzono: {units_created} żetonów\n"
                           f"🎖️ Dowódca: {self.selected_commander.get()}\n"
                           f"🏴 Nacja: {self.selected_nation.get()}\n"
                           f"💰 Budżet: {self.army_budget.get()} VP\n\n"                           f"Żetony zapisane w katalogu assets/tokens/")
    
    def creation_failed(self, error_message):
        """Obsługuje błąd podczas tworzenia armii."""
        self.creating_army = False
        self.progress_label.config(text="❌ Błąd tworzenia armii")
        self.status_label.config(text="❌ Błąd podczas tworzenia armii")
        
        self.create_button.config(state='normal', text="💾 UTWÓRZ ARMIĘ")
        
        messagebox.showerror("❌ Błąd", 
                            f"Wystąpił błąd podczas tworzenia armii:\n\n{error_message}")

def main():
    """Główna funkcja aplikacji."""
    root = tk.Tk()
    app = ArmyCreatorStudio(root)
    
    # Wyśrodkuj okno na ekranie
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
