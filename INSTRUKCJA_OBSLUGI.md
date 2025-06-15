# KAMPANIA 1939 - INSTRUKCJA OBSŁUGI

## OPIS GRY
Kampania 1939 to strategiczna gra turowa symulująca kampanię wrześniową 1939 roku. Gracze wcielają się w rolę generałów i dowódców armii polskich i niemieckich.

## URUCHAMIANIE GRY

### Standardowy tryb (z ekranem startowym):
```bash
python main.py
```

### Tryb szybki (bez ekranu startowego):
```bash
python main_alternative.py
```

## ROZGRYWKA

### ROLE GRACZY:
- **Generał** - zarządza całą armią, widzi wszystkie jednostki, przydziela punkty ekonomiczne
- **Dowódca** - kontroluje konkretne jednostki, ma ograniczoną widoczność

### MECHANIKI GRY:

#### 1. RUCH JEDNOSTEK
- Każda jednostka ma punkty ruchu i paliwo
- Teren wpływa na koszt ruchu (las +2, bagno +3, drogi -1)
- Tryby ruchu: combat, march, recon (różne koszty)

#### 2. WALKA
- System walki oparty na wartościach ataku/obrony
- Modyfikatory terenu i dystansu
- Losowość wyników (80-120% wartości bazowej)

#### 3. EKONOMIA
- Punkty ekonomiczne do kupowania nowych jednostek
- Punkty specjalne z kluczowych lokacji
- Automatyczne przydzielanie co turę

#### 4. WIDOCZNOŚĆ
- Każda jednostka ma zasięg widzenia
- Generał widzi wszystkie jednostki swojej armii
- Dowódca widzi tylko swoje jednostki i wykrytych wrogów

### STEROWANIE:

#### Panel Generała:
- Mapa strategiczna całego teatru działań
- Przegląd wszystkich jednostek
- Zarządzanie ekonomią i zakupami
- Przydzielanie punktów dowódcom

#### Panel Dowódcy:
- Lokalna mapa z własnymi jednostkami
- Wydawanie rozkazów ruchu i ataku
- Zarządzanie zapasami jednostek
- Ograniczona widoczność wroga

### KLUCZOWE SKRÓTY:
- **Prawy klik** - zaznaczenie jednostki
- **Lewy klik** - wydanie rozkazu ruchu
- **Shift+klik** - rozkaz ataku
- **Ctrl+S** - zapis gry
- **Ctrl+L** - wczytanie gry

## WARUNKI ZWYCIĘSTWA
- Kontrola punktów kluczowych (miasta, przeprawy)
- Eliminacja jednostek wroga
- Limit 30 tur (remis przy równych punktach)

## ZAPISYWANIE I WCZYTYWANIE
- Automatyczny zapis co turę w `saves/latest.json`
- Ręczny zapis przez menu gracza
- Możliwość wczytania dowolnego zapisu
- Pełna integralność stanu gry

## ROZWIĄZYWANIE PROBLEMÓW

### Błędy graficzne:
- Sprawdź czy wszystkie obrazy są w `gui/images/`
- Zrestartuj grę w razie problemów z mapą

### Błędy zapisu/wczytania:
- Sprawdź uprawnienia do folderu `saves/`
- Upewnij się, że plik zapisu nie jest uszkodzony

### Błędy jednostek:
- Sprawdź pliki JSON w `assets/tokens/`
- Zweryfikuj poprawność startowych pozycji

## PLIKI KONFIGURACYJNE
- `data/map_data.json` - mapa gry
- `assets/start_tokens.json` - pozycje startowe
- `assets/tokens/index.json` - definicje jednostek

## WYMAGANIA SYSTEMOWE
- Python 3.8+
- Tkinter (zazwyczaj wbudowany)
- Pillow (PIL) do obrazów
- 2GB RAM
- 500MB miejsca na dysku
