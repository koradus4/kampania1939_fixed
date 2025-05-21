# Plan migracji do modularnego silnika gry (GameEngine)

## Cel
~~Oddzielenie logiki gry od GUI, centralizacja zarządzania mapą, żetonami i turami, uproszczenie testowania oraz przygotowanie projektu pod dalszy rozwój.~~

---

## 1. Nowa struktura katalogów

```
/engine
    board.py         # logika mapy, pathfinding, szybkie przeliczanie heksów
    token.py         # klasa Token, wczytywanie żetonów z JSON
    player.py        # klasa Player (dawny Gracz)
    action.py        # klasy akcji (MoveAction, CombatAction, itp.)
    engine.py        # klasa GameEngine: zarządzanie całością
    hex_utils.py     # narzędzia do heksów (współrzędne, dystans, itp.)
/data
    map_data.json
    tokens_index.json
    start_tokens.json
/ui
    map_panel.py
    token_panel.py
```

---

## 2. Migracja klasy Token

~~- Przenieś definicję żetonu z `zetony.py` do `engine/token.py`.~~
~~- Klasa `Token` powinna mieć:~~
  ~~- id, owner, statystyki, pozycję (q, r)~~
  ~~- metody: `can_move_to(dist)`, `set_position(q, r)`, `serialize()`~~
~~- Dodaj funkcję wczytującą żetony z JSON (index + start).~~

---

## 3. Migracja mapy

~~- Przenieś logikę mapy z `model/mapa.py` do `engine/board.py`.~~
~~- Usuń brute-force z `coords_to_hex`, zaimplementuj szybkie przeliczanie axial/cube.~~
~~- Dodaj prosty pathfinding (A*), uwzględniający `tile.move_mod`.~~
~~- Board powinien znać rozkład żetonów (lista tokenów na mapie).~~

---

## 4. GameEngine

~~- Stwórz `engine/engine.py` z klasą `GameEngine`.~~
~~- Odpowiada za:~~
  ~~- inicjalizację mapy i żetonów~~
  ~~- zarządzanie turami, kolejnością graczy, reset ruchów~~
  ~~- seed-owalną losowość (`random.Random(seed)`)~~
  ~~- rejestrację i wykonywanie akcji (`Action.execute(engine)`)~~
  ~~- zwracanie stanu do GUI~~

---

## 5. Akcje

~~- W `engine/action.py`:~~
  ~~- klasa bazowa `Action`~~
  ~~- klasy pochodne: `MoveAction`, `CombatAction`, `FortifyAction` itd.~~
  ~~- każda akcja waliduje stan, modyfikatory terenu, zasięg, koszty ruchu~~

---

## 6. Integracja mapy i żetonów

~~- Board/GameEngine powinien zwracać do GUI listę: `(token, verts, center)` do wyświetlenia.~~
~~- GUI rysuje żetony na środku heksa, wyświetla wartości (np. combat_value).~~

---

## 7. Refaktoryzacja GUI

~~- Przerób GUI (np. `panel_mapa.py`), by korzystało z silnika gry.~~
~~- Usuwaj hard-coded ścieżki – używaj relatywnych lub konfigurowalnych.~~

---

## 8. Seed-owalność

~~- Przekazuj seed do GameEngine, używaj go we wszystkich operacjach losowych.~~

---

## 9. Testy jednostkowe

~~- Dodaj testy dla:~~
  ~~- `Board.distance()`, `find_path()`~~
  ~~- `Token.can_move_to()`, `Action.execute()`~~
  ~~- Parsowanie JSON-ów~~
  ~~- Testy integracyjne GUI ↔ silnik (ruch, walka, kolizje, usuwanie żetonu)~~
  ~~- Testy edge-case, testy AI, testy wydajnościowe~~

---

## 10. Dokumentacja

- ~~Opisz API silnika, format JSON, przykłady użycia.~~  <!-- DO UZUPEŁNIENIA -->

---

## Kolejność prac (etapy)

~~1. Przenieś klasę Token i logikę żetonów do `engine/token.py`.~~
~~2. Przenieś mapę do `engine/board.py`, dodaj szybkie przeliczanie i pathfinding.~~
~~3. Stwórz GameEngine (`engine/engine.py`), zintegruj mapę i żetony.~~
~~4. Dodaj akcje (`engine/action.py`), podłącz do GameEngine.~~
~~5. Przerób GUI, by korzystało z silnika.~~
~~6. Dodaj testy jednostkowe i integracyjne.~~
~~7. Migracja całego kodu gry i GUI na korzystanie z nowej klasy Player zamiast Gracz.~~
~~8. Stopniowe usuwanie starego modelu gracza (model/gracz.py) po pełnej migracji.~~
~~9. Testy integracyjne GUI ↔ silnik, odporność na zmiany danych, poprawki edge-case.~~
~~10. Uzupełnij dokumentację API silnika, formatów JSON, przykłady użycia.~~  <!-- DO ZROBIENIA -->

---

**Po wdrożeniu:**
~~- Silnik gry jest niezależny od GUI.~~
~~- Łatwo testować i rozwijać nowe mechaniki.~~
~~- Możesz podmienić GUI lub dodać AI bez zmian w logice gry.~~

---

~~Migracja całego kodu gry i GUI na korzystanie z nowej klasy Player zamiast Gracz~~
~~Stopniowe usuwanie starego modelu gracza (model/gracz.py) po pełnej migracji~~

---

## Zrealizowane etapy migracji mapy/żetonów

- ~~Przeniesienie logiki mapy i żetonów do silnika (engine/board.py, engine/token.py, engine/hex_utils.py)~~
- ~~Refaktoryzacja GUI do korzystania z silnika~~
- ~~Usunięcie plików archiwalnych modelu~~
- ~~Testy jednostkowe i integracyjne przechodzą poprawnie~~
- ~~Checklistę migracji można uznać za zamkniętą~~

## Nowa architektura

- Mapa: engine/board.py
- Żetony: engine/token.py
- Funkcje geometryczne: engine/hex_utils.py
- GUI: korzysta z silnika przez GameEngine

## Dalsze kroki
- (Opcjonalnie) Rozbudowa testów edge-case, AI, wydajnościowych
- (Opcjonalnie) Usunięcie tego pliku po akceptacji
