# PLAN_REFAKTORYZACJI_ENGINE_ACTIONS.md

## Cel
Dokonać refaktoryzacji i optymalizacji pliku `engine/action.py` w grze planszowej 1939, aby poprawić czytelność, wydajność, testowalność i łatwość rozbudowy kodu.

## Główne założenia
- Rozdzielenie logiki akcji na mniejsze, czytelne metody/funkcje pomocnicze.
- Wydzielenie powtarzających się fragmentów (np. sprawdzanie widoczności, kosztów ruchu, obsługa paliwa) do osobnych funkcji lub klas narzędziowych.
- Uporządkowanie i typowanie argumentów oraz atrybutów klas akcji.
- Ułatwienie testowania jednostkowego poprzez minimalizację zależności i efektów ubocznych.
- Optymalizacja pętli i warunków (np. sprawdzanie widoczności, ścieżek, blokad ruchu).
- Dodanie dokumentacji i komentarzy do kluczowych fragmentów.

## Proponowane kroki
1. **Analiza i rozbicie klasy MoveAction:**
   - Wydzielenie metod pomocniczych: znajdowanie żetonu, sprawdzanie blokad, obliczanie kosztów, aktualizacja widoczności.
   - Przeniesienie logiki widoczności do osobnej funkcji (np. `update_temp_visibility`).
   - Uproszczenie obsługi trybów ruchu i mnożników.
2. **Refaktoryzacja klasy CombatAction:**
   - Wydzielenie logiki sprawdzania dystansu, porównywania wartości bojowych, usuwania żetonów.
3. **Dodanie typowania (type hints) i docstringów.**
4. **Dodanie testów jednostkowych dla nowych funkcji pomocniczych.**
5. **Optymalizacja pętli i warunków (np. unikanie niepotrzebnych iteracji po wszystkich żetonach).**
6. **Przeniesienie powtarzalnych fragmentów do narzędziowych modułów (np. utils/engine_helpers.py).**
7. **Dokumentacja zmian i migracja testów.**

## Potencjalne zyski
- Łatwiejsza rozbudowa o nowe typy akcji.
- Szybsze i bardziej niezawodne testowanie.
- Zmniejszenie liczby błędów i duplikacji kodu.
- Lepsza wydajność przy dużej liczbie żetonów i graczy.

## Dalsze kroki
- Po refaktoryzacji: aktualizacja dokumentacji technicznej i instrukcji dla deweloperów.
- Przegląd i ewentualna refaktoryzacja innych plików silnika (np. board.py, token.py) według podobnych zasad.

---

*Ten dokument powstał jako plan refaktoryzacji pliku `engine/action.py` i powiązanych elementów silnika gry. Szczegóły i harmonogram do ustalenia podczas realizacji.*
