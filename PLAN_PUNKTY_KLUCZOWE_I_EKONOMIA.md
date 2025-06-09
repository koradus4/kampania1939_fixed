# Plan realizacji – Punkty kluczowe i ekonomia generałów

## 1. Struktura danych

- Każdy punkt kluczowy (`key_points`) w `data/map_data.json` ma:
  - współrzędne (np. `"10,-4"`)
  - typ (np. `"miasto"`, `"fortyfikacja"`)
  - pole `value` (wartość początkowa punktu)
- W kodzie gry należy przechowywać także wartość początkową (`initial_value`) każdego punktu (do pamięci gry, nie do pliku).

**Plik:** `data/map_data.json`

## 2. Obliczanie punktów co turę

- Po każdej turze sprawdzamy wszystkie punkty kluczowe.
- Jeśli na danym heksie stoi żeton gracza (dowolnej nacji):
  - Obliczamy **10% wartości początkowej** punktu (np. `int(0.1 * initial_value)`).
  - Tę wartość przekazujemy generałowi danej nacji jako dodatkowe punkty ekonomiczne.
  - Tę samą wartość odejmujemy od aktualnej wartości punktu (`value`).
- Jeśli na heksie nie stoi żeton, punkt nie jest konsumowany w tej turze.

**Pliki:**
- `engine/engine.py` – logika silnika gry, obsługa tury, dostęp do mapy, żetonów i graczy
- `engine/board.py` – obsługa planszy, dostęp do heksów i żetonów
- `engine/token.py` – obsługa żetonów, pozycje na mapie

## 3. Wyzerowanie punktu

- Jeśli po odjęciu wartość punktu (`value`) spadnie do zera lub poniżej:
  - Punkt kluczowy jest usuwany z mapy (`key_points`).
  - Przestaje generować punkty w kolejnych turach.

**Plik:** `engine/engine.py`, `data/map_data.json`

## 4. Integracja z interfejsem

- Panel ekonomiczny generała jest aktualizowany o nowe punkty po każdej turze.
- Punkty te powiększają pulę do rozdysponowania w kolejnej turze.

**Pliki:**
- `core/ekonomia.py` – zarządzanie punktami ekonomicznymi generałów
- `gui/panel_generala.py` – aktualizacja panelu ekonomicznego generała
- `main.py` lub `main_alternative.py` – pętla główna gry, wywołanie mechanizmu po każdej turze

## 5. Dodatkowe uwagi

- Wartość przekazywana co turę jest zawsze liczona od wartości początkowej, nie od aktualnej.
- Mechanizm działa automatycznie po każdej turze.
- Punkty mogą być konsumowane przez różne nacje w różnych turach (jeśli zmieni się kontrola nad polem).

**Pliki pomocnicze:**
- `core/ekonomia.py`
- `engine/board.py`
- `engine/token.py`
- `main.py`
- `main_alternative.py`
- `gui/panel_generala.py`

---

**Akceptacja planu oznacza przejście do implementacji.**
