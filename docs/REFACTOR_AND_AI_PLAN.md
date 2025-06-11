# PLAN REFAKTORYZACJI ENGINE/ACTION.PY

## CELE
1. Uproszczenie struktury akcji
2. Lepsze type hints
3. Podzial na mniejsze, testowalne funkcje
4. Przygotowanie dla integracji z AI

## ETAPY

### ETAP 1: Analiza obecnej struktury
- [ ] Identyfikacja wszystkich typow akcji
- [ ] Mapowanie zaleznosci miedzy akcjami
- [ ] Wylistowanie funkcji do podzialu

### ETAP 2: Refaktoryzacja
- [ ] Podzial execute_action na mniejsze funkcje
- [ ] Stworzenie oddzielnych klas dla typow akcji
- [ ] Dodanie type hints
- [ ] Dokumentacja wszystkich funkcji

### ETAP 3: Testy
- [ ] Aktualizacja istniejacych testow
- [ ] Dodanie testow jednostkowych dla nowych klas
- [ ] Testy integracyjne

### ETAP 4: Integracja z AI
- [ ] Interface dla AI do podejmowania decyzji
- [ ] Funkcje pomocnicze dla oceny stanu gry
- [ ] Integracja z systemem dowodcow

## PRZYGOTOWANIE DLA AI DOWODCOW

### Struktura AI:
```
ai/
├── commanders/
│   ├── base_commander.py       - Bazowa klasa
│   ├── aggressive_commander.py - Agresywny styl
│   ├── defensive_commander.py  - Defensywny styl
│   └── balanced_commander.py   - Zbalansowany styl
├── decision_trees/
│   ├── combat_decisions.py     - Decyzje bojowe
│   ├── movement_decisions.py   - Decyzje ruchu
│   └── economic_decisions.py   - Decyzje ekonomiczne
└── strategies/
    ├── early_game.py          - Strategia wczesnej gry
    ├── mid_game.py            - Strategia srodkowej gry
    └── late_game.py           - Strategia poznej gry
```

### Interface AI-Engine:
- `GameState` - snapshot stanu gry dla AI
- `ActionEvaluator` - ocena akcji przez AI
- `DecisionMaker` - podejmowanie decyzji przez AI
