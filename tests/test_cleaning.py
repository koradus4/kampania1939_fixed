#!/usr/bin/env python3
"""
Test funkcji czyszczenia żetonów
"""

import sys
from pathlib import Path
import shutil

def test_cleaning():
    """Test czyszczenia polskich żetonów."""
    
    print("🔍 TEST CZYSZCZENIA ŻETONÓW")
    print("=" * 40)
    
    # Sprawdź co mamy przed usunięciem
    polska_dir = Path("assets/tokens/Polska")
    niemcy_dir = Path("assets/tokens/Niemcy")
    
    print(f"📂 Folder Polska istnieje: {polska_dir.exists()}")
    if polska_dir.exists():
        polish_tokens = list(polska_dir.iterdir())
        print(f"🇵🇱 Polskie żetony: {len(polish_tokens)}")
        for i, token in enumerate(polish_tokens[:5]):  # Pokaż pierwsze 5
            print(f"   {i+1}. {token.name}")
        if len(polish_tokens) > 5:
            print(f"   ... i {len(polish_tokens)-5} więcej")
    
    print(f"📂 Folder Niemcy istnieje: {niemcy_dir.exists()}")
    if niemcy_dir.exists():
        german_tokens = list(niemcy_dir.iterdir())
        print(f"🇩🇪 Niemieckie żetony: {len(german_tokens)}")
    
    print("\n🗑️ ROZPOCZYNAM USUWANIE POLSKICH ŻETONÓW...")
    
    try:
        if polska_dir.exists():
            print(f"🗂️ Usuwam folder: {polska_dir}")
            shutil.rmtree(polska_dir)
            print("✅ Folder Polska usunięty pomyślnie!")
        else:
            print("⚠️ Folder Polska nie istnieje")
        
        # Sprawdź rezultat
        print(f"\n🔍 Sprawdzam rezultat...")
        print(f"📂 Folder Polska istnieje po usunięciu: {polska_dir.exists()}")
        print(f"📂 Folder Niemcy istnieje po usunięciu: {niemcy_dir.exists()}")
        
        if not polska_dir.exists():
            print("🎉 SUKCES! Polskie żetony zostały usunięte!")
        else:
            print("❌ BŁĄD! Folder nadal istnieje!")
            
    except Exception as e:
        print(f"❌ BŁĄD podczas usuwania: {e}")
        print(f"📝 Typ błędu: {type(e).__name__}")

if __name__ == "__main__":
    test_cleaning()
