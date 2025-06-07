# test_walka_przyklad.py
# Przykładowy test systemu walki – sprawdza, czy walka między żetonami działa poprawnie

def test_walka():
    # Przygotowanie żetonów
    zeton_atakujacy = Zeton(zycie=100, sila_ataku=10)
    zeton_broniacy = Zeton(zycie=100, sila_obrony=5)

    # Atak
    zeton_atakujacy.atak(zeton_broniacy)

    # Sprawdzenie wyników
    assert zeton_broniacy.zycie == 95, "Życie broniącego się żetonu nie zgadza się po ataku"
    assert zeton_atakujacy.zycie == 100, "Życie atakującego żetonu powinno pozostać bez zmian"

    # Kontratak
    zeton_broniacy.atak(zeton_atakujacy)

    # Sprawdzenie wyników po kontrataku
    assert zeton_atakujacy.zycie == 90, "Życie atakującego żetonu nie zgadza się po kontrataku"
    assert zeton_broniacy.zycie == 95, "Życie broniącego się żetonu powinno pozostać bez zmian po kontrataku"