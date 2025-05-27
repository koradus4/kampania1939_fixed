# Plan pracy na dziś – VSCode Agent

> **Data:** {{TODAY}}
> **Cel:**
>
> * Dokończyć podstawowy silnik ruchu żetonów (A\* + GUI + testy + debug)
> * Wdrożyć mechanizm zapisu/odczytu stanu gry (snapshoty + integracja w końcu tury)

---

## 1. Ruch żetonów

1. **Oczyścić `panel_mapa.py`**

   * ⚠️ Zrób kopię zapasową przed zmianami.
   * Usuń całą starą logikę ruchu, zostaw tylko rysowanie siatki i wyświetlanie żetonów.
   * Upewnij się, że `refresh()` rysuje wyłącznie:

     * heksy na podstawie `map_data.json`
     * wszystkie tokeny z aktualnymi `q, r`

2. **Zrozumieć klasę `Token`**

   * Pola: `id`, `owner`, `stats` (`move`, `combat_value`, `image`, …), `q, r`
   * Metody:

     * `can_move_to(dist: int) -> bool`
     * `set_position(q, r)`

3. **A* i `MoveAction`*\*

   * W `engine.py`:

     ```python
     path = board.find_path(start, goal, max_cost=token.stats['move'])
     if path and token.can_move_to(len(path)-1):
         token.set_position(dest_q, dest_r)
     else:
         raise GameError("Nie można ruchu")
     ```
   * Sprawdź, czy `find_path` poprawnie uwzględnia blokady i koszty terenu.

4. **Integracja z GUI**

   * W `panel_mapa.py` dodaj:

     ```python
     self.selected_token_id = None
     ```
   * W handlerze kliknięcia:

     * Jeśli klik na token → `self.selected_token_id = token.id`
     * Inny heks + `selected_token_id` → wywołanie `MoveAction` → `engine.execute_action(...)`
     * Odśwież `refresh()` lub wyświetl błąd.

5. **Live-modyfikacja zasięgu**

   * Pozwól na zmianę `token.stats['move']` (np. w konsoli lub dedykowanym sliderze).
   * Po każdej zmianie → `refresh()`, żeby od razu zobaczyć nowe możliwości.

6. **(Opcjonalnie) Wizualizacja ścieżki**

   * Wyświetl punktowaną linię między startem a celem przed potwierdzeniem ruchu.

---

## 2. Testy i debug

* **Testy jednostkowe (`pytest`)**

  * `test_movement.py`:

    ```python
    def test_can_move_within_range():
        token.stats['move'] = 3
        assert token.can_move_to(3)
        assert not token.can_move_to(4)

    def test_move_action_blocked():
        # ustaw board.tokens tak, aby blokować ścieżkę
        assert MoveAction(...).execute(engine) == (False, _)
    ```
* **Debug**

  * Wstaw `print(f"[MOVE] path: {path}")` w `MoveAction.execute`.
  * Użyj `pdb.set_trace()` w krytycznych miejscach.

---

## 3. Zarządzanie stanem gry

1. **Struktura zapisu**

   ```jsonc
   {
     "turn": 5,
     "active_player": "3 (Polska)",
     "tokens": [
       { "id": "...", "q": 8, "r": 0, "stats": { "move": 10, … } },
       …
     ],
     "map": { "overrides": { "4,2": { "terrain_key": "ruiny" } } },
     "logs": [
       { "actor":"3 (Polska)","action":"move","from":[8,0],"to":[9,0] }
     ]
   }
   ```

2. **Moduł `save_manager.py`**

   * `save_state(engine, path)`
   * `load_state(path) -> GameEngine`

3. **Serializacja**

   * W `Token`: `to_dict()` i `@classmethod from_dict()`
   * W `GameEngine`: expose `turn_number`, `current_player`, `set_state(...)`

4. **Snapshot vs Delta**

   * **Snapshot**: prostszy, większy plik
   * **Delta**: tylko zmiany + `apply_delta(engine, delta)`

5. **Bezpieczeństwo zapisu**

   * Zapis do `*.tmp` → `os.replace()`
   * Proste asserty po wczycie (ilość tokenów, wartości w rozsądnym zakresie)

6. **Integracja**

   * Po `engine.end_turn()` → `save_state(engine, "saves/")`
   * Przy starcie gry: opcja „Kontynuuj” → `load_state("saves/latest.json")`

7. **Testy**

   ```python
   def test_save_and_load(tmp_path):
       engine = setup_test_engine()
       save_state(engine, tmp_path)
       loaded = load_state(tmp_path / "latest.json")
       assert loaded.turn_number == engine.turn_number
       assert loaded.tokens == engine.tokens
   ```

---

## 4. Zadania na dziś

* [x] Oczyścić `panel_mapa.py` i zostawić tylko rysowanie siatki + tokenów
* [x] Przetestować A\* w `board.find_path` i poprawić `MoveAction.execute`
* [x] Dodać wybór i ruch tokenów w GUI (`panel_mapa.py`)
* [ ] Napisać test zapisu/odczytu (`test_save_and_load`)

---

## Notatki i pytania

* Potrzebuję przykładowego `map_data.json` do testów A\*.
* Czy zostawiamy snapshoty czy przechodzimy na delta?
* Jakie formaty nazw plików preferujesz?
