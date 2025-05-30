# Plan realizacji warstwy widoczności żetonów (Fog of War)

## 1. Model widoczności
- Każdy gracz-dowódca posiada:
  - `visible_hexes` – zbiór heksów widocznych na podstawie zasięgu widzenia jego żetonów.
  - `visible_tokens` – zbiór żetonów widocznych (na tych heksach).
- Generał posiada:
  - `visible_hexes` – suma widocznych heksów wszystkich dowódców swojej nacji.
  - `visible_tokens` – suma żetonów widocznych na tych heksach (dowolnej nacji).

## 2. Aktualizacja widoczności
- Po każdym ruchu, rozstawieniu lub usunięciu żetonu aktualizuj widoczność dla wszystkich graczy.
- Po rozpoczęciu tury przelicz widoczność dla każdego gracza.

## 3. Renderowanie mapy
- Renderuj tylko żetony z `visible_tokens` gracza.
- Żetony poza zasięgiem widzenia nie są rysowane i nie są dostępne do kliknięcia.

## 4. Obsługa kliknięć
- Kliknięcie na heks bez widocznego żetonu nie wywołuje panelu informacji o żetonie.
- Jeśli na heksie jest żeton, ale nie jest widoczny dla gracza, kliknięcie nie robi nic (panel informacyjny się nie zmienia lub jest czyszczony).

## 5. Widoczność sojusznicza
- Dowódca widzi tylko swoje żetony oraz żetony przeciwnika, jeśli są w zasięgu widzenia jego żetonów.
- Nie widzi żetonów innych dowódców tej samej nacji, chyba że są w zasięgu widzenia jego własnych żetonów.

## 6. Widoczność generała
- Generał widzi sumę widoczności wszystkich swoich dowódców (wszystkie heksy widziane przez żetony jego nacji).
- Generał widzi wszystkie żetony (własne, sojusznicze i wrogie), które znajdują się na tych heksach.

## 7. Implementacja – kroki techniczne
5. W panelu mapy:
   - Renderuj tylko żetony z `visible_tokens` gracza.
   - Obsługa kliknięcia: jeśli na klikniętym heksie nie ma widocznego żetonu, nie wywołuj panelu informacji.

## 8. Przykład działania kliknięcia
- Gracz klika prawym na heks:
  - Jeśli na tym heksie jest żeton z `visible_tokens` → pokazuje panel informacji.
  - Jeśli nie ma widocznego żetonu → panel informacji się nie zmienia lub jest czyszczony.

## 9. Testy i walidacja
- Przetestuj przypadki: żeton własny, żeton sojuszniczy, żeton przeciwnika, żeton poza zasięgiem.
- Sprawdź, czy nie da się „wyklikać” niewidocznych żetonów.

---

**Nazwa pliku:** `plan_fog_of_war_widocznosc_zetonow.md`
