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
        print(f"[DEBUG] Wygenerowano {points} punktów ekonomicznych. Aktualna suma: {self.economic_points}")

    def add_special_points(self):
        """Dodaje 1 punkt specjalny."""
        self.special_points += 1
        print(f"[DEBUG] Dodano 1 punkt specjalny. Aktualna suma: {self.special_points}")

    def subtract_points(self, points):
        """Odejmuje punkty ekonomiczne z dostępnej puli."""
        if hasattr(self, 'economic_points'):
            self.economic_points -= points
            if self.economic_points < 0:
                self.economic_points = 0
            print(f"[DEBUG] Odjęto {points} punktów ekonomicznych. Aktualna suma: {self.economic_points}")
        else:
            print("[ERROR] Obiekt EconomySystem nie ma atrybutu 'economic_points'.")

    def get_points(self):
        """Zwraca aktualne punkty ekonomiczne i specjalne."""
        return {"economic_points": self.economic_points, "special_points": self.special_points}

    def get_assigned_points(self):
        """Zwraca liczbę punktów przydzielonych dowódcom."""
        # Na potrzeby demonstracji zwracamy stałą wartość, np. 1 punkt na dowódcę
        return 1

if __name__ == "__main__":
    economy = EconomySystem()

    print("Symulacja 10 tur ekonomii")
    for turn in range(1, 11):
        print(f"\n=== Tura {turn} ===")
        economy.generate_economic_points()
        economy.add_special_points()
        points = economy.get_points()
        print(f"{points['economic_points']} punkty ekonomiczne, {points['special_points']} punkty specjalne")
