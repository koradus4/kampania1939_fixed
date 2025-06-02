# PLAN_REFAKTORYZACJI_SILNIKA.md

## Cel
Przeprowadzenie kompleksowej refaktoryzacji i optymalizacji silnika gry planszowej 1939 (Python/Tkinter) w celu poprawy czytelności, wydajności, łatwości rozwoju oraz testowalności kodu.

## Zakres refaktoryzacji

1. **Wyodrębnienie funkcji pomocniczych**
   - Przenieść powtarzające się fragmenty kodu do dedykowanych funkcji/metod.
   - Uporządkować logikę ruchu, widoczności, ekonomii, obsługi nacji.

2. **Optymalizacja dostępu do żetonów i planszy**
   - Zoptymalizować wyszukiwanie żetonów (np. przez indeksowanie po id/pozycji).
   - Usprawnić operacje na planszy (np. cache pól, lepsze API board).

3. **Lepsza obsługa nacji i właścicieli**
   - Ujednolicić sposób identyfikacji właściciela żetonu (np. przez obiekt Player zamiast stringów).
   - Wprowadzić typy wyliczeniowe dla nacji.

4. **Typowanie i docstringi**
   - Wprowadzić typowanie statyczne (type hints) dla wszystkich klas i metod.
   - Dodać docstringi opisujące przeznaczenie i parametry funkcji/metod.

5. **Podział na mniejsze moduły**
   - Rozdzielić duże pliki na mniejsze, logiczne moduły (np. osobno ruch, walka, widoczność, ekonomia).
   - Wydzielić interfejsy do komunikacji GUI ↔ silnik.

6. **Testy jednostkowe i integracyjne**
   - Uzupełnić i rozbudować testy jednostkowe dla kluczowych funkcji silnika.
   - Przygotować testy integracyjne dla scenariuszy gry.

7. **Optymalizacja wydajności**
   - Przeanalizować krytyczne ścieżki (profilowanie).
   - Wprowadzić optymalizacje tam, gdzie występują wąskie gardła.

8. **Uspójnienie stylu kodu**
   - Zastosować jednolity styl kodowania (PEP8, black, isort).
   - Uporządkować nazewnictwo zmiennych, klas, funkcji.

## Proponowana kolejność prac
1. Analiza i podział istniejącego kodu na logiczne moduły.
2. Refaktoryzacja logiki ruchu i widoczności.
3. Refaktoryzacja obsługi ekonomii i punktów ekonomicznych.
4. Ujednolicenie obsługi nacji i właścicieli.
5. Wprowadzenie typowania i docstringów.
6. Rozbudowa testów.
7. Optymalizacje wydajnościowe.
8. Finalne porządki i dokumentacja.

## Uwagi
- Refaktoryzacja powinna być realizowana etapami, z zachowaniem działającej wersji gry po każdym etapie.
- Każda większa zmiana powinna być pokryta testami.
- Wskazane jest utworzenie osobnej gałęzi w repozytorium na czas refaktoryzacji.

---

Plik ten stanowi plan działania do wdrożenia w przyszłości. Wszelkie sugestie i uwagi proszę dopisywać poniżej.
