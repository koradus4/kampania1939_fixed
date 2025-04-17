"""
Moduł systemu ekonomii – zarządza punktami ekonomicznymi i specjalnymi oraz wydarzeniami ekonomicznymi.
"""
import random

class EconomySystem:
    def __init__(self):
        """Inicjalizuje system ekonomii z domyślnymi wartościami dla każdej nacji."""
        self.nations = {
            "Polska": {"economic_points": 0, "special_points": 0},
            "Niemcy": {"economic_points": 0, "special_points": 0}
        }

    def generate_points(self):
        """Generuje punkty ekonomiczne i specjalne dla generałów."""
        for nation, data in self.nations.items():
            economic_points = random.randint(1, 100)
            data["economic_points"] += economic_points
            data["special_points"] += 1
            print(f"[DEBUG] {nation}: +{economic_points} punkty ekonomiczne, +1 punkt specjalny")

    def get_points(self, nation):
        """Zwraca aktualne punkty ekonomiczne i specjalne dla danej nacji."""
        return self.nations.get(nation, {"economic_points": 0, "special_points": 0})

if __name__ == "__main__":
    economy = EconomySystem()

    print("[DEBUG] Symulacja 10 tur ekonomii")
    for turn in range(1, 11):
        print(f"\n=== Tura {turn} ===")
        economy.generate_points()
        for nation in economy.nations:
            points = economy.get_points(nation)
            print(f"[DEBUG] {nation}: {points['economic_points']} punkty ekonomiczne, {points['special_points']} punkty specjalne")
