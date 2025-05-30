# PLAN ROZWOJU PROJEKTU: Silnik gry planszowej 1939

## Moduły do implementacji

### 1. Atak, obrona, amunicja
- System walki (atak/obrona) z uwzględnieniem parametrów żetonów
- Mechanika zużycia amunicji podczas ataku
- Blokada ataku bez amunicji
- Testy: walka, zużycie amunicji, brak amunicji

### 2. Paliwo
- Dodanie parametru paliwa do żetonów
- Zużycie paliwa podczas ruchu
- Blokada ruchu bez paliwa
- Możliwość tankowania (np. przez rozkaz lub na określonych polach)
- Testy: ruch z paliwem, brak paliwa, tankowanie

### 3. Wystawianie jednostek
- Mechanizm wystawiania nowych żetonów na mapę (np. za punkty ekonomiczne)
- Ograniczenia: strefy wystawiania, limity jednostek
- Testy: wystawianie, limity, koszty

### 4. Punkty kluczowe
- Definicja i obsługa punktów kluczowych na mapie
- Warunki zwycięstwa związane z kontrolą punktów
- Testy: przejmowanie, utrata, warunki zwycięstwa

### 5. Rozkazy
- System rozkazów dla graczy (np. atak, obrona, ruch, wsparcie)
- Interfejs do wydawania i realizacji rozkazów
- Testy: wydawanie, realizacja, anulowanie rozkazów

### 6. Wsparcie lotnicze
- Mechanika wsparcia lotniczego (np. naloty, rozpoznanie)
- Ograniczenia: limity, koszty, cooldown
- Testy: aktywacja, efekty, limity

### 7. Punkty specjalne
- Specjalne punkty do wydawania na unikalne akcje (np. sabotaż, zwiad)
- Mechanika zdobywania i wydawania punktów specjalnych
- Testy: zdobywanie, wydawanie, efekty

## Harmonogram (propozycja)
1. Atak/obrona/amunicja
2. Paliwo
3. Wystawianie jednostek
4. Punkty kluczowe
5. Rozkazy
6. Wsparcie lotnicze
7. Punkty specjalne

## Testowanie
- Każdy moduł musi posiadać testy integracyjne i jednostkowe
- Testy na realnych danych (mapa, żetony)
- Testy regresyjne po każdej większej zmianie

## Uwagi
- Każdy etap powinien być dokumentowany w README.md
- Kod powinien być zgodny z istniejącą architekturą silnika
- Priorytet: stabilność, przejrzystość, łatwość rozbudowy
