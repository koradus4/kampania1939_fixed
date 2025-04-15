import random

class Pogoda:
    def __init__(self):
        self.temperatura = None
        self.zachmurzenie = None
        self.opady = None
        self.poprzednia_temperatura = None  # Przechowuje temperaturę z poprzedniego dnia

    def generuj_pogode(self):
        # Generowanie temperatury z ograniczeniem różnicy do 5 stopni
        if self.poprzednia_temperatura is None:
            self.temperatura = random.randint(-5, 25)  # Pierwszy dzień bez ograniczeń
        else:
            min_temp = max(-5, self.poprzednia_temperatura - 5)
            max_temp = min(25, self.poprzednia_temperatura + 5)
            self.temperatura = random.randint(min_temp, max_temp)

        # Zapisanie obecnej temperatury jako poprzedniej na przyszłość
        self.poprzednia_temperatura = self.temperatura

        # Generowanie zachmurzenia
        self.zachmurzenie = random.choice(["Bezchmurnie", "Zachmurzenie umiarkowane", "Duże zachmurzenie"])

        # Generowanie opadów z walidacją
        if self.zachmurzenie in ["Bezchmurnie", "Zachmurzenie umiarkowane"]:
            self.opady = random.choice(["Bezdeszczowo", "Lekkie opady"])
        else:
            self.opady = random.choice(["Bezdeszczowo", "Lekkie opady", "Intensywne opady"])

        # Dodanie opadów śniegu, jeśli temperatura poniżej zera i nie jest bezdeszczowo
        if self.temperatura < 0 and self.opady != "Bezdeszczowo":
            self.opady += " (opady śniegu)"

    def wypisz_pogode(self):
        print("=== Pogoda na dziś ===")
        print(f"Temperatura: {self.temperatura}°C")
        print(f"Zachmurzenie: {self.zachmurzenie}")
        print(f"Opady: {self.opady}")

    def generuj_raport_pogodowy(self):
        """Generuje raport pogodowy w formacie tekstowym."""
        return (
            f"=== Pogoda ===\n"
            f"Temperatura: {self.temperatura}°C\n"
            f"Zachmurzenie: {self.zachmurzenie}\n"
            f"Opady: {self.opady}\n"
        )

if __name__ == "__main__":
    pogoda = Pogoda()
    for _ in range(7):  # Generowanie pogody na 7 dni
        pogoda.generuj_pogode()
        pogoda.wypisz_pogode()
        print()
