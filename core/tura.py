"""
Moduł logiki tury gry: zmiana kolejki graczy i związane z tym operacje.
"""
def end_turn(economy_system, current_nation, unit_count, income=100, cost_per_unit=10):
    """
    Kończy turę aktualnego gracza, przetwarza ekonomię i ustala następnego gracza.
    Zwraca krotkę (next_nation, next_player) dla kolejnej tury.
    """
    # Przetwórz ekonomię dla kończącego turę gracza
    economy_system.process_turn(nation=current_nation, income=income, cost_per_unit=cost_per_unit, unit_count=unit_count)
    # Ustal kolejnego gracza i jego nację
    if current_nation == "Polska":
        return "Niemcy", "Gracz 2"
    else:
        return "Polska", "Gracz 1"

def is_turn_active(nation, current_turn_nation):
    """
    Sprawdza, czy podana nacja (nation) ma obecnie aktywną turę.
    """
    nation_lower = nation.lower()
    current_lower = current_turn_nation.lower()
    # Porównanie po fragmencie nazwy (obsługuje np. "polskie" vs "Polska")
    if ("pol" in nation_lower and "pol" in current_lower) or (("niem" in nation_lower or "ger" in nation_lower) and ("niem" in current_lower or "ger" in current_lower)):
        return True
    return False
