# Plan wdrożenia systemu zakupu i wystawiania nowych jednostek przez generała i dowódców

## Cel
Umożliwić generałowi zakup nowych jednostek za punkty ekonomiczne dla swoich dowódców, a dowódcom – wystawianie tych jednostek na mapie w wyznaczonych punktach zrzutu.

---

## 3. Wystawianie nowych jednostek przez dowódcę

### 3.1. Przycisk w panelu dowódcy
- [ ] Dodaj przycisk „Wystaw nowe jednostki” w `PanelDowodcy`.
- [ ] Jeśli są dostępne nowe żetony, przycisk może migać.

### 3.2. Okno wystawiania (deploy_new_tokens)
- [ ] Może przeciągać żetony na wybrane heksy (punkty zrzutu).
- [ ] Może cofnąć wystawienie (reset heksu – zwraca żeton do puli).
- [ ] Po zatwierdzeniu eksportuje rozmieszczenie do pliku (np. `assets/new_tokens_deployed_{dowodca_id}.json`).

### 3.3. Synchronizacja

---

## 4. Integracja i bezpieczeństwo
- [ ] Punkty ekonomiczne są aktualizowane na bieżąco (panel generała, panel dowódcy).

---

## 5. Testy i UX
- [ ] Testy: zakup, przydział, wystawienie, synchronizacja punktów, blokady.
- [ ] Uproszczenie interfejsów (sklep, wystawianie) do minimum.
- [ ] Komunikaty o błędach i sukcesie.

---

## 6. Pliki do utworzenia/zmodyfikowania
- [ ] `gui/panel_dowodcy.py` – przycisk i obsługa wystawiania
- [x] `gui/deploy_new_tokens.py` – okno wystawiania (istnieje, wyświetla nowe żetony dowódcy)
- [ ] `assets/new_tokens_deployed_{dowodca_id}.json` – eksport rozmieszczenia
- [ ] Ewentualnie: modyfikacje w silniku gry, jeśli wymagane

---

## 7. Kolejność realizacji
3. Przycisk i okno wystawiania w panelu dowódcy
4. Mechanizm eksportu rozmieszczenia
5. Synchronizacja punktów i blokady
6. Testy i poprawki UX

---

## 8. Uwagi
- Wersjonować pliki i testować każdy etap osobno.
- Dbać o spójność ścieżek i formatów plików.
- W razie potrzeby rozbudować plan o szczegóły implementacyjne.

---

**Plik zaktualizowany automatycznie przez GitHub Copilot – usunięto zrealizowane etapy na podstawie analizy kodu.**
