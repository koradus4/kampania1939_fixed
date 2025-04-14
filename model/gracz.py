# Plik do dalszej implementacji

class Gracz:
    def __init__(self, numer, nacja, rola):
        """
        Inicjalizuje obiekt gracza.
        :param numer: Numer gracza (1-4).
        :param nacja: Wybrana nacja (np. "Polska" lub "Niemcy").
        :param rola: Rola gracza ("Generał" lub "Dowódca").
        """
        self.numer = numer
        self.nacja = nacja
        self.rola = rola

    def __str__(self):
        return f"Gracz {self.numer}: {self.nacja} - {self.rola}"
