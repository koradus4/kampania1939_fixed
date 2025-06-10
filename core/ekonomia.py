"""
Moduł systemu ekonomii – zarządza punktami ekonomicznymi i specjalnymi oraz wydarzeniami ekonomicznymi.
"""
import random

class EconomySystem:
    def __init__(self):
        """Inicjalizuje system ekonomii z domyślnymi wartościami."""
        self.economic_points = 0
        self.special_points = 0
        self.assigned_points = 0  # Dodano pole do przechowywania przydzielonych punktów

    def generate_economic_points(self):
        """Generuje punkty ekonomiczne."""
        start_points = self.economic_points
        points = random.randint(1, 100)
        self.economic_points += points
        print(f"[EKONOMIA][GENERAŁ] Losowe punkty ekonomiczne: +{points} (przed: {start_points}, po: {self.economic_points})")

    def add_special_points(self):
        """Dodaje 1 punkt specjalny."""
        self.special_points += 1

    def subtract_points(self, points):
        """Odejmuje punkty ekonomiczne z dostępnej puli."""
        if hasattr(self, 'economic_points'):
            self.economic_points -= points
            if self.economic_points < 0:
                self.economic_points = 0

    def get_points(self):
        """Zwraca aktualne punkty ekonomiczne i specjalne."""
        return {"economic_points": self.economic_points, "special_points": self.special_points}

    def get_assigned_points(self):
        """Zwraca liczbę punktów przydzielonych dowódcom."""
        return self.assigned_points

    def add_economic_points(self, points):
        """Dodaje punkty ekonomiczne (np. z punktów kluczowych)."""
        self.economic_points += points

if __name__ == "__main__":
    economy = EconomySystem()
