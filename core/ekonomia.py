"""
Moduł systemu ekonomii – zarządza punktami ekonomicznymi i specjalnymi oraz wydarzeniami ekonomicznymi.
"""
import random

class EconomySystem:
    def __init__(self):
        """Inicjalizuje system ekonomii z domyślnymi wartościami."""
        self.economic_points = 0
        self.special_points = 0

    def generate_economic_points(self):
        """Generuje punkty ekonomiczne."""
        points = random.randint(1, 100)
        self.economic_points += points
        print(f"[DEBUG] +{points} punkty ekonomiczne")

    def add_special_points(self):
        """Dodaje 1 punkt specjalny."""
        self.special_points += 1
        print(f"[DEBUG] +1 punkt specjalny")

    def subtract_points(self, points):
        """Odejmuje punkty ekonomiczne z dostępnej puli."""
        if hasattr(self, 'economic_points'):
            self.economic_points -= points
            if self.economic_points < 0:
                self.economic_points = 0
        else:
            print("[ERROR] Obiekt EconomySystem nie ma atrybutu 'economic_points'.")

    def get_points(self):
        """Zwraca aktualne punkty ekonomiczne i specjalne."""
        return {"economic_points": self.economic_points, "special_points": self.special_points}

if __name__ == "__main__":
    economy = EconomySystem()

    print("[DEBUG] Symulacja 10 tur ekonomii")
    for turn in range(1, 11):
        print(f"\n=== Tura {turn} ===")
        economy.generate_economic_points()
        economy.add_special_points()
        points = economy.get_points()
        print(f"[DEBUG] {points['economic_points']} punkty ekonomiczne, {points['special_points']} punkty specjalne")
