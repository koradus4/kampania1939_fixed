# Checklist: Migracja obsługi mapy i żetonów do silnika engine/

## Cel
Całkowite przejście z archiwalnych plików `archiwum_model/mapa.py`, `archiwum_model/zetony.py`, `archiwum_model/hex_utils.py` na rozwiązania z katalogu `engine/`.

---

## Kroki migracji

- ~~1. Przeanalizuj, które funkcje/klasy z archiwum_model są jeszcze używane w GUI/testach.~~
- ~~2. Zidentyfikuj brakujące funkcjonalności w `engine/board.py`, `engine/token.py`, `engine/hex_utils.py` i uzupełnij je, jeśli potrzeba.~~
- ~~3. Zmień importy w GUI i testach z `archiwum_model.mapa`, `archiwum_model.zetony`, `archiwum_model.hex_utils` na odpowiednie z `engine/`.~~
- ~~4. Przetestuj działanie PanelMapa, PanelGenerala, PanelDowodcy po zmianie importów.~~
- ~~5. Usuń pliki z `archiwum_model/` po pełnej migracji i potwierdzeniu poprawności działania.~~
- ~~6. Zaktualizuj dokumentację projektu (README, PLAN_MIGRACJI.md) o nową architekturę mapy/żetonów.~~

---

## Status migracji mapy i żetonów

- ~~Cała logika mapy i żetonów przeniesiona do silnika (engine/board.py, engine/token.py, engine/hex_utils.py)~~
- ~~GUI korzysta wyłącznie z silnika (brak zależności od archiwum_model)~~
- ~~Pliki archiwalne (mapa.py, zetony.py, hex_utils.py) usunięte~~
- ~~Testy jednostkowe i integracyjne przechodzą poprawnie (poza środowiskowymi problemami z Tkinter)~~
- ~~Checklistę migracji można uznać za zamkniętą~~

## Nowa architektura

- Mapa: engine/board.py (klasa Board, metody geometryczne, overlay, pathfinding)
- Żetony: engine/token.py (klasa Token, ładowanie z JSON, obsługa pozycji)
- Funkcje geometryczne: engine/hex_utils.py
- GUI: korzysta z Board i Token przez GameEngine

## Dalsze kroki
- (Opcjonalnie) Rozbudowa testów edge-case, AI, wydajnościowych
- (Opcjonalnie) Usunięcie pliku CHECKLISTA_MIGRACJI_MAPA_ZETONY.md po akceptacji
