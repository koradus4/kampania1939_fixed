# Plik do dalszej implementacji

from core.ekonomia import EconomySystem

class Gracz:
    def __init__(self, numer, nacja, rola, czas=5):
        """
        Inicjalizuje obiekt gracza.
        :param numer: Numer gracza (1-6).
        :param nacja: Wybrana nacja (np. "Polska" lub "Niemcy").
        :param rola: Rola gracza ("Generał" lub "Dowódca").
        :param czas: Czas na podturę w minutach (domyślnie 5 minut).
        """
        self.numer = numer
        self.nacja = nacja
        self.rola = rola
        self.czas = czas  # Czas na podturę
        self.economy = EconomySystem()  # Indywidualny system ekonomii dla gracza

        # Dodanie debugowania w terminalu, aby śledzić ustawienie czasu na podturę
        print(f"[DEBUG] Inicjalizacja gracza {numer}: nacja={nacja}, rola={rola}, czas={czas} minut")

    def __str__(self):
        return f"Gracz {self.numer}: {self.nacja} - {self.rola} - {self.czas} minut"
