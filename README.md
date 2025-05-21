# Kampania 1939 – Modularny silnik gry

## Opis projektu

Projekt to modularny silnik gry strategicznej z pełnym oddzieleniem logiki gry od GUI. Cała logika mapy, żetonów i graczy znajduje się w katalogu `engine/`, a interfejs graficzny korzysta wyłącznie z tych klas przez `GameEngine`.

## Architektura

- **Mapa:** `engine/board.py` (klasa `Board`, pathfinding, overlay, obsługa pól)
- **Żetony:** `engine/token.py` (klasa `Token`, ładowanie z JSON, obsługa pozycji)
- **Gracze:** `engine/player.py` (klasa `Player`)
- **Funkcje geometryczne:** `engine/hex_utils.py`
- **Silnik gry:** `engine/engine.py` (klasa `GameEngine`, integracja mapy, żetonów, graczy)
- **GUI:** katalog `gui/` (np. `panel_mapa.py`, `panel_generala.py`, `panel_dowodcy.py`)

## Najważniejsze cechy

- Całkowite oddzielenie logiki gry od GUI
- Seed-owalność i testowalność silnika
- Przejrzysta struktura katalogów
- Testy jednostkowe i integracyjne (katalog `tests/`)
- Łatwe rozszerzanie o AI, nowe akcje, nowe typy żetonów

## Przykład użycia silnika

```python
from engine.engine import GameEngine
engine = GameEngine(
    map_path='assets/mapa_dane.json',
    tokens_index_path='assets/tokens/index.json',
    start_tokens_path='assets/start_tokens.json',
    seed=123
)
state = engine.get_state()
for token in state['tokens']:
    print(token['id'], token['q'], token['r'])
```

## Uruchamianie testów

```bash
pytest tests/ --maxfail=3 --disable-warnings -v
```

## Środowisko uruchomieniowe

Projekt rozwijany i testowany jest na systemie Windows 10/11 z Pythonem 3.12. Zalecane środowisko do uruchamiania gry to:

- Python 3.12 (do pobrania: https://www.python.org/downloads/)
- System operacyjny: Windows 10 lub 11
- Zalecane IDE: Visual Studio Code (https://code.visualstudio.com/) lub PyCharm
- Wymagane biblioteki: Pillow (do obsługi grafiki), tkinter (GUI, standardowo w Pythonie na Windows)

Aby zainstalować wymagane biblioteki, uruchom w terminalu:

```
pip install pillow
```

W przypadku problemów z tkinter na innych systemach niż Windows, należy doinstalować odpowiedni pakiet dla swojej dystrybucji.

## Autorzy i licencja

Projekt edukacyjny, 2023–2025. Wszelkie prawa zastrzeżone.
