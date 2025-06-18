#!/usr/bin/env python3
"""
Test funkcji load_tokens z nowym formatem start_tokens.json
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.token import load_tokens

def test_load_tokens():
    """Test funkcji load_tokens z aktualnym start_tokens.json."""
    try:
        print("🔍 Testowanie load_tokens...")
        
        index_path = "assets/tokens/index.json"
        start_path = "assets/start_tokens.json"
        
        if not os.path.exists(index_path):
            print(f"❌ Błąd: Brak pliku {index_path}")
            return False
            
        if not os.path.exists(start_path):
            print(f"❌ Błąd: Brak pliku {start_path}")
            return False
        
        # Wczytaj żetony
        tokens = load_tokens(index_path, start_path)
        
        print(f"✅ Wczytano {len(tokens)} żetonów!")
        
        # Sprawdź pierwsze kilka żetonów
        for i, token in enumerate(tokens[:5]):
            print(f"   {i+1}. {token.id}: q={token.q}, r={token.r}, owner={token.owner}")
        
        # Sprawdź czy współrzędne hex są sensowne
        valid_coords = 0
        for token in tokens:
            if token.q is not None and token.r is not None:
                valid_coords += 1
        
        print(f"✅ Żetony z poprawnymi współrzędnymi hex: {valid_coords}/{len(tokens)}")
        
        return True
        
    except Exception as e:
        print(f"❌ BŁĄD w test_load_tokens: {e}")
        return False

if __name__ == "__main__":
    test_load_tokens()
