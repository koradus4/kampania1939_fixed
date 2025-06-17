"""
PRAWDZIWY Automatyczny twórca żetonów - faktycznie używa metody save_token() 
z Token Editor do stworzenia armii dowódcy 1 przez wywołanie prawdziwego zapisu
"""

import tkinter as tk
import time
import threading
from pathlib import Path
import sys
import json
from unittest.mock import patch

# Dodaj ścieżkę do edytorów (z nowego miejsca)
import os
project_root = Path(__file__).parent.parent.parent  # ../../
sys.path.append(str(project_root / "edytory"))

class RealAutoTokenCreator:
    def __init__(self):
        self.editor = None
        self.current_unit = 0
        self.army_units = [
            {
                "name": "1. Pluton Grenadierów",
                "nation": "Polska",
                "unit_type": "P",
                "unit_size": "Pluton",
                "movement_points": "2",
                "attack_range": "1", 
                "attack_value": "8",
                "combat_value": "8",
                "defense_value": "10",
                "unit_maintenance": "2",
                "purchase_value": "15",
                "sight_range": "3",
                "support": "drużyna granatników"
            },
            {
                "name": "1. Kompania Piechoty Zmotoryzowanej",
                "nation": "Polska", 
                "unit_type": "P",
                "unit_size": "Kompania",
                "movement_points": "3",
                "attack_range": "1",
                "attack_value": "12",
                "combat_value": "12", 
                "defense_value": "14",
                "unit_maintenance": "4",
                "purchase_value": "25",
                "sight_range": "3",
                "support": "sam. ciężarowy Fiat 621"
            },
            {
                "name": "1. Pluton Czołgów Lekkich",
                "nation": "Polska",
                "unit_type": "TL",
                "unit_size": "Pluton", 
                "movement_points": "4",
                "attack_range": "1",
                "attack_value": "10",
                "combat_value": "10",
                "defense_value": "12",
                "unit_maintenance": "3", 
                "purchase_value": "30",
                "sight_range": "3",
                "support": ""
            },
            {
                "name": "1. Bateria Artylerii Polowej",
                "nation": "Polska",
                "unit_type": "AL",
                "unit_size": "Pluton",
                "movement_points": "2",
                "attack_range": "3",
                "attack_value": "15", 
                "combat_value": "6",
                "defense_value": "6",
                "unit_maintenance": "3",
                "purchase_value": "35",
                "sight_range": "4",
                "support": "obserwator"
            },
            {
                "name": "1. Szwadron Rozpoznawczy", 
                "nation": "Polska",
                "unit_type": "Z",
                "unit_size": "Pluton",
                "movement_points": "6",
                "attack_range": "1",
                "attack_value": "6",
                "combat_value": "6",
                "defense_value": "8",
                "unit_maintenance": "2",
                "purchase_value": "20", 
                "sight_range": "5",
                "support": ""
            }
        ]
    
    def start_creation(self):
        """Uruchamia Token Editor i rozpoczyna automatyczne tworzenie."""
        print("🎖️ PRAWDZIWY AUTOMATYCZNY TWÓRCA ARMII DOWÓDCY 1")
        print("🚀 Uruchamianie Token Editor...")
        
        # Import i uruchomienie Token Editor
        from token_editor_prototyp import TokenEditor
        
        root = tk.Tk()
        self.editor = TokenEditor(root)
        
        # Ustawienie domyślnego dowódcy (1 - Polska)
        if hasattr(self.editor, 'selected_commander'):
            self.editor.selected_commander.set("1 (Polska)")
        
        # Zaplanuj automatyczne wypełnianie po uruchomieniu
        root.after(1000, self.start_auto_fill)  # 1 sekunda na załadowanie
        
        print("📝 Token Editor uruchomiony!")
        print("⏰ Za 1 sekundę rozpocznie się automatyczne wypełnianie...")
        
        root.mainloop()
    
    def start_auto_fill(self):
        """Rozpoczyna automatyczne wypełnianie pierwszej jednostki."""
        if self.current_unit < len(self.army_units):
            print(f"\n🎨 TWORZENIE ŻETONU {self.current_unit + 1}/5:")
            print(f"   📋 {self.army_units[self.current_unit]['name']}")
            self.fill_current_unit()
        else:
            print("\n🎉 WSZYSTKIE ŻETONY UTWORZONE!")
            self.show_completion_summary()
    
    def fill_current_unit(self):
        """Wypełnia formularz dla aktualnej jednostki."""
        unit = self.army_units[self.current_unit]
        
        try:
            # Ustaw podstawowe pola
            self.editor.nation.set(unit["nation"])
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
            print(f"   🎨 Klik 'Podgląd' aby zobaczyć żeton")
            print(f"   💾 Wywołuję prawdziwy zapis żetonu...")
            
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
            print(f"   👁️ Podgląd wygenerowany automatycznie")
            
            # Automatycznie zapisz żeton prawdziwą metodą po 1 sekundzie
            self.editor.root.after(1000, self.real_save)
            
        except Exception as e:
            print(f"   ❌ Błąd podglądu: {e}")
            self.next_unit()
    
    def real_save(self):
        """Wywołuje prawdziwą metodę save_token() z Token Editor."""
        try:
            unit = self.army_units[self.current_unit]
            print(f"   💾 PRAWDZIWY ZAPIS: {unit['name']}")
            
            # Mockowanie dialogów aby uniknąć interakcji z użytkownikiem
            with patch('tkinter.messagebox.askyesno', return_value=True), \
                 patch('tkinter.simpledialog.askstring', return_value=unit['name']):
                
                # Wywołaj prawdziwą metodę save_token()
                self.editor.save_token()
                
            print(f"   ✅ Żeton zapisany prawdziwą metodą Token Editor!")
            
            # Przejdź do następnej jednostki po 2 sekundach
            self.editor.root.after(2000, self.next_unit)
            
        except Exception as e:
            print(f"   ❌ Błąd prawdziwego zapisu: {e}")
            self.next_unit()
    
    def next_unit(self):
        """Przechodzi do następnej jednostki."""
        self.current_unit += 1
        
        if self.current_unit < len(self.army_units):
            print(f"\n⏭️ NASTĘPNA JEDNOSTKA...")
            time.sleep(1)
            self.start_auto_fill()
        else:
            print(f"\n🏁 KONIEC PROCESU TWORZENIA!")
            self.show_completion_summary()
    
    def show_completion_summary(self):
        """Pokazuje podsumowanie ukończonego procesu."""
        print("\n" + "="*60)
        print("🎉 ARMIA DOWÓDCY 1 - PROCES ZAKOŃCZONY!")
        print("="*60)
        
        total_value = sum(int(unit["purchase_value"]) for unit in self.army_units)
        
        print(f"📊 STATYSTYKI ARMII:")
        print(f"   • Jednostek: {len(self.army_units)}")
        print(f"   • Łączna wartość: {total_value} VP")
        print(f"   • Średni koszt: {total_value // len(self.army_units)} VP")
        
        print(f"\n🎯 BALANS:")
        infantry = len([u for u in self.army_units if u["unit_type"] == "P"])
        armor = len([u for u in self.army_units if u["unit_type"] == "TL"])
        artillery = len([u for u in self.army_units if u["unit_type"] == "AL"]) 
        recon = len([u for u in self.army_units if u["unit_type"] == "Z"])
        
        print(f"   • Piechota: {infantry}")
        print(f"   • Pancerne: {armor}")
        print(f"   • Artyleria: {artillery}")
        print(f"   • Rozpoznanie: {recon}")        
        print(f"\n📁 ŻETONY ZAPISANE W:")
        print(f"   assets/tokens/Polska/[katalog_z_pełną_nazwą]/")
        print(f"   Każdy żeton ma plik token.json i token.png")
        
        print(f"\n✅ ARMIA GOTOWA DO WALKI!")
        
        # Sprawdź co faktycznie zostało utworzone
        self.verify_created_tokens()
    
    def verify_created_tokens(self):
        """Sprawdza czy żetony zostały faktycznie utworzone."""
        print(f"\n🔍 WERYFIKACJA UTWORZONYCH ŻETONÓW:")
        
        # Ścieżka względem katalogu głównego projektu
        project_root = Path(__file__).parent.parent.parent
        tokens_path = project_root / "assets" / "tokens" / "Polska"
        
        if not tokens_path.exists():
            print(f"   ❌ Katalog {tokens_path} nie istnieje!")
            return
        
        created_tokens = list(tokens_path.iterdir())
        print(f"   📁 Znaleziono {len(created_tokens)} katalogów żetonów")
        
        for token_dir in created_tokens:
            if token_dir.is_dir():
                json_file = token_dir / "token.json"
                png_file = token_dir / "token.png"
                
                print(f"   📋 {token_dir.name}:")
                print(f"      JSON: {'✅' if json_file.exists() else '❌'}")
                print(f"      PNG:  {'✅' if png_file.exists() else '❌'}")
                
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        print(f"      Nazwa: {data.get('label', 'brak')}")
                        print(f"      Typ: {data.get('unitType', 'brak')}")
                        print(f"      Wartość: {data.get('price', 'brak')} VP")
                    except Exception as e:
                        print(f"      ❌ Błąd odczytu JSON: {e}")
          # Sprawdź index.json
        project_root = Path(__file__).parent.parent.parent
        index_file = project_root / "assets" / "tokens" / "index.json"
        if index_file.exists():
            print(f"\n   📚 Index.json został automatycznie utworzony ✅")
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                print(f"   📊 Index zawiera {len(index_data)} żetonów")
            except Exception as e:
                print(f"   ❌ Błąd odczytu index.json: {e}")
        else:
            print(f"   ❌ Index.json nie został utworzony!")

def main():
    """Główna funkcja uruchamiająca automatyczne tworzenie."""
    
    print("🎖️ PRAWDZIWY AUTOMATYCZNY TWÓRCA ARMII DOWÓDCY 1")
    print("=" * 50)
    print("🎯 Używa prawdziwej metody save_token() z Token Editor")
    print("📋 Tworzenie 5 zbalansowanych żetonów dla dowódcy 1")
    print("🎨 Automatycznie tworzy pliki PNG i JSON")
    print("📁 Tworzy pełną strukturę katalogów")
    print()
    
    # Uruchom bez pytania
    creator = RealAutoTokenCreator()
    creator.start_creation()

if __name__ == "__main__":
    main()
