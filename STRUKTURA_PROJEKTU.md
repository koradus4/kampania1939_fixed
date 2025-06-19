# STRUKTURA PROJEKTU KAMPANIA 1939

```
kampania1939_fixed/
├── main.py                  # Główny plik uruchomieniowy (z ekranem startowym)
├── main_alternative.py      # Szybki start bez ekranu wyboru
├── README.md               # Podstawowe informacje o projekcie
├── INSTRUKCJA_OBSLUGI.md   # Kompletna instrukcja użytkownika
├── OPIS_PROJEKTU.md        # Dokumentacja architektury
│
├── engine/                 # 🔧 SILNIK GRY
│   ├── __init__.py
│   ├── engine.py          # Główny silnik gry, integracja komponentów
│   ├── board.py           # Mapa heksagonalna, pathfinding
│   ├── token.py           # Jednostki wojskowe, mechaniki
│   ├── player.py          # Gracze, widoczność, VP
│   ├── action.py          # System rozkazów (ruch, walka)
│   ├── save_manager.py    # Zapis/wczytanie gry
│   └── hex_utils.py       # Funkcje geometryczne heksów
│
├── gui/                    # 🖼️ INTERFEJS UŻYTKOWNIKA
│   ├── __init__.py
│   ├── ekran_startowy.py  # Wybór graczy na start
│   ├── panel_generala.py  # Interfejs generała (pełna mapa)
│   ├── panel_dowodcy.py   # Interfejs dowódcy (lokalna mapa)  
│   ├── panel_gracza.py    # Wspólne elementy UI
│   ├── panel_mapa.py      # Główny komponent mapy
│   │                      # - Przezroczystość żetonów (alpha 40% dla nieaktywnych)
│   │                      # - Auto-centrowanie na jednostkach gracza
│   │                      # - Zarządzanie widocznością dowódców
│   ├── token_info_panel.py # Informacje o jednostce
│   ├── token_shop.py      # Kupowanie jednostek
│   │                      # - Kolory napisów zgodne z Token Editor
│   │                      # - Poprawione zarządzanie zakupami
│   ├── deploy_new_tokens.py # Deployment nowych jednostek
│   ├── panel_ekonomiczny.py # Zarządzanie ekonomią
│   ├── panel_pogodowy.py  # Panel pogody
│   ├── opcje_dostepnosci.py # Ustawienia dostępności
│   ├── uzupelnij_zeton.py # Uzupełnianie zapasów
│   ├── zarzadzanie_punktami_ekonomicznymi.py
│   ├── images/            # Grafiki interfejsu i portret graczy
│   └── audio/             # Dźwięki gry (przygotowane)
│
├── core/                   # ⚙️ SYSTEMY PODSTAWOWE
│   ├── tura.py            # Zarządzanie turami
│   ├── ekonomia.py        # System punktów ekonomicznych
│   ├── pogoda.py          # Warunki atmosferyczne  
│   ├── dyplomacja.py      # Relacje między frakcjami
│   ├── rozkazy.py         # System rozkazów
│   ├── siec.py            # Komunikacja sieciowa (przygotowane)
│   └── zwyciestwo.py      # Warunki końca gry
│
├── ai/                     # 🤖 SZTUCZNA INTELIGENCJA
│   ├── commanders/        # Implementacje AI dowódców
│   ├── models/           # Modele decyzyjne AI
│   └── data/             # Dane treningowe
│
├── tests/                  # ✅ TESTY
│   ├── __init__.py
│   ├── test_integralnosc_calej_gry.py    # Test pełnej rozgrywki
│   ├── test_zapis_wczytanie_gry.py       # Test zapisu/wczytania
│   ├── test_action_refactored.py         # Test systemu rozkazów
│   ├── test_combat_system_example.py     # Test walki
│   ├── test_modyfikatory_ruchu_terenu.py # Test ruchu
│   ├── test_panel_gracza_*.py            # Testy GUI
│   └── ... (inne testy mechanik)
│
├── data/                   # 📊 DANE GRY
│   └── map_data.json      # Definicja mapy heksagonalnej
│
├── assets/                 # 🎨 ZASOBY
│   ├── mapa_globalna.jpg  # Tło mapy strategicznej
│   ├── start_tokens.json  # Pozycje startowe jednostek
│   └── tokens/            # Definicje i grafiki jednostek
│       ├── index.json     # Indeks wszystkich jednostek
│       ├── aktualne/      # Nowo utworzone jednostki
│       └── ... (pliki jednostek)
│
├── saves/                  # 💾 ZAPISY GRY
│   ├── latest.json        # Ostatni automatyczny zapis
│   └── ... (zapisy gracza)
│
├── docs/                   # 📚 DOKUMENTACJA
│   ├── PLAN_ROZWOJU.md    # Roadmapa rozwoju
│   ├── REFACTOR_AND_AI_PLAN.md # Plan refaktoryzacji
│   ├── README_GAMEPLAY.md  # Mechaniki rozgrywki
│   └── plans/             # Szczegółowe plany
│
├── scripts/                # 🔨 SKRYPTY POMOCNICZE  
│   ├── cleanup_project.py # Czyszczenie projektu
│   ├── master_cleanup.py  # Zaawansowane porządkowanie
│   ├── reorganize_project.py # Reorganizacja struktury
│   ├── prepare_refactor.py   # Przygotowanie refaktoryzacji
│   ├── create_backup.bat     # Backup projektu
│   ├── push_to_github.ps1    # Wysyłanie na GitHub
│   └── quick_push.ps1        # Szybki push
│
├── tools/                  # 🛠️ NARZĘDZIA DEWELOPERSKIE
│   ├── diagnostyka_key_points.py # Diagnostyka punktów kluczowych
│   ├── convert_attack_fields.py  # Konwersja pól ataku
│   └── check_tokens_vs_json.py   # Weryfikacja jednostek
│
├── edytory/                # ✏️ EDYTORY
│   ├── map_editor_prototyp.py    # Edytor mapy
│   └── token_editor_prototyp.py  # Edytor jednostek
│
├── accessibility/          # ♿ DOSTĘPNOŚĆ
│   ├── interfejs_wizualny.py # Ułatwienia wizualne
│   ├── komendy_glosowe.py    # Sterowanie głosowe
│   └── narracja_glosowa.py   # Narrator dla niewidomych
│
├── archive/                # 📦 ARCHIWUM
│   ├── old_tests/         # Stare/duplikaty testów
│   ├── backup_files/      # Kopie zapasowe
│   └── duplicates/        # Niepotrzebne duplikaty
│
└── utils/                  # 🧰 NARZĘDZIA POMOCNICZE
    └── loader.py          # Ładowanie zasobów
```

## KLUCZOWE PLIKI:

### Uruchamianie:
- `main.py` - pełna gra z ekranem wyboru
- `main_alternative.py` - szybki start

### Konfiguracja:
- `data/map_data.json` - mapa gry  
- `assets/start_tokens.json` - pozycje startowe
- `assets/tokens/index.json` - definicje jednostek

### Dokumentacja:
- `INSTRUKCJA_OBSLUGI.md` - jak grać
- `OPIS_PROJEKTU.md` - architektura
- `README.md` - podstawowe info

## STATYSTYKI PROJEKTU:
- **~85 plików Python**
- **~15,000 linii kodu**
- **Kompletny system gry turowej**
- **Pełne GUI dla 2 typów graczy**
- **System AI-ready**
- **Kompletne testy**

## OSTATNIE AKTUALIZACJE (Czerwiec 2025):
- ✅ **Naprawione błędy wystawiania żetonów** - poprawne zarządzanie puli
- ✅ **System przezroczystości dowódców** - wizualne odróżnienie aktywnych żetonów  
- ✅ **Auto-centrowanie mapy** - mapa wycentrowana na jednostkach gracza
- ✅ **Zunifikowane kolory napisów** - spójność między Token Shop a Token Editor
- ✅ **Stabilność systemu** - naprawione błędy AttributeError i migania
