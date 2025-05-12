# kampania1939_fixed – Konfiguracja GitHub Workstudio

## ✅ Opis projektu

To repozytorium posiada pełną integrację z GitHub Actions w modelu **GitHub Workstudio**. Konfiguracja umożliwia automatyczne testy i sanity check po każdej zmianie w kodzie.

Projekt: **kampania1939_fixed** (gra strategiczna Python + Pygame)

---

## ✅ Agenci Workstudio w projekcie

### 🎮 1. Test Python Game (`.github/workflows/test.yml`)

- Sprawdza, czy istnieje plik `main.py`.
- Uruchamiany po każdym push lub pull request.

### 🎮 2. Test uruchomienia gry z pygame (`.github/workflows/game_run_test.yml`)

- Instalacja `pygame` i uruchomienie gry (`python main.py`).
- Jeżeli gra wymaga GUI, workflow zakończy się komunikatem informacyjnym.

### 🎮 3. Sanity check - struktura projektu (`.github/workflows/sanity_check.yml`)

- Sprawdza, czy istnieją katalogi:
  - `assets`
  - `tokens`

### 🎮 4. Critical files check - pliki projektu (`.github/workflows/critical_files_check.yml`)

- Sprawdza, czy istnieją kluczowe pliki:
  - `main.py` (wymagany)
  - `README.md` (wymagany)
  - `requirements.txt` (opcjonalny, tylko ostrzeżenie)

---

## ✅ Jak dodać nowy workflow

1. Utworzyć plik `.yml` w folderze:

```
kampania1939_fixed/.github/workflows/
```

2. Skorzystać z istniejących przykładów jako wzoru.
3. Wprowadzić własne komendy lub dodatkowe testy.

---

## ✅ Zalecana struktura projektu

```
kampania1939_fixed/
├── assets/
├── tokens/
├── core/
├── gui/
├── model/
├── net/
├── utils/
├── edytory/
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── game_run_test.yml
│       ├── sanity_check.yml
│       └── critical_files_check.yml
├── main.py
├── README.md
├── requirements.txt (opcjonalnie)
```

---

## ✅ Status: KONFIGURACJA KOMPLETNA ✅

To repozytorium posiada w pełni działające GitHub Workstudio, zgodne z najlepszymi praktykami Continuous Integration (CI) dla projektów gier w Python + Pygame.

Repozytorium jest gotowe do dalszego rozwoju oraz potencjalnej migracji do silnika Godot lub dalszego rozwoju w Pygame.
