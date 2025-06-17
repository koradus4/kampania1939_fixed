# 🎖️ Kampania 1939 - Gra Strategiczna

## O Projekcie

**Kampania 1939** to zaawansowana gra strategiczna odtwarzająca działania wojenne z 1939 roku. Projekt zawiera kompletny silnik gry, edytory i narzędzia automatyzacji.

## 🚀 Szybki Start

### Kreator Armii (Główne Narzędzie)
```bash
python kreator_armii.py
```

**Najszybszy sposób na stworzenie kompletnej armii!**
- 🎮 Przyjazny interfejs GUI
- ⚡ Pełna automatyzacja (bez ręcznych dialogów)
- 🎲 Losowe generowanie lub precyzyjna kontrola
- 📊 Podgląd i balansowanie na żywo
- 💾 Automatyczny zapis żetonów (JSON + PNG)

[📖 Pełna instrukcja Kreatora Armii](KREATOR_ARMII.md)

### Główna Gra
```bash
python main.py
```

## 📁 Struktura Projektu

```
kampania1939_fixed/
├── kreator_armii.py          # 🎖️ KREATOR ARMII (GŁÓWNE NARZĘDZIE)
├── main.py                   # Główna aplikacja gry
├── 
├── engine/                   # Silnik gry
├── gui/                      # Interfejsy graficzne
├── edytory/                  # Edytory żetonów i map
├── tools/                    # Narzędzia automatyzacji
├── assets/                   # Zasoby (mapy, żetony)
├── tests/                    # Testy automatyczne
└── docs/                     # Dokumentacja
```

## 🛠️ Narzędzia

### 1. 🎖️ Kreator Armii ⭐ **POLECANE**
- **Plik**: `kreator_armii.py` (główny folder)
- **Opis**: Profesjonalna aplikacja GUI do tworzenia zbalansowanych armii
- **Funkcje**: Wybór nacji/dowódcy, kontrola budżetu, automatyczne balansowanie
- **Rezultat**: Kompletne żetony JSON+PNG w `assets/tokens/`

### 2. 🗂️ Token Editor
- **Plik**: `edytory/token_editor_prototyp.py`
- **Opis**: Edytor pojedynczych żetonów jednostek
- **Użycie**: Ręczne tworzenie lub edycja żetonów

### 3. 🗺️ Map Editor
- **Plik**: `edytory/map_editor_prototyp.py`
- **Opis**: Edytor map heksagonalnych
- **Użycie**: Tworzenie nowych map do gry

### 4. 🤖 Automatyzacja Armii
- **Folder**: `tools/army_automation/`
- **Opis**: Skrypty do masowego tworzenia armii
- **Użycie**: Zaawansowane scenariusze automatyzacji

## 📖 Dokumentacja

### Główne Instrukcje
- [🎖️ Kreator Armii](KREATOR_ARMII.md) - **ROZPOCZNIJ TUTAJ**
- [📋 Automatyzacja Armii](AUTOMATYZACJA_ARMII.md)
- [🎮 Instrukcja Rozgrywki](docs/INSTRUKCJA_OBSLUGI.md)
- [🏗️ Plan Rozwoju](docs/PLAN_ROZWOJU.md)

### Dokumentacja Techniczna
- [📐 Struktura Projektu](docs/STRUKTURA_PROJEKTU.md)
- [🧠 Możliwości AI](docs/AI_CAPABILITIES_MANIFEST.md)
- [🔧 Refaktor i AI](docs/REFACTOR_AND_AI_PLAN.md)

## 🎮 Rozgrywka

### Mechaniki Gry
- **Turowy system** strategiczny
- **Ekonomia** i zarządzanie zasobami
- **Dyplomacja** między graczami
- **Pogoda** wpływająca na rozgrywkę
- **Heksagonalna mapa** z systemem VP

### Nacje i Dowódcy
- **Polska**: Dowódcy 1, 2, 3
- **Niemcy**: Dowódcy 5, 6
- **Unikalne jednostki** dla każdej nacji
- **Historyczne nazwy** i statystyki

## 🔧 Instalacja i Uruchomienie

### Wymagania
- Python 3.8+
- Tkinter (zazwyczaj wbudowany)
- PIL/Pillow (dla grafik)

### Instalacja
```bash
git clone [repository_url]
cd kampania1939_fixed
pip install -r requirements.txt  # jeśli istnieje
```

### Uruchomienie
```bash
# Kreator Armii (polecane)
python kreator_armii.py

# Główna gra
python main.py

# Token Editor
python edytory/token_editor_prototyp.py

# Map Editor
python edytory/map_editor_prototyp.py
```

## 🎯 Pierwsze Kroki

1. **Rozpocznij od Kreatora Armii**: `python kreator_armii.py`
2. **Stwórz swoją pierwszą armię** (Polska/Niemcy, 10 żetonów, 500 VP)
3. **Sprawdź rezultaty** w `assets/tokens/`
4. **Uruchom główną grę**: `python main.py`
5. **Załaduj utworzone żetony** i rozpocznij rozgrywkę

## 🔥 Najważniejsze Funkcje

### ✅ Co Działa Perfekcyjnie
- 🎖️ **Kreator Armii** - pełna automatyzacja, GUI, balansowanie
- 💾 **Generowanie żetonów** - JSON + PNG, historyczne nazwy
- 🎲 **Losowe armie** - inteligentne, zbalansowane
- 📊 **Analizy składu** - typy jednostek, koszty VP
- 🏗️ **Token Editor** - kompletny edytor pojedynczych żetonów

### 🚧 W Rozwoju
- 🎮 **Główna gra** - silnik, GUI, mechaniki
- 🗺️ **Map Editor** - edycja map heksagonalnych
- 🤖 **AI przeciwnicy** - inteligentni dowódcy
- 🌐 **Sieć multiplayer** - rozgrywka online

## 📞 Wsparcie

W razie problemów:
1. Sprawdź dokumentację w folderze `docs/`
2. Przeczytaj pliki README w poszczególnych folderach
3. Sprawdź testy w folderze `tests/`

---

**Kampania 1939** © 2025 - Gra strategiczna nowej generacji! 🎖️
