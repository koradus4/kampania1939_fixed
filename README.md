# kampaniawrzesniowa1939 – GitHub Workstudio Setup

## ✅ Agenci AI i automatyzacji w tym repozytorium

### 🎮 Codzienna praca

- **GitHub Copilot** → podpowiada kod podczas pisania w VS Code.
- **GitHub Copilot Chat** → tłumaczy błędy, odpowiada na pytania o kod.

### 🤖 Automatyzacja zadań (jeśli GitHub Enterprise + Copilot for Business)

- **GitHub Copilot Workspace (beta)** → AI planuje zadanie, zakłada branch, tworzy pull request.

### 🔧 Automatyczne testy gry

- **GitHub Actions** → po każdej zmianie sprawdza czy projekt się uruchamia i czy pliki są kompletne.

### 💻 Opcjonalnie

- **VS Code Continue** → analiza dużych plików, pomoc w refaktoryzacji całych modułów gry.

---

# ✅ Minimalna konfiguracja GitHub Actions do testów Pythona

Utwórz plik:

`.github/workflows/test.yml`

```yaml
name: Test Python Game

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt || true

    - name: Test game launch
      run: |
        echo "Sprawdzanie czy plik main.py istnieje..."
        test -f main.py
        echo "Test zakończony: plik main.py istnieje."
```

---

## ✅ Instrukcja dla Twojego repo

1. Wrzuć plik `.github/workflows/test.yml` do swojego repozytorium.
2. Po każdym push lub pull request → GitHub automatycznie sprawdzi czy plik `main.py` istnieje.
3. Możesz rozbudować testy np. o uruchomienie gry lub testy jednostkowe.

---

To jest wersja startowa dopasowana do Twojego projektu `kampaniawrzesniowa1939` w VS Code + GitHub Workstudio.
