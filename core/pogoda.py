import random

class Pogoda:
    def __init__(self):
        self.temperatura = None
        self.zachmurzenie = None
        self.opady = None
        self.poprzednia_temperatura = None  # Przechowuje temperaturę z poprzedniego dnia

    def generuj_pogode(self):
        """Generuje pogodę raz na dzień z ograniczeniem zmiany temperatury do 2 stopni."""
        min_temp = None
        max_temp = None

        if self.poprzednia_temperatura is None:
            self.temperatura = random.randint(-5, 25)  # Pierwszy dzień bez ograniczeń
        else:
            min_temp = max(-5, self.poprzednia_temperatura - 2)
            max_temp = min(25, self.poprzednia_temperatura + 2)
            self.temperatura = random.randint(min_temp, max_temp)

        # Zapisanie obecnej temperatury jako poprzedniej na przyszłość
        self.poprzednia_temperatura = self.temperatura

        # Generowanie zachmurzenia
        self.zachmurzenie = random.choice(["Bezchmurnie", "Zachmurzenie umiarkowane", "Duże zachmurzenie"])

        # Generowanie opadów z walidacją
        if self.zachmurzenie == "Bezchmurnie":
            self.opady = "Bezdeszczowo"
        elif self.zachmurzenie == "Zachmurzenie umiarkowane":
            self.opady = random.choice(["Bezdeszczowo", "Lekkie opady"])
        else:  # Duże zachmurzenie
            self.opady = random.choice(["Bezdeszczowo", "Lekkie opady", "Intensywne opady"])

        # Dodanie opadów śniegu, jeśli temperatura poniżej zera i nie jest bezdeszczowo
        if self.temperatura < 0 and self.opady != "Bezdeszczowo":
            self.opady += " (opady śniegu)"

    def wypisz_pogode(self):
        # Usunięto printy, funkcja nie wypisuje już nic do konsoli
        pass

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
        # Usunięto printy testowe
