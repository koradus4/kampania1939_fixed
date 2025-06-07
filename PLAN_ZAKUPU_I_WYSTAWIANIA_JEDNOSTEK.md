# Plan wdrożenia systemu zakupu i wystawiania nowych jednostek przez generała i dowódców

## Cel
Umożliwić generałowi zakup nowych jednostek za punkty ekonomiczne dla swoich dowódców, a dowódcom – wystawianie tych jednostek na mapie w wyznaczonych punktach zrzutu.

---

## 1. Zakup nowych jednostek przez generała

### 1.1. Dodanie przycisku w panelu generała
- Dodaj przycisk „Zakup nowe jednostki” w `PanelGenerala`.
- Po kliknięciu otwiera się nowe okno (nowy plik, np. `gui/token_shop.py`).

### 1.2. Okno zakupu jednostek (token_shop)
- Skopiuj i uprość edytor żetonów (`token_editor_prototyp.py`) do nowego pliku.
- Wyświetl aktualną pulę punktów ekonomicznych generała (odblokowane pole).
- Pozwól na wybór dowódcy, dla którego kupowana jest jednostka.
- Po kliknięciu „Kup”:
  - Odejmij odpowiednią liczbę punktów ekonomicznych.
  - Zapisz żeton do katalogu/folderu „do odbioru” dla wybranego dowódcy (np. `assets/tokens/nowe_dla_{dowodca_id}` lub wpis w JSON).
  - Zaktualizuj pulę punktów w panelu generała.

### 1.3. Synchronizacja punktów
- Po zamknięciu okna zakupów odśwież punkty ekonomiczne w panelu generała.

---

## 2. Przechowywanie nowych jednostek
- Każdy dowódca ma swoją „poczekalnię” na nowe żetony (np. folder lub wpis w pliku JSON).
- Po zakupie żeton trafia do tej poczekalni.

---

## 3. Wystawianie nowych jednostek przez dowódcę

### 3.1. Przycisk w panelu dowódcy
- Dodaj przycisk „Wystaw nowe jednostki” w `PanelDowodcy`.
- Jeśli są dostępne nowe żetony, przycisk może migać.

### 3.2. Okno wystawiania (deploy_new_tokens)
- Skopiuj i uprość edytor mapy (`map_editor_prototyp.py`) do nowego pliku.
- Dowódca widzi tylko swoje nowe żetony i tylko swoje punkty zrzutu.
- Może przeciągać żetony na wybrane heksy (punkty zrzutu).
- Może cofnąć wystawienie (reset heksu – zwraca żeton do puli).
- Po zatwierdzeniu eksportuje rozmieszczenie do pliku (np. `assets/new_tokens_deployed_{dowodca_id}.json`).

### 3.3. Synchronizacja
- Po wystawieniu żetony są już „na mapie” i nie można ich ponownie wystawić.
- W kolejnej turze dowódca może już nimi grać.

---

## 4. Integracja i bezpieczeństwo
- Punkty ekonomiczne są aktualizowane na bieżąco (panel generała, panel dowódcy).
- Blokada ponownego wystawienia tych samych żetonów.
- Mechanizm czyszczenia poczekalni po wystawieniu.

---

## 5. Testy i UX
- Testy: zakup, przydział, wystawienie, synchronizacja punktów, blokady.
- Uproszczenie interfejsów (sklep, wystawianie) do minimum.
- Komunikaty o błędach i sukcesie.

---

## 6. Pliki do utworzenia/zmodyfikowania
- `gui/panel_generala.py` – przycisk i obsługa zakupu
- `gui/token_shop.py` – okno zakupu
- `assets/tokens/nowe_dla_{dowodca_id}/` lub JSON – przechowywanie nowych żetonów
- `gui/panel_dowodcy.py` – przycisk i obsługa wystawiania
- `gui/deploy_new_tokens.py` – okno wystawiania
- `assets/new_tokens_deployed_{dowodca_id}.json` – eksport rozmieszczenia
- Ewentualnie: modyfikacje w silniku gry, jeśli wymagane

---

## 7. Kolejność realizacji
1. Prototyp okna zakupu (sklep generała)
2. Mechanizm zapisu nowych żetonów do poczekalni dowódcy
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

**Plik utworzony automatycznie przez GitHub Copilot na podstawie rozmowy.**
