# KAMPANIA 1939 - INSTRUKCJA OBSŁUGI

## SPIS TREŚCI
1. [Uruchamianie gry](#uruchamianie-gry)
2. [Interfejs gracza](#interfejs-gracza)
3. [Mechanika rozgrywki](#mechanika-rozgrywki)
4. [System ekonomiczny](#system-ekonomiczny)
5. [Walka i jednostki](#walka-i-jednostki)
6. [Zapis i wczytywanie](#zapis-i-wczytywanie)
7. [Rozwiązywanie problemów](#rozwiązywanie-problemów)

## URUCHAMIANIE GRY

### Podstawowe uruchomienie
```bash
python main.py
```
- Uruchamia grę z ekranem startowym
- Pozwala wybrać role graczy i nacje

### Szybkie uruchomienie (bez ekranu startowego)
```bash
python main_alternative.py
```
- Automatycznie ustawia 6 graczy: 3 Polska, 3 Niemcy
- Kolejność: Generał Polski → Dowódcy Polski → Generał Niemiecki → Dowódcy Niemieccy

## INTERFEJS GRACZA

### Panel Generała
- **Mapa globalna** - widok całej mapy z punktami strategicznymi
- **Informacje o ekonomii** - przychody z miast i zasobów
- **Punkty zwycięstwa** - aktualny stan VP i historia
- **Zarządzanie dowódcami** - przegląd sił podległych

### Panel Dowódcy
- **Mapa taktyczna** - szczegółowy widok obszaru operacji
- **Jednostki** - zarządzanie żetonami (ruch, walka, zaopatrzenie)
- **Sklep żetonów** - kupowanie nowych jednostek
- **Timer tury** - pozostały czas na wykonanie ruchów

## MECHANIKA ROZGRYWKI

### Struktura tury
1. **Ruch Generała Polskiego** (5 min)
2. **Ruch Dowódcy Polskiego #1** (5 min)
3. **Ruch Dowódcy Polskiego #2** (5 min)
4. **Ruch Generała Niemieckiego** (5 min)
5. **Ruch Dowódcy Niemieckiego #1** (5 min)
6. **Ruch Dowódcy Niemieckiego #2** (5 min)

### Akcje w turze
- **Ruch jednostek** - klik i przeciągnij żeton na docelowe pole
- **Walka** - automatyczna przy kontakcie z wrogiem
- **Zmiana trybu ruchu** - marsz/rekonesans/walka
- **Kupowanie jednostek** - w sklepie żetonów
- **Uzupełnianie zapasów** - regeneracja paliwa i amunicji

## SYSTEM EKONOMICZNY

### Punkty ekonomiczne
- **Generał otrzymuje**: punkty z miast i zasobów strategicznych
- **Dowódcy otrzymują**: część punktów od Generała na zakupy
- **Wydatki**: nowe jednostki, uzupełnianie zapasów

### Punkty kluczowe (Key Points)
- **Miasta strategiczne** - dają punkty ekonomiczne co turę
- **Zasoby** - ropa, stal, żywność
- **Kontrola** - żeton na polu = kontrola dla tej nacji

### Punkty zwycięstwa (VP)
- **Zajęcie miast** - większe miasta = więcej VP
- **Eliminacja wrogów** - zniszczenie jednostek przeciwnika
- **Kontrola obiektów** - lotniska, forty, porty

## WALKA I JEDNOSTKI

### Typy jednostek
- **Piechota** - tania, obronna, wolna
- **Czołgi** - droga, szybka, silna w ataku
- **Lotnictwo** - zasięg, rekonesans, wsparcie
- **Artyleria** - daleki zasięg, wsparcie

### Tryby ruchu
1. **Marsz** - szybki ruch, słaba obrona
2. **Rekonesans** - zwiększony zasięg widzenia
3. **Walka** - silna obrona, wolny ruch

### Mechanika walki
- **Automatyczna** - przy kontakcie jednostek różnych nacji
- **Wartości** - atak vs obrona + modyfikatory terenu
- **Rezultat** - straty w jednostkach, możliwe wycofanie

## ZAPIS I WCZYTYWANIE

### Zapis gry
- **Przycisk "Zapisz"** w panelu gracza
- **Automatyczny zapis** - `saves/latest.json`
- **Nazwane zapisy** - z datą i nazwą gracza

### Wczytywanie gry
- **Przycisk "Wczytaj"** w panelu gracza
- **Kontynuacja** - od momentu zapisu z tym samym graczem
- **Pełny stan** - mapa, jednostki, ekonomia, tura

### Pliki zapisu
```
saves/
├── latest.json                          # Ostatni automatyczny zapis
├── save_2025-06-15_12-30-45_Generał1_Polska.json  # Zapisy nazwane
└── save_2025-06-15_13-15-22_Dowódca2_Niemcy.json
```

## ROZWIĄZYWANIE PROBLEMÓW

### Częste problemy

**Gra się zawiesza podczas ruchu**
- Sprawdź czy żeton ma punkty ruchu
- Sprawdź czy pole docelowe nie jest zablokowane
- Restart aplikacji i wczytaj ostatni zapis

**Nie widać wrogich jednostek**
- Jednostki są widoczne tylko w zasięgu wzroku
- Użyj trybu rekonesansu do zwiększenia zasięgu
- Zbliż swoje jednostki do obszaru wroga

**Błędy przy zapisie/wczytywaniu**
- Sprawdź czy folder `saves/` istnieje
- Sprawdź uprawnienia do zapisu w folderze
- Usuń uszkodzone pliki `.json` z saves/

**Problemy z GUI**
- Zamknij i uruchom ponownie grę
- Sprawdź czy wszystkie okna są zamknięte
- Użyj `main_alternative.py` jako alternatywy

### Logi debugowania
Gra wypisuje informacje diagnostyczne w konsoli:
```
[WALKA] Atakujący: token_123 na 5,7
[EKONOMIA] Polski Generał otrzymał 15 punktów
[RUCH] Żeton przeszedł z (3,4) do (4,5)
```

### Pliki konfiguracyjne
- `data/map_data.json` - dane mapy i punktów strategicznych
- `assets/tokens/index.json` - definicje wszystkich typów jednostek
- `assets/start_tokens.json` - rozmieszczenie początkowe

## WSKAZÓWKI STRATEGICZNE

### Dla Generała
1. **Ekonomia** - priorytet na kontrolę miast
2. **Strategia** - koordynacja działań dowódców
3. **Długoterminowość** - planowanie na 30 tur

### Dla Dowódcy
1. **Taktyka** - efektywne użycie jednostek
2. **Rekonesans** - zwiększaj widoczność
3. **Współpraca** - wsparcie innych dowódców

### Wskazówki ogólne
- **Oszczędność paliwa** - planuj ruchy efektywnie
- **Obrona miast** - nie pozwól wrogowi na łatwe zdobycze
- **Timing** - koordynuj ataki między turami dowódców
- **Backup** - regularnie zapisuj grę

---

## KONTAKT I POMOC

W przypadku problemów technicznych sprawdź folder `tests/` - zawiera przykłady użycia wszystkich funkcji systemu.

**Wersja dokumentu**: 1.0 (15 czerwca 2025)
