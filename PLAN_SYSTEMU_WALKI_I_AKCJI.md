# PLAN SYSTEMU WALKI I AKCJI

## 1. Oznaczanie jednostek walczących
- [x] ~~Dodaj pole `is_fighting` lub `in_combat` (bool) do obiektu żetonu, ustawiane na czas rozstrzygania walki.~~
- [x] ~~W silniku gry trzymaj listę aktywnych walk jako tupla `(attacker, defender)` na czas rozstrzygania.~~
- [x] ~~Dodaj oznaczenie graficzne na mapie (ikona, obramowanie, kolor tła) dla żetonów biorących udział w walce.~~
- [x] ~~W panelu info żetonu wyświetl status tekstowy „WALCZY!”, jeśli bierze udział w walce.~~

## 2. Reakcja wroga na wejście w zasięg widzenia i ataku
- [x] ~~Po ruchu żetonu sprawdź, które wrogie żetony widzą go i mają go w swoim zasięgu ataku.~~
- [x] ~~Każdy taki wróg może oddać strzał (atak reakcyjny/obronny).~~
- [ ] Możliwość ograniczenia liczby reakcji (np. raz na turę, tylko jeśli wróg nie atakował w tej turze).

## 3. Atak aktywny i wsparcie sojuszników
- [x] ~~Po ruchu żeton może zaatakować dowolny żeton wroga w swoim zasięgu ataku.~~
- [x] ~~Sojusznicy (inne żetony tego samego dowódcy), które widzą wroga i mają go w swoim zasięgu ataku, mogą również przeprowadzić atak wsparcia (np. ogień krzyżowy).~~

## 4. Logika rozstrzygania ataku
- [x] ~~Oblicz siłę ataku i obrony (uwzględnij tryb ruchu, morale, wsparcie, modyfikatory terenu itp.).~~
- [x] ~~Dodaj współczynnik losowy (np. rzut kością 1-6, albo losowy procent ±20%).~~
- [x] ~~Porównaj wynik ataku i obrony:~~
    - [x] ~~Jeśli atak > obrona → atak udany.~~
    - [x] ~~Jeśli atak ≤ obrona → atak nieudany.~~
- [x] ~~Wylicz straty:~~
    - [x] ~~Prosta tabela strat (np. atak udany: obrońca traci X, atakujący Y; atak nieudany: atakujący traci X, obrońca Y).~~
    - [x] ~~Efekt „zniszczenia” jeśli różnica jest duża.~~

## 5. System akcji i zużycie punktów ruchu
- [x] ~~Każda jednostka posiada pulę punktów ruchu na turę (np. 10).~~
- [x] ~~Punkty ruchu są zużywane nie tylko na ruch, ale także na inne akcje (atak, wsparcie, wycofanie się itp.).~~
- [x] ~~Przykład: jeśli jednostka zużyje 5 punktów na ruch, zostaje jej 5 na ataki lub inne akcje.~~
- [x] ~~Każdy atak kosztuje 1 punkt ruchu (lub więcej, jeśli zdecydujemy się na różnicowanie kosztów akcji).~~
- [x] ~~Jednostka może wykonać tyle ataków, ile ma pozostałych punktów ruchu.~~
- [x] ~~Jeśli po atakach zostaną punkty ruchu, może je wykorzystać np. na wycofanie się lub dalszy ruch.~~
- [x] ~~Punkty ruchu przeciwnika resetują się na początku jego tury.~~

## 6. Wpływ terenu na walkę i ruch
- [x] ~~Każdy heks ma określony typ terenu (np. las, miasto, pole, wzgórze) – obecnie w mapie tylko `teren_płaski`, ale edytor map pozwoli wprowadzić inne wartości.~~
- [x] ~~Teren wpływa na koszt ruchu (`move_mod` z mapy, np. las = +2, pole = +1, miasto = +3) – koszt ruchu = 1 + move_mod, w pełni wdrożone w silniku i testach.~~
- [x] ~~Teren wpływa na obronę (`defense_mod` z mapy, np. las +30% do obrony, miasto +50%, pole brak bonusu).~~
- [ ] Teren może wpływać na zasięg widzenia i ataku (np. las ogranicza zasięg widzenia do 1, wzgórze zwiększa zasięg ataku o 1).
- [x] ~~Efekty terenu są uwzględniane przy rozstrzyganiu walki i planowaniu ruchu.~~

## 7. Testy i GUI
- [x] ~~Testy jednostkowe: zużycie punktów ruchu na akcje, wpływ terenu na koszt ruchu i obronę (pełny coverage, testy przechodzą na realnych danych mapy).~~
- [x] ~~Wyświetlanie efektów terenu na mapie i w panelu info.~~

## 8. Playtesty i walidacja
- [x] Przeprowadzono pełne playtesty systemu walki, ruchu, wsparcia, reakcji i efektów terenu na realnej mapie – brak regresji, mechanika zgodna z założeniami.
- [x] Testy regresji (pytest) przechodzą w całości po zmianie logiki kosztu ruchu.
