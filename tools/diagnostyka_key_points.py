#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Narzędzie diagnostyczne dla systemu punktów specjalnych (key_points)
"""

import json
import os
import sys

# Dodaj ścieżkę do głównego katalogu projektu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.engine import GameEngine
from engine.player import Player
from core.ekonomia import EconomySystem

def diagnose_key_points_system():
    """Kompleksowa diagnostyka systemu key_points"""
    
    print("=" * 60)
    print("DIAGNOSTYKA SYSTEMU PUNKTÓW SPECJALNYCH (KEY_POINTS)")
    print("=" * 60)
    
    # 1. Sprawdź plik mapy
    print("\n1. SPRAWDZANIE PLIKU MAPY")
    print("-" * 30)
    
    map_path = "data/map_data.json"
    if not os.path.exists(map_path):
        print(f"❌ BŁĄD: Plik mapy nie istnieje: {map_path}")
        return
    
    print(f"✅ Plik mapy istnieje: {map_path}")
    
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
        print("✅ Plik mapy został poprawnie załadowany")
    except Exception as e:
        print(f"❌ BŁĄD wczytywania pliku mapy: {e}")
        return
    
    # Sprawdź key_points w pliku mapy
    key_points = map_data.get('key_points', {})
    if not key_points:
        print("❌ BRAK key_points w pliku mapy!")
        print("💡 Dodaj key_points do data/map_data.json w formacie:")
        print('   "key_points": {')
        print('     "10,-4": {"type": "miasto", "value": 50},')
        print('     "15,2": {"type": "fortyfikacja", "value": 30}')
        print('   }')
        return
    
    print(f"✅ Znaleziono {len(key_points)} punktów specjalnych:")
    for hex_id, point_data in key_points.items():
        print(f"   - {hex_id}: {point_data}")
    
    # 2. Sprawdź inicjalizację GameEngine    print("\n2. SPRAWDZANIE GAMEENGINE")
    print("-" * 30)
    
    try:
        game_engine = GameEngine(
            map_path="data/map_data.json",
            tokens_index_path="assets/tokens/index.json",
            tokens_start_path="assets/start_tokens.json",
            seed=42,
            read_only=True  # Zapobiega nadpisywaniu pliku mapy
        )
        print("✅ GameEngine został zainicjalizowany")
    except Exception as e:
        print(f"❌ BŁĄD inicjalizacji GameEngine: {e}")
        return
    
    # Sprawdź key_points_state
    if hasattr(game_engine, 'key_points_state'):
        print(f"✅ key_points_state istnieje: {len(game_engine.key_points_state)} punktów")
        for hex_id, state in game_engine.key_points_state.items():
            print(f"   - {hex_id}: {state}")
    else:
        print("❌ BRAK key_points_state w GameEngine!")
        return
    
    # Sprawdź board.key_points
    if hasattr(game_engine.board, 'key_points'):
        print(f"✅ board.key_points istnieje: {len(game_engine.board.key_points)} punktów")
        for hex_id, point_data in game_engine.board.key_points.items():
            print(f"   - {hex_id}: {point_data}")
    else:
        print("❌ BRAK board.key_points!")
    
    # 3. Sprawdź żetony
    print("\n3. SPRAWDZANIE ŻETONÓW")
    print("-" * 30)
    
    print(f"✅ Załadowano {len(game_engine.tokens)} żetonów")
    
    tokens_with_positions = [t for t in game_engine.tokens if t.q is not None and t.r is not None]
    print(f"✅ Żetony z pozycjami: {len(tokens_with_positions)}")
    
    # Sprawdź, które żetony stoją na key_points
    tokens_on_key_points = []
    for token in tokens_with_positions:
        hex_id = f"{token.q},{token.r}"
        if hex_id in game_engine.key_points_state:
            tokens_on_key_points.append((token, hex_id))
    
    print(f"✅ Żetony na punktach specjalnych: {len(tokens_on_key_points)}")
    for token, hex_id in tokens_on_key_points:
        print(f"   - Żeton {token.id} ({token.owner}) na {hex_id}")
    
    # 4. Sprawdź graczy
    print("\n4. SPRAWDZANIE GRACZY")
    print("-" * 30)
    
    # Stwórz testowych graczy
    players = [
        Player(1, "Polska", "Generał", 5, "test.png"),
        Player(2, "Polska", "Dowódca", 5, "test.png"),
        Player(3, "Polska", "Dowódca", 5, "test.png"),
        Player(4, "Niemcy", "Generał", 5, "test.png"),
        Player(5, "Niemcy", "Dowódca", 5, "test.png"),
        Player(6, "Niemcy", "Dowódca", 5, "test.png"),
    ]
    
    # Dodaj systemy ekonomii
    for p in players:
        p.economy = EconomySystem()
    
    game_engine.players = players
    
    generals = [p for p in players if p.role.lower() == 'generał']
    print(f"✅ Znaleziono {len(generals)} generałów:")
    for general in generals:
        print(f"   - {general.nation} Generał (id={general.id}), punkty: {general.economy.economic_points}")
    
    # 5. Symuluj process_key_points
    print("\n5. SYMULACJA PROCESS_KEY_POINTS")
    print("-" * 30)
    
    print("🔄 Wywołuję process_key_points...")
    
    # Zapisz stan przed
    before_state = {}
    for general in generals:
        before_state[general.id] = general.economy.economic_points
    
    try:
        game_engine.process_key_points(players)
        print("✅ process_key_points wykonane bez błędów")
    except Exception as e:
        print(f"❌ BŁĄD w process_key_points: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Sprawdź zmiany
    print("\n6. ANALIZA WYNIKÓW")
    print("-" * 30)
    
    changes_detected = False
    for general in generals:
        before = before_state[general.id]
        after = general.economy.economic_points
        if after != before:
            print(f"✅ {general.nation} Generał: {before} → {after} (+{after-before})")
            changes_detected = True
        else:
            print(f"❌ {general.nation} Generał: {before} → {after} (brak zmian)")
    
    if not changes_detected:
        print("\n❌ BRAK ZMIAN W PUNKTACH EKONOMICZNYCH!")
        print("🔍 Możliwe przyczyny:")
        print("   1. Żaden żeton nie stoi na punktach specjalnych")
        print("   2. Błąd w identyfikacji właścicieli żetonów")
        print("   3. Błąd w mapowaniu nacji do generałów")
        print("   4. Punkty specjalne mają wartość 0")
    else:
        print("\n✅ SYSTEM PUNKTÓW SPECJALNYCH DZIAŁA POPRAWNIE!")
    
    # 7. Szczegółowa analiza problemu
    print("\n7. SZCZEGÓŁOWA ANALIZA")
    print("-" * 30)
    
    if tokens_on_key_points:
        print("🔍 Analiza żetonów na punktach specjalnych:")
        
        for token, hex_id in tokens_on_key_points:
            print(f"\n   Żeton {token.id} na {hex_id}:")
            print(f"     - Owner: '{token.owner}'")
            
            # Wyciągnij nację z ownera
            if hasattr(token, 'owner') and token.owner:
                try:
                    nation = token.owner.split("(")[-1].replace(")", "").strip()
                    print(f"     - Wyciągnięta nacja: '{nation}'")
                    
                    # Znajdź generała dla tej nacji
                    general = None
                    for p in players:
                        if p.nation == nation and p.role.lower() == 'generał':
                            general = p
                            break
                    
                    if general:
                        print(f"     - Znaleziony generał: {general.nation} (id={general.id})")
                        
                        # Sprawdź key_point
                        kp = game_engine.key_points_state.get(hex_id)
                        if kp:
                            print(f"     - Key point: {kp}")
                            give = int(0.1 * kp['initial_value'])
                            if give < 1:
                                give = 1
                            if kp['current_value'] > 0:
                                print(f"     - Powinien dostać: {give} punktów")
                            else:
                                print(f"     - Punkt wyczerpany (current_value: {kp['current_value']})")
                        else:
                            print(f"     - BŁĄD: brak key_point dla {hex_id}")
                    else:
                        print(f"     - BŁĄD: nie znaleziono generała dla nacji '{nation}'")
                        print(f"     - Dostępni generałowie: {[p.nation for p in generals]}")
                        
                except Exception as e:
                    print(f"     - BŁĄD wyciągania nacji: {e}")
            else:
                print(f"     - BŁĄD: brak ownera")
    else:
        print("❌ Żaden żeton nie stoi na punktach specjalnych!")
        print("💡 Przesuń żeton na heks z punktem specjalnym i spróbuj ponownie")
    
    print("\n" + "=" * 60)
    print("KONIEC DIAGNOSTYKI")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_key_points_system()
