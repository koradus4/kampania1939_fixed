import pytest
from engine.token import Token

def test_przeliczanie_punktow_ruchu_po_zmianie_trybu():
    # Testuje czy zmiana trybu nie resetuje punktów ruchu, tylko przelicza proporcjonalnie
    t = Token(id="test", owner="1 (Polska)", stats={"move": 10, "defense_value": 4})
    t.apply_movement_mode(reset_mp=True)  # start: combat, 10/10
    assert t.currentMovePoints == 10
    # Zużyj 4 punkty ruchu
    t.currentMovePoints -= 4
    # Zmień tryb na marszowy (x1.5)
    t.movement_mode = "march"
    t.apply_movement_mode(reset_mp=False)
    # W trybie marszowym max=15, zużyto 4, więc powinno zostać 11
    assert t.maxMovePoints == 15
    assert t.currentMovePoints == 11, f"Po zmianie trybu powinno zostać 11, jest {t.currentMovePoints}"
    # Zmień tryb na zwiad (x0.5)
    t.movement_mode = "recon"
    t.apply_movement_mode(reset_mp=False)
    # W trybie zwiad max=5, zużyto 4, więc powinno zostać 1
    assert t.maxMovePoints == 5
    assert t.currentMovePoints == 1, f"Po zmianie trybu powinno zostać 1, jest {t.currentMovePoints}"
    # Zmień tryb na bojowy (x1)
    t.movement_mode = "combat"
    t.apply_movement_mode(reset_mp=False)
    # W trybie bojowym max=10, zużyto 4, więc powinno zostać 6
    assert t.maxMovePoints == 10
    assert t.currentMovePoints == 6, f"Po powrocie do bojowego powinno zostać 6, jest {t.currentMovePoints}"
    print("[TEST] test_przeliczanie_punktow_ruchu_po_zmianie_trybu OK")
