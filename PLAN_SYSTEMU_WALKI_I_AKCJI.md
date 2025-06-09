# Plan systemu walki – wersja 1 (zatwierdzony)

## 2. Liczba ataków
- Atakujący może wykonać tyle ataków, ile ma niewykorzystanych punktów ruchu (`move`).
- Każdy atak kosztuje 1 punkt ruchu żetonu atakującego.

## 3. Rozstrzyganie pojedynczego ataku
- **Atakujący:**
  - Bierze swój `attack.value`, losuje mnożnik z zakresu 0,8–1,2 i mnoży.
  - Wynik to liczba ran zadanych obrońcy (odejmowane od `combat_value` obrońcy).
- **Obrońca:**
  - Suma: `defense_value` + modyfikator terenu (`defense_mod` z mapy).
  - Wynik mnoży przez losowy mnożnik 0,8–1,2.
  - Wynik to liczba ran zadanych atakującemu (odejmowane od `combat_value` atakującego).

## 4. Kolejne ataki i ruch
- Jeśli atakującemu zostały punkty ruchu, może atakować ponownie lub ruszyć się.

## 5. Eliminacja żetonu
- Jeśli `combat_value` obrońcy spadnie do 0 lub poniżej:
  - Losowanie 50% szans:
    - Jeśli się uda – obrońca przeżywa z 1 punktem `combat_value` i cofa się o 1 pole.
    - Jeśli nie – żeton jest usuwany z planszy.
- Jeśli `combat_value` atakującego spadnie do 0 lub poniżej:
  - Atakujący nie przeprowadza żadnych testów – żeton jest natychmiast eliminowany z planszy.

## 6. Wizualizacja ataku
- Po kliknięciu na żeton przeciwnika pojawia się okno potwierdzenia ataku (np. "Czy chcesz zaatakować ten żeton?" z przyciskami TAK/NIE).
- Po potwierdzeniu ataku:
  - Pole z atakującym żetonem podświetla się na zielono (delikatna mgiełka).
  - Pole z broniącym żetonem podświetla się na czerwono (delikatna mgiełka).
- Po rozstrzygnięciu ataku:
  - Jeśli broniący zostaje wyeliminowany: żeton broniącego miga kilka razy na czerwono, po czym znika z planszy.
  - Jeśli broniący przeżywa z 1 punktem combat_value: żeton broniącego miga na czerwono, po czym automatycznie cofa się o jedno pole i wraca do normalnego wyglądu.
  - Jeśli atakujący zostaje wyeliminowany: żeton atakującego miga kilka razy na czerwono, po czym znika z planszy.
- Po zakończeniu animacji wszystkie pola i żetony wracają do normalnego wyglądu.

---

*Plan zaakceptowany do realizacji. W razie potrzeby będzie rozbudowywany o kolejne szczegóły.*
