# STRUKTURA PROJEKTU KAMPANIA 1939

## GŁÓWNE PLIKI WEJŚCIOWE

### main.py
- **Opis**: Główny punkt wejścia z ekranem startowym
- **Użycie**: `python main.py`
- **Funkcje**: Wybór graczy, ról, czasów na tury

### main_alternative.py
- **Opis**: Szybkie uruchomienie bez ekranu startowego  
- **Użycie**: `python main_alternative.py`
- **Funkcje**: Automatyczne ustawienie 6 graczy, natychmiastowy start

## ARCHITEKTURA MODUŁÓW

### engine/ - Silnik gry (CORE)
```
engine/
├── __init__.py              # Inicjalizacja modułu
├── engine.py               # GameEngine - główna klasa silnika
├── board.py                # Board - mapa hex, pathfinding
├── token.py                # Token - jednostki, ładowanie z JSON
├── player.py               # Player - gracze, ekonomia, widoczność
├── action.py               # Actions - ruchy, walka, akcje
├── action_refactored.py    # Zrefaktoryzowane akcje (nowsza wersja)
├── action_refactored_clean.py # Czysta wersja akcji
├── hex_utils.py            # Funkcje geometrii heksagonalnej
└── save_manager.py         # Zapis/wczytywanie stanu gry
```

**Kluczowe klasy**:
- `GameEngine` - centralna logika gry
- `Board` - mapa z pathfindingiem
- `Token` - jednostki wojskowe
- `Player` - gracze z ekonomią

### gui/ - Interfejs użytkownika
```
gui/
├── __init__.py              # Inicjalizacja GUI
├── ekran_startowy.py       # Ekran wyboru graczy i ról
├── panel_generala.py       # Interface Generała (mapa globalna)
├── panel_dowodcy.py        # Interface Dowódcy (mapa taktyczna)
├── panel_gracza.py         # Wspólny panel gracza (zapis/wczytaj)
├── panel_mapa.py           # Główny widget mapy hex
├── panel_ekonomiczny.py    # Panel zarządzania ekonomią
├── panel_pogodowy.py       # Panel informacji o pogodzie
├── token_info_panel.py     # Panel informacji o żetonie
├── token_shop.py           # Sklep kupowania jednostek
├── token_shop_standalone.py # Osobna wersja sklepu
├── deploy_new_tokens.py    # Rozmieszczanie nowych jednostek
├── uzupelnij_zeton.py      # Uzupełnianie zapasów żetonu
├── zarzadzanie_punktami_ekonomicznymi.py # Zarządzanie ekonomią
├── opcje_dostepnosci.py    # Opcje dostępności
├── audio/                  # Pliki dźwiękowe
└── images/                 # Obrazki interface
```

### core/ - Systemy wspomagające
```
core/
├── ekonomia.py             # EconomySystem - system ekonomiczny
├── pogoda.py               # Pogoda - system pogodowy
├── tura.py                 # TurnManager - zarządzanie turami
├── rozkazy.py              # System rozkazów
├── dyplomacja.py           # System dyplomacji
├── siec.py                 # Komunikacja sieciowa
└── zwyciestwo.py           # VictoryConditions - warunki zwycięstwa
```

### tests/ - Testy jednostkowe i integracyjne
```
tests/
├── __init__.py             # Inicjalizacja testów
├── test_game_full_integrity.py # Test integralności całej gry
├── test_save_load_integrity.py # Test zapisywania/wczytywania
├── test_zapis_wczytanie_gry.py # Test zapisów gry
├── test_action_refactored.py   # Test zrefaktoryzowanych akcji
├── test_combat_system_example.py # Test systemu walki
├── test_modyfikatory_ruchu_terenu.py # Test modyfikatorów terenu
├── test_blokada_ruchu.py      # Test blokad ruchu
├── test_panel_gracza_*.py     # Testy interfejsu gracza
├── test_przydzial_punktow_*.py # Testy systemu punktów
└── [inne testy specyficzne]   # Pozostałe testy funkcji
```

### data/ - Dane gry
```
data/
└── map_data.json           # Definicja mapy hex z punktami strategicznymi
```

### assets/ - Zasoby gry
```
assets/
├── mapa_globalna.jpg       # Tło mapy globalnej
├── start_tokens.json       # Rozmieszczenie początkowe jednostek
└── tokens/                 # Definicje i grafiki jednostek
    ├── index.json          # Indeks wszystkich typów jednostek
    ├── aktualne/           # Nowo utworzone jednostki
    └── [definicje jednostek] # Pliki JSON + PNG jednostek
```

### saves/ - Zapisy gry
```
saves/
├── latest.json             # Ostatni automatyczny zapis
└── save_*.json             # Nazwane zapisy graczy
```

### docs/ - Dokumentacja
```
docs/
├── INSTRUKCJA_OBSLUGI.md   # Instrukcja dla graczy
├── STRUKTURA_PROJEKTU.md   # Ten plik - opis architektury
├── README_GAMEPLAY.md      # Opis mechaniki gry
├── REFACTOR_AND_AI_PLAN.md # Plan refaktoryzacji i AI
└── plans/                  # Plany rozwoju projektu
```

### scripts/ - Skrypty pomocnicze
```
scripts/
├── cleanup_project.py      # Czyszczenie projektu z niepotrzebnych plików
├── master_cleanup.py       # Główny skrypt porządkowania
├── reorganize_project.py   # Reorganizacja struktury folderów
├── prepare_refactor.py     # Przygotowanie do refaktoryzacji
├── create_backup.bat       # Backup projektu (Windows)
├── export_to_github.bat    # Export do GitHub (Windows)
├── push_to_github.bat      # Push do GitHub (Windows)
├── push_to_github.ps1      # Push PowerShell
└── quick_push.ps1          # Szybki push
```

### tools/ - Narzędzia deweloperskie
```
tools/
├── diagnostyka_key_points.py # Diagnostyka punktów strategicznych
├── convert_attack_fields.py  # Konwersja pól ataku
└── check_tokens_vs_json.py   # Sprawdzanie zgodności żetonów
```

### edytory/ - Edytory zasobów
```
edytory/
├── map_editor_prototyp.py  # Prototyp edytora map
└── token_editor_prototyp.py # Prototyp edytora jednostek
```

### accessibility/ - Dostępność
```
accessibility/
├── interfejs_wizualny.py   # Ulepszenia wizualne
├── komendy_glosowe.py      # Komendy głosowe
└── narracja_glosowa.py     # Narracja dla niewidomych
```

### ai/ - Sztuczna inteligencja
```
ai/
├── commanders/             # Implementacje AI dowódców
├── data/                   # Dane treningowe AI  
└── models/                 # Modele AI
```

### archive/ - Archiwum
```
archive/
├── backup_files           # Kopie zapasowe
└── [przeniesione pliki]   # Nieużywane pliki z głównego projektu
```

## PRZEPŁYW DANYCH

### 1. Inicjalizacja (main.py)
```
EkranStartowy → wybór graczy → GameEngine → ładowanie mapy/żetonów
```

### 2. Pętla gry
```
TurnManager → Player → GUI (Panel) → Akcje → GameEngine → Update stanu
```

### 3. Zapis/Wczytywanie
```
SaveManager → JSON → pełny stan gry → restauracja przy wczytaniu
```

## KLUCZOWE WZORCE

### Separation of Concerns
- **engine/** - tylko logika biznesowa
- **gui/** - tylko prezentacja
- **core/** - systemy wspomagające

### Single Source of Truth
- `GameEngine` jest jedynym źródłem stanu gry
- GUI tylko odbiera i wysyła akcje

### Testability
- Każdy moduł ma testy w `tests/`
- Seed-owalność dla powtarzalnych testów

### Modularity
- Każdy system w osobnym pliku
- Łatwe dodawanie nowych funkcji

## DEPENDENCIES

### Wewnętrzne
- `engine` → `core` (systemy wspomagające)
- `gui` → `engine` (dane) + `core` (funkcje)
- `tests` → wszystkie moduły

### Zewnętrzne
- **tkinter** - interface graficzny
- **PIL** - manipulacja obrazów
- **json** - serializacja danych
- **random** - generator liczb losowych
- **pathlib** - operacje na plikach

## ROZWÓJ I MAINTENANCE

### Dodawanie nowych funkcji
1. Logika → `engine/` lub `core/`
2. Interface → `gui/`
3. Testy → `tests/`
4. Dokumentacja → `docs/`

### Refaktoryzacja
1. Backup → `scripts/create_backup.bat`
2. Testy → sprawdź czy przechodzą
3. Zmiany → małe, iteracyjne
4. Dokumentacja → aktualizuj

### Debugging
- Logi w konsoli
- Testy jednostkowe
- Pliki diagnostyczne w `tools/`

---

**Ostatnia aktualizacja**: 15 czerwca 2025  
**Wersja projektu**: 2.1  
**Status**: Produkcyjny - gotowy do gry
