# PLAN ROZWOJU PROJEKTU: Silnik gry planszowej 1939

## Moduły do implementacji

### 1. Atak, obrona, amunicja
- [ ] System walki (atak/obrona) z uwzględnieniem parametrów żetonów
- [ ] Mechanika zużycia amunicji podczas ataku
- [ ] Blokada ataku bez amunicji
- [ ] Testy: walka, zużycie amunicji, brak amunicji
- [ ] Logika walki: efekty specjalne, wsparcia, morale, raporty bitewne
- [ ] Animacje i logi bitewne w GUI
- [ ] Rozbudowa paneli info o prezentację efektów walki

### 2. Zapis i odczyt gry
<!-- Wszystkie zadania zrealizowane. PAMIĘTAJ: po wdrożeniu nowych funkcji lub zmianach w systemie save/load, zaktualizuj checklistę i dokumentację! -->

### 3. Dźwięki akcji żetonów
- [ ] Odtwarzanie dźwięków akcji (ruch, atak, zniszczenie, wsparcie, tankowanie)
- [ ] Integracja z panelem mapy i walki
- [ ] Testy: wywołania dźwięków, odporność na brak plików

### 4. Wystawianie jednostek
- [ ] Mechanizm wystawiania nowych żetonów na mapę (np. za punkty ekonomiczne)
- [ ] Ograniczenia: strefy wystawiania, limity jednostek
- [ ] Testy: wystawianie, limity, koszty

### 5. Punkty kluczowe
- [ ] Definicja i obsługa punktów kluczowych na mapie
- [ ] Warunki zwycięstwa związane z kontrolą punktów
- [ ] Testy: przejmowanie, utrata, warunki zwycięstwa

### 6. Rozkazy
- [ ] System rozkazów dla graczy (np. atak, obrona, ruch, wsparcie)
- [ ] Interfejs do wydawania i realizacji rozkazów
- [ ] Testy: wydawanie, realizacja, anulowanie rozkazów

### 7. Wsparcie lotnicze
- [ ] Mechanika wsparcia lotniczego (np. naloty, rozpoznanie)
- [ ] Ograniczenia: limity, koszty, cooldown
- [ ] Testy: aktywacja, efekty, limity

### 8. Punkty specjalne
- [ ] Specjalne punkty do wydawania na unikalne akcje (np. sabotaż, zwiad)
- [ ] Mechanika zdobywania i wydawania punktów specjalnych
- [ ] Testy: zdobywanie, wydawanie, efekty

## Harmonogram (propozycja)
1. Atak/obrona/amunicja
2. Zapis/odczyt gry
3. Dźwięki akcji
4. Wystawianie jednostek
5. Punkty kluczowe
6. Rozkazy
7. Wsparcie lotnicze
8. Punkty specjalne

## Testowanie
- Każdy moduł musi posiadać testy integracyjne i jednostkowe
- Testy na realnych danych (mapa, żetony)
- Testy regresyjne po każdej większej zmianie

## Uwagi
- Każdy etap powinien być dokumentowany w README.md
- Kod powinien być zgodny z istniejącą architekturą silnika
- Priorytet: stabilność, przejrzystość, łatwość rozbudowy
