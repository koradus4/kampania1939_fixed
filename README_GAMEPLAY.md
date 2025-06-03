# Jak grać w grę planszową "Kampania 1939" (wersja cyfrowa)

## Cel gry
Celem gry jest poprowadzenie swoich jednostek do zwycięstwa poprzez manewrowanie, walkę i zajmowanie kluczowych obszarów mapy. Każdy gracz dowodzi armią (np. Polska, Niemcy) i rozgrywa naprzemienne tury.

## Podstawowe zasady
- Gra toczy się na heksagonalnej mapie z różnymi typami terenu (pole, las, rzeka, miasto, wzgórze).
- Każdy gracz posiada żetony reprezentujące oddziały (piechota, czołgi, artyleria itp.).
- Każdy żeton ma statystyki: atak (zasięg i siła), obrona, punkty ruchu (MP), tryb ruchu, paliwo.
- Tura gracza składa się z fazy ruchu i fazy walki.

## Ruch
- Każdy żeton ma pulę punktów ruchu (MP) na turę.
- Koszt ruchu na pole = 1 + modyfikator terenu (`move_mod`), np. las = +2, rzeka = +3.
- Nie można wejść na pole zajęte przez sojusznika ani na pole nieprzejezdne (move_mod = -1).
- Po ruchu, jeśli żeton wejdzie w zasięg wrogich jednostek, może zostać zaatakowany (atak reakcyjny).

## Walka
- Atak można wykonać na wrogi żeton w zasięgu ataku (zależnie od statystyk i terenu).
- W walce uwzględniane są: siła ataku, obrona (z modyfikatorem terenu), wsparcie sojuszników (ogień krzyżowy), losowość.
- Wsparcie: sojusznicy w zasięgu widzenia i ataku mogą dodać bonus do ataku.
- Wynik walki: jeśli atak > obrona – obrońca zostaje zniszczony; jeśli nie – atakujący traci zasób bojowy.
- Każda akcja (atak, wsparcie, ruch) zużywa punkty ruchu (MP).

## Efekty terenu
- Teren wpływa na koszt ruchu i obronę (np. las utrudnia ruch i zwiększa obronę).
- Efekty terenu są widoczne w panelu info po kliknięciu na pole lub żeton.

## Interfejs
- Kliknij żeton, aby go wybrać i zobaczyć szczegóły.
- Kliknij pole na mapie, aby wydać rozkaz ruchu lub ataku.
- Żetony biorące udział w walce mają pomarańczową obwódkę i status "WALCZY!".
- Panel info pokazuje aktualne MP, efekty terenu, status walki.

## Dodatkowe zasady
- Punkty ruchu resetują się na początku każdej tury.
- Nie można wykonywać akcji bez punktów ruchu.
- Po zakończeniu tury kliknij przycisk "Koniec tury".

## Wskazówki dla testera
- Przetestuj różne typy terenu, wsparcie, ataki reakcyjne, blokady ruchu.
- Zwracaj uwagę na komunikaty o błędach i czytelność interfejsu.
- Jeśli znajdziesz błąd lub niejasność, zapisz sytuację i zgłoś ją zespołowi.

Powodzenia i miłej gry!
