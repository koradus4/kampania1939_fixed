# KAMPANIA 1939 - CAŁOŚCIOWE DZIAŁANIE PROJEKTU

## ARCHITEKTURA SYSTEMU

### 1. SILNIK GRY (`engine/`)
Serce aplikacji - obsługuje logikę gry:
- **`engine.py`** - główny silnik, integruje wszystkie komponenty
- **`board.py`** - mapa heksagonalna, pathfinding, overlay
- **`token.py`** - jednostki wojskowe, ładowanie z JSON
- **`player.py`** - gracze, widoczność, punkty zwycięstwa
- **`action.py`** - system rozkazów (ruch, walka)
- **`save_manager.py`** - zapis/wczytanie stanu gry
- **`hex_utils.py`** - funkcje geometryczne dla heksów

### 2. INTERFEJS UŻYTKOWNIKA (`gui/`)
Kompletny system GUI dla różnych ról:
- **`ekran_startowy.py`** - wybór graczy i rozpoczęcie gry
- **`panel_generala.py`** - interfejs dla generała (pełna mapa)
- **`panel_dowodcy.py`** - interfejs dla dowódcy (lokalna mapa)
- **`panel_gracza.py`** - wspólne elementy UI (VP, czas, akcje)
- **`panel_mapa.py`** - główny komponent mapy z interakcją
  - Przezroczystość żetonów nieaktywnych dowódców
  - Automatyczne centrowanie na jednostkach gracza
  - System scrollowania i nawigacji
- **`token_info_panel.py`** - szczegóły wybranej jednostki
- **`token_shop.py`** - kupowanie nowych jednostek
  - Kolory napisów zgodne z Token Editor
  - Poprawione zarządzanie zakupami

### 3. SYSTEMY PODSTAWOWE (`core/`)
Mechaniki rozgrywki:
- **`tura.py`** - zarządzanie turami i kolejnością graczy
- **`ekonomia.py`** - system punktów ekonomicznych
- **`pogoda.py`** - warunki atmosferyczne wpływające na grę
- **`dyplomacja.py`** - relacje między frakcjami
- **`zwyciestwo.py`** - warunki zakończenia gry

### 4. SZTUCZNA INTELIGENCJA (`ai/`)
Przygotowana struktura dla AI:
- **`commanders/`** - implementacje AI dla różnych dowódców
- **`models/`** - modele decyzyjne
- **`data/`** - dane treningowe

## PRZEPŁYW DZIAŁANIA

### Uruchomienie:
1. **main.py** → Ekran startowy → Wybór graczy
2. **main_alternative.py** → Bezpośredni start z domyślnymi ustawieniami

### Inicjalizacja gry:
1. Ładowanie mapy (`data/map_data.json`)
2. Ładowanie jednostek (`assets/tokens/`)
3. Tworzenie objektów graczy z ekonomią
4. Inicjalizacja widoczności
5. Uruchomienie pętli tur

### Pętla rozgrywki:
```
PĘTLA GŁÓWNA:
├── Sprawdzenie załadowanego save
├── Aktualizacja aktywnego gracza
├── Uruchomienie odpowiedniego panelu (Generał/Dowódca)
├── Oczekiwanie na akcje gracza
├── Przetwarzanie rozkazów
├── Aktualizacja widoczności
├── Sprawdzenie warunków końca tury
├── Przejście do kolejnego gracza
└── Sprawdzenie warunków końca gry
```

### Mechanika tur:
1. **Generał** - widzi całość, zarządza ekonomią, wydaje rozkazy strategiczne
2. **Dowódca 1** - kontroluje swoje jednostki, wykonuje ruchy taktyczne  
3. **Dowódca 2** - kontroluje swoje jednostki, wykonuje ruchy taktyczne
4. **Generał przeciwny** - jak wyżej dla drugiej strony
5. **Dowódcy przeciwni** - jak wyżej
6. **Koniec tury** - rozliczenie ekonomii, reset punktów ruchu

## KLUCZOWE FEATURES

### System widoczności:
- Każda jednostka ma zasięg widzenia
- Generał widzi wszystkie jednostki swojej armii
- Dowódca widzi tylko swoje + wykryte wrogie
- Tymczasowa widoczność podczas ruchu
- **NOWE**: Przezroczystość żetonów nieaktywnych dowódców (40% alpha)
- **NOWE**: Automatyczne centrowanie mapy na jednostkach gracza

### System ekonomiczny:
- Punkty ekonomiczne co turę
- Punkty specjalne z kluczowych lokacji
- Kupowanie nowych jednostek
- Uzupełnianie zapasów
- **NAPRAWIONE**: Poprawne usuwanie żetonów z puli po wystawieniu

### System walki:
- Wartości ataku/obrony jednostek
- Modyfikatory terenu i dystansu  
- Losowość wyników
- Różne typy amunicji

### Tryby ruchu:
- **Combat** - wolny, ekonomiczny
- **March** - standardowy
- **Recon** - szybki, kosztowny

## BEZPIECZEŃSTWO I INTEGRALNOŚĆ

### Weryfikacja właściciela:
- Każdy rozkaz sprawdza czy jednostka należy do gracza
- Blokada dostępu do cudzych jednostek

### Integralność zapisu:
- Pełna serializacja stanu gry
- Weryfikacja spójności po wczytaniu
- Backup automatyczny

### Walidacja rozkazów:
- Sprawdzanie punktów ruchu/paliwa
- Walidacja ścieżek ruchu
- Kontrola zasięgu ataku

## ROZSZERZALNOŚĆ

Projekt przygotowany na:
- Implementację AI dowódców
- Dodanie nowych typów jednostek
- Rozbudowę systemu dyplomacji
- Multiplayer online
- Moddowanie map i scenariuszy

## TESTOWANIE

Kompletny zestaw testów:
- Testy integracyjne całej rozgrywki
- Testy systemu zapisu/wczytania
- Testy mechanik ruchu i walki
- Testy interfejsu użytkownika

## OSTATNIE AKTUALIZACJE (Czerwiec 2025)

### ✅ Naprawione błędy:
- **Problem wystawiania żetonów** - poprawne usuwanie z puli po deployment
- **Błąd AttributeError** - dodana inicjalizacja `current_path` w PanelMapa
- **Kolory napisów** - Token Shop używa tych samych kolorów co Token Editor
- **Migające przyciski** - poprawne odświeżanie stanu po wystawieniu żetonu

### 🆕 Nowe funkcje:
- **Przezroczystość żetonów** - nieaktywni dowódcy mają żetony z 40% alpha
- **Auto-centrowanie mapy** - automatyczne wycentrowanie na jednostkach gracza
- **Lepszy UX** - natychmiastowe rozpoznanie żetonów aktywnego dowódcy

### 🎯 Usprawnienia wizualne:
- Żetony aktywnego dowódcy: jasne, wyraźne kolory
- Żetony nieaktywnych: przyciemnione, w tle
- Generał widzi wszystkie żetony normalnie
- Płynne przejścia między turami
