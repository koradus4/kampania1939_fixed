# TODO na dziś – refaktoryzacja przepływu stanu gry (kampania1939)

## Cel
Zapewnić spójny, globalny stan gry (plansza, żetony, tura) współdzielony przez wszystkie panele GUI i silnik gry. Usunąć problem resetowania stanu przy każdej turze/panelu.

## Zadania

~~1. **GameEngine jako źródło prawdy**~~
   - ~~Upewnić się, że `GameEngine` przechowuje aktualny stan planszy (`Board`), żetonów i tury.~~
   - ~~Dodać metody do pobierania i aktualizacji stanu (jeśli brakuje).~~

~~2. **Refaktoryzacja PanelMapa i innych paneli**~~
   - ~~Zamiast tworzyć nowe instancje `Board` i żetonów, panele GUI mają korzystać z referencji do obiektu `GameEngine` (lub jego atrybutów).~~
   - ~~Przekazywać instancję `GameEngine` do paneli przy ich tworzeniu.~~
   - ~~Usunąć wczytywanie żetonów/mapy w panelach – korzystać z tych z silnika.~~

~~3. **TurnManager i cykl gry**~~
   - ~~`TurnManager` powinien operować na jednej instancji `GameEngine` przez całą grę.~~
   - ~~Przekazywać tę instancję do paneli przy zmianie tury.~~

~~4. **Testy**~~
   - ~~Sprawdzić, czy zmiany wprowadzone przez gracza (np. ruch żetonu) są widoczne w kolejnej turze i panelu.~~
   - ~~Dodać testy integracyjne (np. w `tests/test_panel_mapa_integration.py`).~~

## Priorytet
- Zacząć od PanelMapa, GameEngine, TurnManager.
- Zmiany w innych panelach (PanelGenerała, PanelDowódcy) analogicznie.

## Efekt końcowy
- Stan gry jest jeden, współdzielony, nie resetuje się między turami/panelami.
- Każda zmiana wprowadzona przez gracza jest zachowana i widoczna dla wszystkich.

---

**Dodatkowo:**
- Po zakończeniu refaktoryzacji – przetestować pełny cykl tury (ruch, zniszczenie żetonu, przejście do kolejnego panelu/tury).
- Zgłosić ewentualne problemy lub pomysły na dalsze usprawnienia.
