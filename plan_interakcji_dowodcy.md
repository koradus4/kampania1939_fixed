# PLAN INTERAKCJI DOWÓDCY Z ŻETONAMI (BEZ AKCJI SPECJALNYCH)

1. Dowódca klika na swój żeton na mapie.
    - Żeton zostaje podświetlony (zaznaczony).
    - Wyświetlane jest menu dostępnych akcji:
      - Ruch
      - Atak

2. Dowódca wybiera akcję z menu:
    - Jeśli wybierze Ruch:
        - Wskazuje pole docelowe na mapie.
        - Sprawdzany jest koszt ruchu oraz dostępność punktów ruchu.
        - Jeśli ruch jest możliwy, żeton przesuwa się na wybrany heks, a punkty ruchu są odejmowane.
    - Jeśli wybierze Atak:
        - Wskazuje żeton przeciwnika w zasięgu ataku.
        - Przeprowadzana jest symulacja starcia (odejmowane są wartości bojowe, sprawdzane efekty).
        - Jeśli żeton przeciwnika zostaje zniszczony, jest usuwany z mapy.

3. Podczas ruchu lub ataku:
    - Sprawdzane są efekty widoczności i reakcje przeciwnika (np. automatyczny ostrzał, ujawnienie żetonów).

4. Dowódca może powtarzać akcje żetonem, aż do wyczerpania punktów akcji, lub wybrać inny żeton.

5. Po zakończeniu wszystkich akcji dowódca kończy turę.
    - Stan mapy i żetonów jest aktualizowany.
    - Kontrola przechodzi do kolejnego gracza.
