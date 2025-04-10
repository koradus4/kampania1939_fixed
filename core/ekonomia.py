"""
Moduł systemu ekonomii – zarządza punktami ekonomicznymi i zaopatrzenia oraz wydarzeniami ekonomicznymi.
"""
import random
import copy
from typing import Dict, Any, Optional
from model.zasoby import MAX_ECONOMIC_POINTS, MAX_SUPPLY_POINTS, INITIAL_ECONOMY_DATA, ECONOMIC_EVENTS


class EconomySystem:
    def __init__(self):
        """Inicjalizuje system ekonomii z domyślnymi wartościami dla każdej nacji."""
        self.nations: Dict[str, Dict[str, Any]] = copy.deepcopy(INITIAL_ECONOMY_DATA)

    def get_nation_data(self, nation: str) -> Optional[Dict[str, Any]]:
        """Zwraca dane ekonomiczne (słownik) dla danej nacji."""
        return self.nations.get(nation)

    def display_status(self, nation: str) -> str:
        """Zwraca tekstowy status ekonomii dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        return f"Punkty ekonomiczne: {data['economic_points']}, Punkty zaopatrzenia: {data['supply_points']}"

    def modify_economic_points(self, nation: str, amount: int) -> int:
        """Modyfikuje punkty ekonomiczne o podaną wartość dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        data['economic_points'] = max(0, min(MAX_ECONOMIC_POINTS, data['economic_points'] + amount))
        return data['economic_points']

    def modify_supply_points(self, nation: str, amount: int) -> int:
        """Modyfikuje punkty zaopatrzenia o podaną wartość dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        data['supply_points'] = max(0, min(MAX_SUPPLY_POINTS, data['supply_points'] + amount))
        return data['supply_points']

    def reset_economy(self, nation: str) -> None:
        """Resetuje punkty ekonomiczne i zaopatrzenia do wartości początkowych dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        data['economic_points'] = 1000
        data['supply_points'] = 500

    def add_income(self, nation: str, amount: int) -> int:
        """Dodaje przychód (punkty ekonomiczne) dla danej nacji."""
        return self.modify_economic_points(nation, amount)

    def add_expense(self, nation: str, amount: int) -> int:
        """Odejmuje wydatek od punktów ekonomicznych danej nacji."""
        return self.modify_economic_points(nation, -amount)

    def produce_supply(self, nation: str, cost: int, amount: int) -> bool:
        """Konwertuje punkty ekonomiczne (koszt) na dodatkowe punkty zaopatrzenia dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        if data['economic_points'] >= cost:
            self.modify_economic_points(nation, -cost)
            self.modify_supply_points(nation, amount)
            return True
        return False

    def generate_report(self, nation: str) -> str:
        """Generuje tekstowy raport ekonomiczny dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        return (
            f"=== Raport Ekonomiczny: {nation} ===\n"
            f"Punkty ekonomiczne: {data['economic_points']}\n"
            f"Punkty zaopatrzenia: {data['supply_points']}\n"
        )

    def process_turn(self, nation: str, income: int, cost_per_unit: int = 0, unit_count: int = 0) -> None:
        """Przetwarza koniec tury dla danej nacji."""
        print(f"\n=== Przetwarzanie tury dla {nation} ===")
        self.add_income(nation, income)
        total_cost = cost_per_unit * unit_count
        self.add_expense(nation, total_cost)
        print(f"Koszt utrzymania {unit_count} jednostek: {total_cost}.")
        self.random_event(nation)
        print(self.generate_report(nation))

    def random_event(self, nation: str) -> None:
        """Losuje i stosuje losowe wydarzenie ekonomiczne dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        event_name, economic_change, supply_change = random.choice(ECONOMIC_EVENTS)
        print(f"\n=== Wydarzenie dla {nation}: {event_name} ===")
        self.modify_economic_points(nation, economic_change)
        self.modify_supply_points(nation, supply_change)

    def show_history(self, nation: str) -> None:
        """Wyświetla historię zdarzeń ekonomicznych dla danej nacji."""
        data = self.get_nation_data(nation)
        if not data:
            raise ValueError(f"Brak danych dla nacji: {nation}")
        print(f"\n=== Historia Ekonomii dla {nation} ===")
        for entry in data.get('history', []):
            print(entry)
