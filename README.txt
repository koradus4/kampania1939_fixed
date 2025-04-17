### Plan implementacji systemu ekonomii i zarządzania czasem w grze

#### 1. Zmiana systemu ekonomii
- **Cel**: Uproszczenie systemu ekonomii i dodanie generowania punktów ekonomicznych oraz punktów specjalnych dla generałów.
- **Kroki**:
  1. Usuń wszystkie obecne funkcje w pliku `ekonomia.py`.
  2. Dodaj mechanizm generowania punktów ekonomicznych (1-100) dla generałów co pełną turę.
  3. Dodaj generowanie 1 punktu specjalnego na turę dla każdego generała.
  4. Wyświetlaj punkty ekonomiczne i specjalne w panelu generała w osobnej ramce.
  5. Dodaj możliwość rozdysponowywania punktów ekonomicznych na dowódców.

#### 2. Dodanie wyboru czasu w ekranie startowym
- **Cel**: Umożliwienie graczom wyboru czasu na podturę dla generałów i dowódców.
- **Kroki**:
  1. W pliku `ekran_startowy.py` dodaj nowe pola wyboru (`ttk.Combobox`) obok wyboru nacji.
  2. Domyślnie ustaw czas na 5 minut dla generała i po 5 minut dla dowódców (łącznie 15 minut).
  3. Waliduj, aby suma czasu dla jednej nacji wynosiła dokładnie 15 minut.
  4. Zapisz wybrany czas w obiekcie gracza (`Gracz`).

#### 3. Modyfikacja paneli graczy
- **Cel**: Wyświetlanie pozostałego czasu oraz punktów ekonomicznych w panelach generałów i dowódców.
- **Kroki**:
  1. W plikach `panel_generalapolska.py` i `panel_dowodcypolska1.py` dodaj nową ramkę z opisem "Czas" i "Punkty ekonomiczne".
  2. Wyświetlaj pozostały czas w formacie minut i sekund.
  3. Aktualizuj czas co sekundę.
  4. Dodaj przycisk "Kup dodatkowy czas" w panelu generała, który pozwoli na zakup czasu kosztem punktów ekonomicznych.
  5. Zaktualizuj punkty ekonomiczne i czas w panelach dowódców.

#### Kolejność implementacji
1. **Zmiana systemu ekonomii**.
2. **Dodanie wyboru czasu w ekranie startowym**.
3. **Modyfikacja paneli graczy**.

#### Docelowe funkcjonalności
- Generałowie otrzymują punkty ekonomiczne (1-100) i 1 punkt specjalny co turę.
- Generałowie mogą rozdysponowywać punkty ekonomiczne na dowódców.
- Gracze wybierają czas na podtury w ekranie startowym.
- Czas i punkty ekonomiczne są wyświetlane w panelach graczy.
- Generałowie mogą kupować dodatkowy czas kosztem punktów ekonomicznych.