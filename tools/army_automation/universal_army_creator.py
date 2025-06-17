"""
UNIWERSALNY Automatyczny twórca armii - tworzy armie dla wszystkich dowódców
Polskich (2, 3) i Niemieckich (5, 6) używając prawdziwej metody save_token()
"""

import tkinter as tk
import time
from pathlib import Path
import sys
import json
from unittest.mock import patch

# Dodaj ścieżkę do edytorów (z nowego miejsca)
import os
project_root = Path(__file__).parent.parent.parent  # ../../
sys.path.append(str(project_root / "edytory"))

class UniversalArmyCreator:
    def __init__(self):
        self.editor = None
        self.current_commander = 0
        self.current_unit = 0
        
        # Definicje armii dla wszystkich dowódców
        self.armies = {
            "2_Polska": {
                "commander": "2 (Polska)",
                "nation": "Polska", 
                "units": [
                    {
                        "name": "2. Batalion Piechoty Górskiej",
                        "unit_type": "P", "unit_size": "Batalion",
                        "movement_points": "3", "attack_range": "1", "attack_value": "15",
                        "combat_value": "15", "defense_value": "18", "unit_maintenance": "6",
                        "purchase_value": "45", "sight_range": "4", "support": "przewodnicy górski"
                    },
                    {
                        "name": "2. Dywizjon Artylerii Ciężkiej",
                        "unit_type": "AC", "unit_size": "Kompania", 
                        "movement_points": "1", "attack_range": "4", "attack_value": "20",
                        "combat_value": "8", "defense_value": "8", "unit_maintenance": "5",
                        "purchase_value": "50", "sight_range": "5", "support": "obserwator artyleryjski"
                    },
                    {
                        "name": "2. Pluton Czołgów Średnich",
                        "unit_type": "TŚ", "unit_size": "Pluton",
                        "movement_points": "3", "attack_range": "2", "attack_value": "12",
                        "combat_value": "12", "defense_value": "15", "unit_maintenance": "4",
                        "purchase_value": "40", "sight_range": "3", "support": ""
                    },
                    {
                        "name": "2. Kompania Samochodów Pancernych",
                        "unit_type": "TS", "unit_size": "Kompania",
                        "movement_points": "5", "attack_range": "1", "attack_value": "10",
                        "combat_value": "10", "defense_value": "12", "unit_maintenance": "3",
                        "purchase_value": "35", "sight_range": "4", "support": "radio"
                    }
                ]
            },
            
            "3_Polska": {
                "commander": "3 (Polska)",
                "nation": "Polska",
                "units": [
                    {
                        "name": "3. Pułk Ułanów Krakowskich",
                        "unit_type": "K", "unit_size": "Batalion",
                        "movement_points": "6", "attack_range": "1", "attack_value": "12",
                        "combat_value": "12", "defense_value": "10", "unit_maintenance": "4",
                        "purchase_value": "35", "sight_range": "5", "support": "szable"
                    },
                    {
                        "name": "3. Batalion Strzelców Podhalańskich",
                        "unit_type": "P", "unit_size": "Batalion",
                        "movement_points": "4", "attack_range": "2", "attack_value": "14",
                        "combat_value": "14", "defense_value": "16", "unit_maintenance": "5",
                        "purchase_value": "40", "sight_range": "4", "support": "snajperzy"
                    },
                    {
                        "name": "3. Bateria Artylerii Konnej",
                        "unit_type": "AL", "unit_size": "Kompania",
                        "movement_points": "4", "attack_range": "3", "attack_value": "16",
                        "combat_value": "8", "defense_value": "8", "unit_maintenance": "4",
                        "purchase_value": "42", "sight_range": "4", "support": "konie"
                    },
                    {
                        "name": "3. Pluton Tankietek",
                        "unit_type": "TL", "unit_size": "Pluton",
                        "movement_points": "5", "attack_range": "1", "attack_value": "8",
                        "combat_value": "8", "defense_value": "10", "unit_maintenance": "2",
                        "purchase_value": "25", "sight_range": "3", "support": ""
                    },
                    {
                        "name": "3. Oddział Rozpoznawczy",
                        "unit_type": "Z", "unit_size": "Pluton",
                        "movement_points": "7", "attack_range": "1", "attack_value": "5",
                        "combat_value": "5", "defense_value": "7", "unit_maintenance": "2",
                        "purchase_value": "18", "sight_range": "6", "support": "wywiad"
                    }
                ]
            },
            
            "5_Niemcy": {
                "commander": "5 (Niemcy)",
                "nation": "Niemcy",
                "units": [
                    {
                        "name": "5. Panzergrenadier Regiment",
                        "unit_type": "P", "unit_size": "Batalion",
                        "movement_points": "4", "attack_range": "1", "attack_value": "16",
                        "combat_value": "16", "defense_value": "18", "unit_maintenance": "6",
                        "purchase_value": "48", "sight_range": "3", "support": "Sd.Kfz. 251"
                    },
                    {
                        "name": "5. Panzer Abteilung",
                        "unit_type": "TŚ", "unit_size": "Kompania",
                        "movement_points": "4", "attack_range": "2", "attack_value": "18",
                        "combat_value": "15", "defense_value": "20", "unit_maintenance": "7",
                        "purchase_value": "60", "sight_range": "3", "support": "Panzer IV"
                    },
                    {
                        "name": "5. Artillerie Regiment",
                        "unit_type": "AC", "unit_size": "Batalion", 
                        "movement_points": "2", "attack_range": "5", "attack_value": "25",
                        "combat_value": "10", "defense_value": "10", "unit_maintenance": "8",
                        "purchase_value": "70", "sight_range": "5", "support": "leFH 18"
                    },
                    {
                        "name": "5. Aufklärungs Abteilung",
                        "unit_type": "Z", "unit_size": "Kompania",
                        "movement_points": "6", "attack_range": "1", "attack_value": "8",
                        "combat_value": "8", "defense_value": "10", "unit_maintenance": "3",
                        "purchase_value": "30", "sight_range": "6", "support": "Sd.Kfz. 222"
                    }
                ]
            },
            
            "6_Niemcy": {
                "commander": "6 (Niemcy)",
                "nation": "Niemcy", 
                "units": [
                    {
                        "name": "6. Infanterie Regiment",
                        "unit_type": "P", "unit_size": "Batalion",
                        "movement_points": "3", "attack_range": "1", "attack_value": "14",
                        "combat_value": "14", "defense_value": "16", "unit_maintenance": "5",
                        "purchase_value": "42", "sight_range": "3", "support": "MG 34"
                    },
                    {
                        "name": "6. Panzer Kompanie",
                        "unit_type": "TL", "unit_size": "Kompania",
                        "movement_points": "5", "attack_range": "1", "attack_value": "12",
                        "combat_value": "12", "defense_value": "14", "unit_maintenance": "4",
                        "purchase_value": "38", "sight_range": "3", "support": "Panzer II"
                    },
                    {
                        "name": "6. leichte Artillerie",
                        "unit_type": "AL", "unit_size": "Kompania",
                        "movement_points": "3", "attack_range": "3", "attack_value": "14",
                        "combat_value": "6", "defense_value": "6", "unit_maintenance": "3",
                        "purchase_value": "36", "sight_range": "4", "support": "leIG 18"
                    },
                    {
                        "name": "6. Flak Abteilung",
                        "unit_type": "AP", "unit_size": "Pluton",
                        "movement_points": "2", "attack_range": "2", "attack_value": "10",
                        "combat_value": "8", "defense_value": "8", "unit_maintenance": "3",
                        "purchase_value": "32", "sight_range": "4", "support": "Flak 38"
                    },
                    {
                        "name": "6. Pionier Zug",
                        "unit_type": "Z", "unit_size": "Pluton",
                        "movement_points": "3", "attack_range": "1", "attack_value": "6",
                        "combat_value": "6", "defense_value": "8", "unit_maintenance": "2",
                        "purchase_value": "22", "sight_range": "3", "support": "ładunki wybuchowe"
                    }
                ]
            }
        }
        
        # Lista armii do przetworzenia
        self.army_keys = list(self.armies.keys())
    
    def start_creation(self):
        """Uruchamia Token Editor i rozpoczyna automatyczne tworzenie wszystkich armii."""
        print("🎖️ UNIWERSALNY AUTOMATYCZNY TWÓRCA ARMII")
        print("=" * 60)
        print("🎯 Tworzy armie dla wszystkich dowódców:")
        for key, army in self.armies.items():
            commander = army["commander"]
            unit_count = len(army["units"])
            total_value = sum(int(unit["purchase_value"]) for unit in army["units"])
            print(f"   • {commander}: {unit_count} żetonów, {total_value} VP")
        print()
        
        # Import i uruchomienie Token Editor
        from token_editor_prototyp import TokenEditor
        
        root = tk.Tk()
        self.editor = TokenEditor(root)
        
        # Zaplanuj automatyczne wypełnianie po uruchomieniu
        root.after(1000, self.start_next_army)  # 1 sekunda na załadowanie
        
        print("📝 Token Editor uruchomiony!")
        print("⏰ Za 1 sekundę rozpocznie się automatyczne tworzenie armii...")
        
        root.mainloop()
    
    def start_next_army(self):
        """Rozpoczyna tworzenie następnej armii."""
        if self.current_commander < len(self.army_keys):
            army_key = self.army_keys[self.current_commander]
            army = self.armies[army_key]
            
            print(f"\n🎖️ ARMIA {self.current_commander + 1}/{len(self.army_keys)}: {army['commander']}")
            print(f"   🏴 Nacja: {army['nation']}")
            print(f"   📋 Jednostek: {len(army['units'])}")
            
            # Resetuj licznik jednostek dla nowej armii
            self.current_unit = 0
            
            # Rozpocznij tworzenie jednostek dla tej armii
            self.start_auto_fill()
        else:
            print(f"\n🎉 WSZYSTKIE ARMIE UTWORZONE!")
            self.show_final_summary()
    
    def start_auto_fill(self):
        """Rozpoczyna automatyczne wypełnianie następnej jednostki w aktualnej armii."""
        army_key = self.army_keys[self.current_commander]
        army = self.armies[army_key]
        
        if self.current_unit < len(army["units"]):
            unit = army["units"][self.current_unit]
            print(f"\n🎨 ŻETON {self.current_unit + 1}/{len(army['units'])}: {unit['name']}")
            self.fill_current_unit()
        else:
            print(f"\n✅ ARMIA {army['commander']} UKOŃCZONA!")
            
            # Przejdź do następnej armii
            self.current_commander += 1
            self.editor.root.after(2000, self.start_next_army)
    
    def fill_current_unit(self):
        """Wypełnia formularz dla aktualnej jednostki."""
        army_key = self.army_keys[self.current_commander]
        army = self.armies[army_key]
        unit = army["units"][self.current_unit]
        
        try:
            # Ustaw dowódcę i nację
            if hasattr(self.editor, 'selected_commander'):
                self.editor.selected_commander.set(army["commander"])
            self.editor.nation.set(army["nation"])
            
            # Ustaw podstawowe pola jednostki
            self.editor.unit_type.set(unit["unit_type"]) 
            self.editor.unit_size.set(unit["unit_size"])
            
            # Ustaw pola numeryczne
            self.editor.movement_points.set(unit["movement_points"])
            self.editor.attack_range.set(unit["attack_range"])
            self.editor.attack_value.set(unit["attack_value"])
            self.editor.combat_value.set(unit["combat_value"])
            self.editor.defense_value.set(unit["defense_value"])
            self.editor.unit_maintenance.set(unit["unit_maintenance"])
            self.editor.purchase_value.set(unit["purchase_value"])
            self.editor.sight_range.set(unit["sight_range"])
            
            # Ustaw wsparcie jeśli istnieje
            if unit["support"] and hasattr(self.editor, 'selected_support'):
                self.editor.selected_support.set(unit["support"])
            
            print(f"   ✅ Pola wypełnione")
            print(f"   💾 Zapisuję żeton...")
            
            # Zaplanuj automatyczny podgląd i zapis
            self.editor.root.after(500, self.auto_preview_and_save)
            
        except Exception as e:
            print(f"   ❌ Błąd wypełniania: {e}")
            self.next_unit()
    
    def auto_preview_and_save(self):
        """Automatycznie wywołuje podgląd i prawdziwy zapis."""
        try:
            # Najpierw wygeneruj podgląd
            self.editor.update_preview()
            print(f"   👁️ Podgląd wygenerowany")
            
            # Automatycznie zapisz żeton prawdziwą metodą po 1 sekundzie
            self.editor.root.after(1000, self.real_save)
            
        except Exception as e:
            print(f"   ❌ Błąd podglądu: {e}")
            self.next_unit()
    
    def real_save(self):
        """Wywołuje prawdziwą metodę save_token() z Token Editor."""
        try:
            army_key = self.army_keys[self.current_commander]
            army = self.armies[army_key]
            unit = army["units"][self.current_unit]
            
            print(f"   💾 PRAWDZIWY ZAPIS: {unit['name']}")
            
            # Mockowanie dialogów aby uniknąć interakcji z użytkownikiem
            with patch('tkinter.messagebox.askyesno', return_value=True), \
                 patch('tkinter.simpledialog.askstring', return_value=unit['name']):
                
                # Wywołaj prawdziwą metodę save_token()
                self.editor.save_token()
                
            print(f"   ✅ Żeton zapisany!")
            
            # Przejdź do następnej jednostki po 1 sekundzie
            self.editor.root.after(1000, self.next_unit)
            
        except Exception as e:
            print(f"   ❌ Błąd prawdziwego zapisu: {e}")
            self.next_unit()
    
    def next_unit(self):
        """Przechodzi do następnej jednostki w aktualnej armii."""
        self.current_unit += 1
        self.start_auto_fill()
    
    def show_final_summary(self):
        """Pokazuje podsumowanie wszystkich utworzonych armii."""
        print("\n" + "="*80)
        print("🎉 WSZYSTKIE ARMIE UTWORZONE - PODSUMOWANIE KOŃCOWE")
        print("="*80)
        
        total_armies = len(self.armies)
        total_units = sum(len(army["units"]) for army in self.armies.values())
        total_value = sum(sum(int(unit["purchase_value"]) for unit in army["units"]) 
                         for army in self.armies.values())
        
        print(f"📊 STATYSTYKI GLOBALNE:")
        print(f"   • Armii utworzonych: {total_armies}")
        print(f"   • Łączna liczba żetonów: {total_units}")
        print(f"   • Łączna wartość wszystkich armii: {total_value} VP")
        print(f"   • Średnia wartość armii: {total_value // total_armies} VP")
        
        print(f"\n🎯 PODZIAŁ PO ARMIACH:")
        for army_key, army in self.armies.items():
            commander = army["commander"]
            nation = army["nation"]
            unit_count = len(army["units"])
            army_value = sum(int(unit["purchase_value"]) for unit in army["units"])
            
            print(f"   🎖️ {commander} ({nation}):")
            print(f"      • Jednostek: {unit_count}")
            print(f"      • Wartość: {army_value} VP")
            
            # Podział typów jednostek
            types = {}
            for unit in army["units"]:
                unit_type = unit["unit_type"]
                types[unit_type] = types.get(unit_type, 0) + 1
            
            print(f"      • Typy: {', '.join(f'{t}({c})' for t, c in types.items())}")
        
        print(f"\n📁 ŻETONY ZAPISANE W:")
        print(f"   assets/tokens/Polska/ - polskie żetony")
        print(f"   assets/tokens/Niemcy/ - niemieckie żetony")
        print(f"   Każdy żeton ma plik token.json i token.png")
        
        print(f"\n✅ WSZYSTKIE ARMIE GOTOWE DO WALKI!")
        
        # Sprawdź co faktycznie zostało utworzone
        self.verify_created_tokens()
    
    def verify_created_tokens(self):
        """Sprawdza czy żetony zostały faktycznie utworzone dla wszystkich nacji."""
        print(f"\n🔍 WERYFIKACJA UTWORZONYCH ŻETONÓW:")
        
        project_root = Path(__file__).parent.parent.parent
        nations = ["Polska", "Niemcy"]
        
        for nation in nations:
            tokens_path = project_root / "assets" / "tokens" / nation
            
            if tokens_path.exists():
                created_tokens = [d for d in tokens_path.iterdir() if d.is_dir()]
                print(f"\n   🏴 {nation}: {len(created_tokens)} żetonów")
                
                for token_dir in created_tokens:
                    json_file = token_dir / "token.json"
                    png_file = token_dir / "token.png"
                    
                    json_ok = "✅" if json_file.exists() else "❌"
                    png_ok = "✅" if png_file.exists() else "❌"
                    print(f"      📋 {token_dir.name}: JSON {json_ok} PNG {png_ok}")
            else:
                print(f"\n   ❌ {nation}: katalog nie istnieje!")
        
        # Sprawdź index.json
        index_file = project_root / "assets" / "tokens" / "index.json"
        if index_file.exists():
            print(f"\n   📚 Index.json został automatycznie zaktualizowany ✅")
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                print(f"   📊 Index zawiera {len(index_data)} żetonów łącznie")
            except Exception as e:
                print(f"   ❌ Błąd odczytu index.json: {e}")
        else:
            print(f"   ❌ Index.json nie został utworzony!")

def main():
    """Główna funkcja uruchamiająca automatyczne tworzenie wszystkich armii."""
    
    print("🎖️ UNIWERSALNY AUTOMATYCZNY TWÓRCA ARMII")
    print("=" * 60)
    print("🎯 Tworzy zbalansowane armie dla wszystkich dowódców")
    print("🎨 Używa prawdziwej metody save_token() z Token Editor")
    print("📁 Tworzy pełną strukturę katalogów z PNG i JSON")
    print()
    
    creator = UniversalArmyCreator()
    creator.start_creation()

if __name__ == "__main__":
    main()
