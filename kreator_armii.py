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
import shutil
from unittest.mock import patch

# Dodaj ścieżkę do edytorów (z głównego folderu projektu)
project_root = Path(__file__).parent
sys.path.append(str(project_root / "edytory"))

class ArmyCreatorStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("🎖️ Kreator Armii - Kampania 1939")
        self.root.geometry("900x750")  # Zwiększona wysokość z 600 na 750
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
        header_frame = tk.Frame(self.root, bg="#6B8E23", height=60)  # Olive green jak w grze
        header_frame.pack(fill=tk.X, padx=10, pady=3)
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
          # Lewa kolumna - Parametry ze scrollbarem
        left_outer_frame = tk.Frame(main_frame, bg="#6B8E23", width=350)
        left_outer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_outer_frame.pack_propagate(False)
        
        # Canvas ze scrollbarem dla lewej kolumny
        canvas = tk.Canvas(left_outer_frame, bg="#6B8E23", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_outer_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#6B8E23")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind scroll events
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self.create_parameters_panel(self.scrollable_frame)
        
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
        self.commander_combo.bind('<<ComboboxSelected>>', self.on_commander_change)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=20, pady=8)
        
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
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=20, pady=8)
        
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
          # Panel zarządzania folderami - kompaktowy
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=20, pady=3)
        
        management_frame = tk.Frame(parent, bg="#6B8E23")  # Olive green
        management_frame.pack(fill=tk.X, padx=15, pady=3)
        
        # Nagłówek mniejszy
        header_label = tk.Label(management_frame, text="🗂️ ZARZĄDZANIE FOLDERAMI", 
                               bg="#6B8E23", fg="white", font=("Arial", 10, "bold"))
        header_label.pack(pady=1)
        
        # Statystyki żetonów - kompaktowe
        self.stats_frame = tk.Frame(management_frame, bg="#556B2F", relief=tk.RIDGE, bd=1)
        self.stats_frame.pack(fill=tk.X, pady=2)
        
        self.stats_label = tk.Label(self.stats_frame, 
                                   text="📊 Sprawdzanie folderów...", 
                                   bg="#556B2F", fg="white", 
                                   font=("Arial", 8), wraplength=300)
        self.stats_label.pack(pady=1)
        
        # Przyciski czyszczenia - mniejsze
        clean_frame = tk.Frame(management_frame, bg="#6B8E23")
        clean_frame.pack(fill=tk.X, pady=1)
        
        # Małe przyciski z mniejszymi fontami
        btn_style = ttk.Style()
        btn_style.configure('Small.Danger.TButton',
                           font=('Arial', 9),
                           foreground='#8B0000')
        btn_style.configure('Small.Military.TButton',
                           font=('Arial', 9),
                           foreground='#556B2F')
        
        ttk.Button(clean_frame, text="🗑️ Polskie",
                  command=self.clean_polish_tokens,
                  style='Small.Danger.TButton').pack(fill=tk.X, pady=1)
        
        ttk.Button(clean_frame, text="🗑️ Niemieckie",
                  command=self.clean_german_tokens,
                  style='Small.Danger.TButton').pack(fill=tk.X, pady=1)
        
        ttk.Button(clean_frame, text="🗑️ WSZYSTKIE",
                  command=self.clean_all_tokens,                  style='Small.Danger.TButton').pack(fill=tk.X, pady=1)
        
        ttk.Button(clean_frame, text="🔄 Odśwież",
                  command=self.refresh_token_stats,
                  style='Small.Military.TButton').pack(fill=tk.X, pady=1)
          # Panel rozstawiania armii na mapie - bardzo kompaktowy
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=15, pady=2)
        
        deploy_frame = tk.Frame(parent, bg="#6B8E23")
        deploy_frame.pack(fill=tk.X, padx=15, pady=2)
        
        # Nagłówek mniejszy
        deploy_label = tk.Label(deploy_frame, text="🗺️ MAPA", 
                               bg="#6B8E23", fg="white", font=("Arial", 9, "bold"))
        deploy_label.pack(pady=1)
        
        # Info o ćwiartce - bardzo kompaktowe
        self.quarter_info = tk.Label(deploy_frame, text="📍 Wybierz dowódcę", 
                                    bg="#556B2F", fg="white", font=("Arial", 7), 
                                    wraplength=300, height=2)
        self.quarter_info.pack(fill=tk.X, pady=1)
        
        # Przyciski rozstawiania - małe
        deploy_buttons = tk.Frame(deploy_frame, bg="#6B8E23")
        deploy_buttons.pack(fill=tk.X, pady=1)
        
        # Dodaj style dla bardzo małych przycisków
        btn_style = ttk.Style()
        btn_style.configure('Tiny.Military.TButton',
                           font=('Arial', 8),
                           foreground='#556B2F')
        btn_style.configure('Tiny.Danger.TButton',
                           font=('Arial', 8),
                           foreground='#8B0000')
        
        ttk.Button(deploy_buttons, text="⚔️ Rozstaw",
                  command=self.deploy_army_to_map,
                  style='Tiny.Military.TButton').pack(fill=tk.X, pady=1)
        
        ttk.Button(deploy_buttons, text="📋 Info", 
                  command=self.preview_quarter_info,
                  style='Tiny.Military.TButton').pack(fill=tk.X, pady=1)
        
        ttk.Button(deploy_buttons, text="🧹 Wyczyść",
                  command=self.clear_army_from_map,
                  style='Tiny.Danger.TButton').pack(fill=tk.X, pady=1)
        
        # Załaduj początkowe statystyki
        self.refresh_token_stats()
    
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
        
        ttk.Label(list_frame, text="📋 Skład armii:", style='Header.TLabel').pack(anchor='w')        # Scrolled text dla listy jednostek - mniejszy
        self.units_text = scrolledtext.ScrolledText(list_frame, height=8, width=40,
                                                   bg="white", fg="#556B2F",  # Tekst w kolorze dark olive
                                                   font=('Consolas', 8))
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
        """Tworzy pasek statusu - kompaktowy."""
        status_frame = tk.Frame(self.root, bg="#556B2F", height=25)  # Zmniejszona wysokość z 30 na 25
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = ttk.Label(status_frame, 
                                     text="⚡ Kreator Armii - Gotowy",
                                     style='Header.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)  # Zmniejszone pady z 5 na 2
        
        # Informacja o autorze - mniejsza
        author_label = ttk.Label(status_frame,
                                text="Kampania 1939 © 2025",
                                style='Header.TLabel')
        author_label.pack(side=tk.RIGHT, padx=5, pady=2)  # Zmniejszone pady z 5 na 2
    
    def on_nation_change(self, event=None):
        """Obsługuje zmianę nacji."""
        self.update_commander_options()
        self.update_preview()
        self.update_quarter_info()
    
    def on_commander_change(self, event=None):
        """Obsługuje zmianę dowódcy."""
        self.update_preview()
        self.update_quarter_info()

    def update_commander_options(self):
        """Aktualizuje opcje dowódców dla wybranej nacji."""
        nation = self.selected_nation.get()
        commanders = self.commanders.get(nation, [])
        
        self.commander_combo['values'] = commanders
        if commanders:
            self.selected_commander.set(commanders[0])
        
        # Aktualizuj info o ćwiartce po zmianie dowódcy
        self.update_quarter_info()
    
    def update_quarter_info(self):
        """Aktualizuje informacje o wybranej ćwiartce."""
        try:
            if hasattr(self, 'quarter_info'):
                nation = self.selected_nation.get()
                commander = self.selected_commander.get()
                quarter = self.get_quarter_for_nation_and_commander(nation, commander)
                
                info_text = f"📍 {quarter['description']}\n"
                info_text += f"🗺️ Q: {quarter['q_min']}-{quarter['q_max']}, "
                info_text += f"R: {quarter['r_min']}-{quarter['r_max']}"
                
                self.quarter_info.config(text=info_text)
        except:
            pass  # Ignoruj błędy podczas inicjalizacji
    
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
    def get_map_quarters(self):
        """Dzieli mapę na 4 ćwiartki dla dowódców."""
        return {
            "polska_gora": {    # 🇵🇱 Dowódca 1 - Północ
                "q_min": 0, "q_max": 27,
                "r_min": -20, "r_max": 0,
                "nation": "Polska",
                "commander": 1,
                "description": "🇵🇱 Północ (Dowódca 1)"
            },
            "polska_dol": {     # 🇵🇱 Dowódca 2 - Południe  
                "q_min": 0, "q_max": 27,
                "r_min": 0, "r_max": 20,
                "nation": "Polska", 
                "commander": 2,
                "description": "🇵🇱 Południe (Dowódca 2)"
            },
            "niemcy_gora": {    # 🇩🇪 Dowódca 5 - Północ
                "q_min": 28, "q_max": 55,
                "r_min": -20, "r_max": 0,
                "nation": "Niemcy",
                "commander": 5, 
                "description": "🇩🇪 Północ (Dowódca 5)"
            },
            "niemcy_dol": {     # 🇩🇪 Dowódca 6 - Południe
                "q_min": 28, "q_max": 55,
                "r_min": 0, "r_max": 20,
                "nation": "Niemcy",
                "commander": 6,
                "description": "🇩🇪 Południe (Dowódca 6)"
            }
        }
    
    def get_quarter_for_nation_and_commander(self, nation, commander_id):
        """Zwraca odpowiednią ćwiartkę dla nacji i dowódcy."""
        quarters = self.get_map_quarters()
        
        # Mapowanie dowódców na ćwiartki
        if nation == "Polska":
            if commander_id in [1, "1 (Polska)"]:
                return quarters["polska_gora"]
            elif commander_id in [2, "2 (Polska)"]:
                return quarters["polska_dol"]
        elif nation == "Niemcy":
            if commander_id in [5, "5 (Niemcy)"]:
                return quarters["niemcy_gora"] 
            elif commander_id in [6, "6 (Niemcy)"]:
                return quarters["niemcy_dol"]
        
        # Domyślnie pierwsza ćwiartka dla nacji
        if nation == "Polska":
            return quarters["polska_gora"]
        else:
            return quarters["niemcy_gora"]
    
    def is_hex_in_quarter(self, hex_coord, quarter):
        """Sprawdza czy hex należy do danej ćwiartki."""
        try:
            q, r = map(int, hex_coord.split(','))
            return (quarter["q_min"] <= q <= quarter["q_max"] and 
                   quarter["r_min"] <= r <= quarter["r_max"])
        except:
            return False
    
    def get_hexes_in_quarter(self, quarter):
        """Zwraca wszystkie heksy w danej ćwiartce."""
        hexes = []
        for q in range(quarter["q_min"], quarter["q_max"] + 1):
            for r in range(quarter["r_min"], quarter["r_max"] + 1):
                hex_coord = f"{q},{r}"
                hexes.append(hex_coord)
        return hexes

    # ...existing code...
    
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
            from edytory.token_editor_prototyp import TokenEditor
            
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
                 patch('tkinter.messagebox.showinfo', return_value=None), \
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
    
    # === FUNKCJE ZARZĄDZANIA FOLDERAMI ===
    
    def refresh_token_stats(self):
        """Odświeża statystyki żetonów w folderach."""
        try:
            tokens_dir = Path("assets/tokens")
            if not tokens_dir.exists():
                self.stats_label.config(text="📂 Folder assets/tokens nie istnieje")
                return
            
            # Sprawdź foldery nacji
            polish_count, polish_vp = self.count_nation_tokens("Polska")
            german_count, german_vp = self.count_nation_tokens("Niemcy")
            
            stats_text = f"📊 STATYSTYKI ŻETONÓW:\n"
            stats_text += f"🇵🇱 Polska: {polish_count} żetonów ({polish_vp} VP)\n"
            stats_text += f"🇩🇪 Niemcy: {german_count} żetonów ({german_vp} VP)"
            
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            self.stats_label.config(text=f"❌ Błąd: {str(e)}")
    
    def count_nation_tokens(self, nation):
        """Zlicza żetony i VP dla danej nacji."""
        tokens_dir = Path(f"assets/tokens/{nation}")
        if not tokens_dir.exists():
            return 0, 0
        
        count = 0
        total_vp = 0
        
        for token_folder in tokens_dir.iterdir():
            if token_folder.is_dir():
                json_file = token_folder / "token.json"
                if json_file.exists():
                    count += 1
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            total_vp += int(data.get('purchase_value', 0))
                    except:
                        pass  # Ignoruj błędy odczytu
        
        return count, total_vp
    
    def clean_polish_tokens(self):
        """Czyści polskie żetony z potwierdzeniem."""
        print("🔍 DEBUG: clean_polish_tokens() - WYWOŁANA!")
        print(f"🔍 DEBUG: Przekazuję do clean_nation_tokens('Polska', '🇵🇱')")
        self.clean_nation_tokens("Polska", "🇵🇱")
    
    def clean_german_tokens(self):
        """Czyści niemieckie żetony z potwierdzeniem."""
        print("🔍 DEBUG: clean_german_tokens() - WYWOŁANA!")
        print(f"🔍 DEBUG: Przekazuję do clean_nation_tokens('Niemcy', '🇩🇪')")
        self.clean_nation_tokens("Niemcy", "🇩🇪")
    
    def clean_all_tokens(self):
        """Czyści wszystkie żetony z potwierdzeniem."""
        if messagebox.askyesno("⚠️ UWAGA!", 
                              "Czy na pewno chcesz usunąć WSZYSTKIE żetony?\n\n"
                              "Ta operacja nie może być cofnięta!\n\n"
                              "🗑️ Zostaną usunięte:\n"
                              "• Wszystkie polskie żetony\n"
                              "• Wszystkie niemieckie żetony\n"                              "• Plik index.json"):
            
            try:
                tokens_dir = Path("assets/tokens")
                
                if tokens_dir.exists():
                    # Usuń foldery nacji
                    for nation_dir in tokens_dir.iterdir():
                        if nation_dir.is_dir() and nation_dir.name in ["Polska", "Niemcy"]:
                            shutil.rmtree(nation_dir)
                      # Usuń index.json
                    index_file = tokens_dir / "index.json"
                    if index_file.exists():
                        index_file.unlink()
                
                # Wyczyść start_tokens.json
                print("🔍 DEBUG: Czyszczę start_tokens.json...")
                self.clear_all_start_tokens()
                
                self.refresh_token_stats()
                messagebox.showinfo("✅ Sukces!", "Wszystkie żetony zostały usunięte.\nMapa została wyczyszczona z żetonów.")
                
            except Exception as e:                messagebox.showerror("❌ Błąd", f"Błąd podczas usuwania:\n{str(e)}")
    
    def clean_nation_tokens(self, nation, flag):
        """Czyści żetony wybranej nacji z potwierdzeniem."""
        print(f"🔍 DEBUG: clean_nation_tokens() - WYWOŁANA dla {nation} {flag}")
        
        # Sprawdź ile żetonów do usunięcia
        print(f"🔍 DEBUG: Sprawdzam żetony dla {nation}...")
        count, vp = self.count_nation_tokens(nation)
        print(f"🔍 DEBUG: Znaleziono {count} żetonów, {vp} VP dla {nation}")        
        if count == 0:
            print(f"🔍 DEBUG: Brak żetonów {nation} - wyświetlam dialog info")
            messagebox.showinfo("ℹ️ Info", f"Brak żetonów {flag} {nation} do usunięcia.")
            return
        
        print(f"🔍 DEBUG: Wyświetlam dialog potwierdzenia dla {count} żetonów {nation}")
        if messagebox.askyesno("⚠️ POTWIERDŹ USUNIĘCIE",
                              f"Czy na pewno chcesz usunąć żetony {flag} {nation}?\n\n"
                              f"🗑️ Do usunięcia:\n"
                              f"• {count} żetonów\n"
                              f"• {vp} VP łącznie\n\n"                              f"Ta operacja nie może być cofnięta!"):
            
            print(f"🔍 DEBUG: Użytkownik potwierdził usunięcie {nation}")
            
            try:
                nation_dir = Path(f"assets/tokens/{nation}")
                print(f"🔍 DEBUG: Próbuję usunąć folder: {nation_dir}")
                print(f"🔍 DEBUG: Folder istnieje: {nation_dir.exists()}")
                
                if nation_dir.exists():
                    print(f"🔍 DEBUG: Wywołuję shutil.rmtree({nation_dir})")
                    shutil.rmtree(nation_dir)
                    print(f"🔍 DEBUG: shutil.rmtree() zakończone!")
                    print(f"🔍 DEBUG: Folder istnieje po usunięciu: {nation_dir.exists()}")
                  # Aktualizuj index.json
                print(f"🔍 DEBUG: Aktualizuję index.json...")
                self.update_index_after_deletion(nation)
                
                # Wyczyść start_tokens.json dla usuwanej nacji
                print(f"🔍 DEBUG: Czyszczę start_tokens.json dla {nation}...")
                self.clear_nation_from_start_tokens(nation)
                
                print(f"🔍 DEBUG: Odświeżam statystyki...")
                self.refresh_token_stats()
                
                print(f"🔍 DEBUG: Wyświetlam dialog sukcesu...")
                messagebox.showinfo("✅ Sukces!", 
                                   f"Usunięto {count} żetonów {flag} {nation} ({vp} VP).\n"
                                   f"Mapa została wyczyszczona z żetonów tej nacji.")
                print(f"🔍 DEBUG: Operacja zakończona pomyślnie!")
                
            except Exception as e:
                print(f"🔍 DEBUG: BŁĄD podczas usuwania: {e}")
                print(f"🔍 DEBUG: Typ błędu: {type(e).__name__}")
                messagebox.showerror("❌ Błąd", f"Błąd podczas usuwania:\n{str(e)}")
        else:
            print(f"🔍 DEBUG: Użytkownik anulował usunięcie {nation}")
    
    def update_index_after_deletion(self, deleted_nation):
        """Aktualizuje index.json po usunięciu żetonów nacji."""
        try:
            index_file = Path("assets/tokens/index.json")
            if not index_file.exists():
                return
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # Usuń żetony usuniętej nacji z indeksu
            if deleted_nation in index_data:
                del index_data[deleted_nation]
            
            # Zapisz zaktualizowany indeks
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Błąd aktualizacji index.json: {e}")
    
    def clear_nation_from_start_tokens(self, nation):
        """Usuwa żetony wybranej nacji z start_tokens.json."""
        try:
            start_tokens_path = Path("assets/start_tokens.json")
            print(f"🔍 DEBUG: clear_nation_from_start_tokens() - ścieżka: {start_tokens_path}")
            
            if not start_tokens_path.exists():
                print(f"🔍 DEBUG: Plik start_tokens.json nie istnieje - tworzę pusty")
                empty_data = {"tokens": {}}
                with open(start_tokens_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_data, f, indent=2, ensure_ascii=False)
                return
            
            # Wczytaj istniejące dane
            with open(start_tokens_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tokens = data.get("tokens", {})
            print(f"🔍 DEBUG: Wczytano {len(tokens)} żetonów z start_tokens.json")
            
            # Znajdź żetony do usunięcia (po prefiksie nazwy)
            tokens_to_remove = []
            for token_id, token_data in tokens.items():
                token_name = token_data.get("name", "")
                # Sprawdź czy żeton należy do usuwanej nacji (na podstawie nazwy)
                if (nation == "Polska" and any(prefix in token_name.lower() for prefix in ["pol", "poland", "1939_pol"])) or \
                   (nation == "Niemcy" and any(prefix in token_name.lower() for prefix in ["ger", "german", "1939_ger"])):
                    tokens_to_remove.append(token_id)
            
            print(f"🔍 DEBUG: Znaleziono {len(tokens_to_remove)} żetonów {nation} do usunięcia z mapy")
            
            # Usuń żetony
            for token_id in tokens_to_remove:
                del tokens[token_id]
            
            # Zapisz zaktualizowane dane
            data["tokens"] = tokens
            with open(start_tokens_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ DEBUG: Usunięto {len(tokens_to_remove)} żetonów {nation} z start_tokens.json")
            
        except Exception as e:
            print(f"❌ BŁĄD clear_nation_from_start_tokens: {e}")
    
    def clear_all_start_tokens(self):
        """Usuwa wszystkie żetony z start_tokens.json."""
        try:
            start_tokens_path = Path("assets/start_tokens.json")
            print(f"🔍 DEBUG: clear_all_start_tokens() - ścieżka: {start_tokens_path}")
            
            empty_data = {"tokens": {}}
            
            with open(start_tokens_path, 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ DEBUG: Wyczyszczono start_tokens.json - wszystkie żetony usunięte z mapy")
            
        except Exception as e:
            print(f"❌ BŁĄD clear_all_start_tokens: {e}")

    def deploy_army_to_map(self):
        """Rozstawia utworzoną armię na mapie według wybranej ćwiartki."""
        try:
            print("🔍 DEBUG: deploy_army_to_map() - WYWOŁANA!")
            print(f"🔍 DEBUG: self.created_units = {self.created_units}")
            print(f"🔍 DEBUG: len(self.created_units) = {len(self.created_units) if self.created_units else None}")
            
            # Sprawdź czy armia została utworzona (albo w zmiennej albo w folderach)
            if not self.created_units:
                print("❌ DEBUG: Brak self.created_units - sprawdzam foldery żetonów...")
                
                # Sprawdź czy są żetony w folderach
                nation = self.selected_nation.get()
                print(f"🔍 DEBUG: Sprawdzam żetony dla nacji: {nation}")
                
                tokens_folder = Path(f"assets/tokens/{nation}")
                print(f"🔍 DEBUG: Ścieżka foldera: {tokens_folder}")
                print(f"🔍 DEBUG: Folder istnieje: {tokens_folder.exists()}")
                
                if tokens_folder.exists():
                    token_folders = [f.name for f in tokens_folder.iterdir() if f.is_dir()]
                    print(f"🔍 DEBUG: Znalezione foldery żetonów: {token_folders}")
                    
                    if token_folders:
                        print(f"✅ DEBUG: Znaleziono {len(token_folders)} żetonów w folderach")
                        # Wczytaj żetony z folderów
                        self.created_units = self.load_tokens_from_folders(nation)
                        print(f"🔍 DEBUG: Wczytane żetony: {len(self.created_units)} sztuk")
                        print("✅ DEBUG: Żetony wczytane z folderów do self.created_units")
                    else:
                        print("❌ DEBUG: Brak folderów żetonów")
                        messagebox.showwarning("⚠️ Uwaga", 
                                             f"Brak żetonów dla nacji {nation}!\n\n"
                                             f"Najpierw utwórz armię, a potem ją rozstaw!")
                        return
                else:
                    print("❌ DEBUG: Folder żetonów nie istnieje")
                    messagebox.showwarning("⚠️ Uwaga", 
                                         "Najpierw utwórz armię, a potem ją rozstaw!")
                    return
            
            print(f"✅ DEBUG: Mamy {len(self.created_units)} żetonów do rozstawienia")
            
            # Pobierz parametry
            nation = self.selected_nation.get()
            commander = self.selected_commander.get()
            print(f"🔍 DEBUG: Nacja: {nation}, Dowódca: {commander}")
            
            # Znajdź odpowiednią ćwiartkę
            quarter = self.get_quarter_for_nation_and_commander(nation, commander)
            print(f"🔍 DEBUG: Wybrana ćwiartka: {quarter['description']}")
            
            # Potwierdź rozstawianie
            if messagebox.askyesno("🗺️ ROZSTAWIANIE ARMII",
                                  f"Rozstawić armię w ćwiartce:\n\n"
                                  f"📍 {quarter['description']}\n"
                                  f"📊 {len(self.created_units)} żetonów\n"
                                  f"🎖️ Dowódca: {commander}\n\n"
                                  f"Kontynuować?"):
                
                print("✅ DEBUG: Użytkownik potwierdził rozstawianie")
                deployed_count = self.perform_army_deployment(quarter)
                messagebox.showinfo("✅ Sukces!", 
                                   f"Rozstawiono {deployed_count} żetonów\n"
                                   f"w ćwiartce {quarter['description']}")
            else:
                print("❌ DEBUG: Użytkownik anulował rozstawianie")
                
        except Exception as e:
            print(f"❌ DEBUG: BŁĄD w deploy_army_to_map: {str(e)}")
            print(f"❌ DEBUG: Typ błędu: {type(e).__name__}")
            messagebox.showerror("❌ Błąd", f"Błąd rozstawiania: {str(e)}")
    
    def load_tokens_from_folders(self, nation):
        """Wczytuje żetony z folderów dla danej nacji."""
        print(f"🔍 DEBUG: load_tokens_from_folders({nation}) - WYWOŁANA!")
        tokens = []
        
        tokens_folder = Path(f"assets/tokens/{nation}")
        print(f"🔍 DEBUG: Sprawdzam folder: {tokens_folder}")
        
        if tokens_folder.exists():
            for token_folder in tokens_folder.iterdir():
                if token_folder.is_dir():
                    print(f"🔍 DEBUG: Sprawdzam folder żetonu: {token_folder.name}")
                    token_json = token_folder / "token.json"
                    if token_json.exists():
                        try:
                            with open(token_json, 'r', encoding='utf-8') as f:
                                token_data = json.load(f)
                                tokens.append({
                                    'name': token_folder.name,
                                    'data': token_data
                                })
                                print(f"✅ DEBUG: Wczytano żeton: {token_folder.name}")
                        except Exception as e:
                            print(f"❌ DEBUG: Błąd wczytywania {token_folder.name}: {e}")
        
        print(f"✅ DEBUG: Łącznie wczytano {len(tokens)} żetonów z folderów")
        return tokens
    
    def preview_quarter_info(self):
        """Pokazuje informacje o wybranej ćwiartce."""
        try:
            nation = self.selected_nation.get()
            commander = self.selected_commander.get()
            quarter = self.get_quarter_for_nation_and_commander(nation, commander)
            
            # Aktualizuj info label
            info_text = f"📍 {quarter['description']}\n"
            info_text += f"🗺️ Q: {quarter['q_min']}-{quarter['q_max']}, "
            info_text += f"R: {quarter['r_min']}-{quarter['r_max']}"
            
            self.quarter_info.config(text=info_text)
            
            # Pokaż szczegóły w dialog
            total_hexes = (quarter['q_max'] - quarter['q_min'] + 1) * (quarter['r_max'] - quarter['r_min'] + 1)
            
            messagebox.showinfo("📋 INFORMACJE O ĆWIARTCE",
                               f"🎖️ {quarter['description']}\n\n"
                               f"📏 Wymiary:\n"
                               f"   • Q: {quarter['q_min']} do {quarter['q_max']} ({quarter['q_max'] - quarter['q_min'] + 1} kolumn)\n"
                               f"   • R: {quarter['r_min']} do {quarter['r_max']} ({quarter['r_max'] - quarter['r_min'] + 1} wierszy)\n\n"
                               f"📊 Łącznie heksów: {total_hexes}\n"
                               f"🏴 Nacja: {quarter['nation']}\n"
                               f"👤 Dowódca: {quarter['commander']}")
                               
        except Exception as e:
            messagebox.showerror("❌ Błąd", f"Błąd podglądu: {str(e)}")
    
    def clear_army_from_map(self):
        """Usuwa armię z mapy (czysci start_tokens.json)."""
        if messagebox.askyesno("🧹 CZYSZCZENIE MAPY",
                              "Czy na pewno chcesz usunąć wszystkie żetony z mapy?\n\n"
                              "Ta operacja wyczyści plik start_tokens.json"):
            try:
                # Wyczyść plik start_tokens.json
                start_tokens_path = Path("assets/start_tokens.json")
                
                empty_data = {"tokens": {}}
                
                with open(start_tokens_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("✅ Sukces!", "Mapa została wyczyszczona z żetonów.")
                
            except Exception as e:
                messagebox.showerror("❌ Błąd", f"Błąd czyszczenia mapy: {str(e)}")

    def perform_army_deployment(self, quarter):
        """Wykonuje rzeczywiste rozstawianie armii w ćwiartce."""
        try:
            print(f"🔍 DEBUG: perform_army_deployment() - WYWOŁANA!")
            print(f"🔍 DEBUG: Ćwiartka: {quarter['description']}")
            print(f"🔍 DEBUG: Żetony do rozstawienia: {len(self.created_units)}")
            
            # Wczytaj mapę
            map_data_path = Path("data/map_data.json")
            print(f"🔍 DEBUG: Sprawdzam map_data.json: {map_data_path}")
            print(f"🔍 DEBUG: Plik istnieje: {map_data_path.exists()}")
            
            if not map_data_path.exists():
                raise Exception("Nie znaleziono pliku map_data.json")
            
            with open(map_data_path, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            print(f"✅ DEBUG: Wczytano map_data.json - główne sekcje: {list(map_data.keys())}")
            
            # Pobierz heksy z sekcji terrain
            terrain_data = map_data.get('terrain', {})
            print(f"✅ DEBUG: Sekcja terrain zawiera {len(terrain_data)} heksów")
            
            # Debug: pokaż przykładowe heksy
            example_hexes = list(terrain_data.keys())[:5]
            print(f"🔍 DEBUG: Przykładowe heksy z terrain: {example_hexes}")
            
            # Znajdź dostępne heksy w ćwiartce
            available_hexes = []
            all_hexes_in_quarter = []
            
            for hex_coord in terrain_data.keys():
                if self.is_hex_in_quarter(hex_coord, quarter):
                    available_hexes.append(hex_coord)
                # Debug: sprawdź wszystkie możliwe heksy w ćwiartce
                try:
                    q, r = map(int, hex_coord.split(','))
                    if (quarter["q_min"] <= q <= quarter["q_max"] and 
                        quarter["r_min"] <= r <= quarter["r_max"]):
                        all_hexes_in_quarter.append(hex_coord)
                except:
                    pass
            
            print(f"🔍 DEBUG: Dostępne heksy w ćwiartce: {len(available_hexes)}")
            print(f"🔍 DEBUG: Wszystkie teoretyczne heksy w ćwiartce: {len(all_hexes_in_quarter)}")
            print(f"🔍 DEBUG: Pierwsze 5 heksów: {available_hexes[:5]}")
            
            # Debug: sprawdź zakres współrzędnych w mapie
            q_coords = []
            r_coords = []
            for hex_coord in terrain_data.keys():
                try:
                    q, r = map(int, hex_coord.split(','))
                    q_coords.append(q)
                    r_coords.append(r)
                except:
                    pass
            
            if q_coords and r_coords:
                print(f"🔍 DEBUG: Rzeczywisty zakres Q w mapie: {min(q_coords)} do {max(q_coords)}")
                print(f"🔍 DEBUG: Rzeczywisty zakres R w mapie: {min(r_coords)} do {max(r_coords)}")
                print(f"🔍 DEBUG: Ćwiartka oczekuje Q: {quarter['q_min']}-{quarter['q_max']}, R: {quarter['r_min']}-{quarter['r_max']}")
            
            if not available_hexes:
                print("❌ DEBUG: Brak dostępnych heksów w ćwiartce!")
                # Sprawdź czy ćwiartka w ogóle pokrywa się z mapą
                print(f"🔍 DEBUG: Sprawdzam pokrycie ćwiartki z mapą...")
                if q_coords and r_coords:
                    map_q_min, map_q_max = min(q_coords), max(q_coords)
                    map_r_min, map_r_max = min(r_coords), max(r_coords)
                    
                    overlap_q = not (quarter['q_max'] < map_q_min or quarter['q_min'] > map_q_max)
                    overlap_r = not (quarter['r_max'] < map_r_min or quarter['r_min'] > map_r_max)
                    
                    print(f"🔍 DEBUG: Pokrycie Q: {overlap_q}, Pokrycie R: {overlap_r}")
                    
                    if not overlap_q or not overlap_r:
                        raise Exception(f"Ćwiartka {quarter['description']} nie pokrywa się z mapą!\n"
                                      f"Mapa: Q({map_q_min}-{map_q_max}), R({map_r_min}-{map_r_max})\n"
                                      f"Ćwiartka: Q({quarter['q_min']}-{quarter['q_max']}), R({quarter['r_min']}-{quarter['r_max']})")
                
                raise Exception(f"Brak dostępnych heksów w ćwiartce {quarter['description']}")
              # Losowo rozstaw żetony
            random.shuffle(available_hexes)
            
            deployed_tokens = []
            deployed_count = 0
            
            for i, unit in enumerate(self.created_units):
                if i >= len(available_hexes):
                    print(f"⚠️ DEBUG: Więcej żetonów ({len(self.created_units)}) niż dostępnych heksów ({len(available_hexes)})")
                    break  # Więcej żetonów niż dostępnych heksów
                
                hex_coord = available_hexes[i]
                token_name = unit.get('name', f'token_{i}')
                
                # Parsuj współrzędne
                q, r = map(int, hex_coord.split(','))
                
                # Format zgodny z load_tokens
                deployed_tokens.append({
                    "id": token_name,
                    "q": q,
                    "r": r
                })
                deployed_count += 1
                
                if i < 5:  # Debug pierwszych 5
                    print(f"🔍 DEBUG: Rozstawiam żeton {i+1}: {token_name} na {hex_coord}")
            
            print(f"✅ DEBUG: Rozstawiono {deployed_count} żetonów")
            
            # Zapisz do start_tokens.json - format to lista, nie słownik!
            start_tokens_path = Path("assets/start_tokens.json")
            start_tokens_path.parent.mkdir(exist_ok=True)
            
            start_tokens_data = deployed_tokens
            
            with open(start_tokens_path, 'w', encoding='utf-8') as f:
                json.dump(start_tokens_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ DEBUG: Zapisano do {start_tokens_path}")
            
            return deployed_count
            
        except Exception as e:
            print(f"❌ DEBUG: BŁĄD w perform_army_deployment: {str(e)}")
            print(f"❌ DEBUG: Typ błędu: {type(e).__name__}")
            raise Exception(f"Błąd podczas rozstawiania: {str(e)}")

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
