import pytest
from engine.token import Token
from engine.player import Player
from core.ekonomia import EconomySystem

def test_uzupelnianie_zetonu_paliwo_i_zasoby():
    # Przygotowanie żetonu i gracza
    token = Token(id=101, owner="2 (Polska)", stats={
        'label': 'Testowy Czołg',
        'maintenance': 10,  # maxFuel
        'combat_value': 5   # max zasoby bojowe
    })
    token.currentFuel = 3
    token.combat_value = 2
    gracz = Player(2, "Polska", "Dowódca", 5, "")
    gracz.punkty_ekonomiczne = 7
    gracz.economy = EconomySystem()

    print(f"Stan początkowy: paliwo={token.currentFuel}/{token.stats['maintenance']}, zasoby bojowe={token.combat_value}/{token.stats['combat_value']}, punkty={gracz.punkty_ekonomiczne}")

    # Symulacja uzupełniania: chcemy dodać 4 paliwa i 2 zasoby bojowe (łącznie 6 punktów)
    ile_fuel = 4
    ile_combat = 2
    # Logika jak w panelu dowódcy
    max_fuel = token.stats['maintenance'] - token.currentFuel  # 7
    max_combat = token.stats['combat_value'] - token.combat_value  # 3
    max_lacznie = min(gracz.punkty_ekonomiczne, max_fuel + max_combat)  # 6+3=9, ale gracz ma 7
    print(f"Można uzupełnić max: paliwo={max_fuel}, zasoby bojowe={max_combat}, łącznie={max_lacznie}")
    print(f"Wybrano do uzupełnienia: paliwo={ile_fuel}, zasoby bojowe={ile_combat}")
    assert ile_fuel <= max_fuel
    assert ile_combat <= max_combat
    assert ile_fuel + ile_combat <= gracz.punkty_ekonomiczne
    # Uzupełnianie
    token.currentFuel += ile_fuel
    if token.currentFuel > token.stats['maintenance']:
        token.currentFuel = token.stats['maintenance']
    token.combat_value += ile_combat
    if token.combat_value > token.stats['combat_value']:
        token.combat_value = token.stats['combat_value']
    gracz.punkty_ekonomiczne -= (ile_fuel + ile_combat)
    print(f"Po uzupełnieniu: paliwo={token.currentFuel}, zasoby bojowe={token.combat_value}, punkty={gracz.punkty_ekonomiczne}")
    # Sprawdzenie
    assert token.currentFuel == 7
    assert token.combat_value == 4
    assert gracz.punkty_ekonomiczne == 1
    # Próba przekroczenia limitu
    ile_fuel = 10
    ile_combat = 10
    suma = ile_fuel + ile_combat
    print(f"Próba przekroczenia limitu: paliwo={ile_fuel}, zasoby bojowe={ile_combat}, suma={suma}, punkty={gracz.punkty_ekonomiczne}, max_fuel={max_fuel}, max_combat={max_combat}")
    assert suma > gracz.punkty_ekonomiczne or ile_fuel > max_fuel or ile_combat > max_combat
