# Plik do dalszej implementacji

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

        # Przypisanie ścieżki do obrazu w zależności od nacji i roli
        base_path = "c:/Users/klif/kampania1939_fixed/gui/images/"
        if self.nacja == "Polska" and self.rola == "Generał":
            self.image_path = base_path + "Marszałek Polski Edward Rydz-Śmigły.png"
        elif self.nacja == "Niemcy" and self.rola == "Generał":
            self.image_path = base_path + "Generał pułkownik Walther von Brauchitsch.png"
        elif self.nacja == "Polska" and self.rola == "Dowódca":
            if self.numer == 2:  # Dowódca 2 Polska
                self.image_path = base_path + "Generał Juliusz Rómmel.png"
            else:  # Dowódca 1 Polska
                self.image_path = base_path + "Generał Tadeusz Kutrzeba.png"
        elif self.nacja == "Niemcy" and self.rola == "Dowódca":
            if self.numer == 6:  # Dowódca 2 Niemcy
                self.image_path = base_path + "Generał Walther von Reichenau.png"
            else:  # Dowódca 1 Niemcy
                self.image_path = base_path + "Generał Fedor von Bock.png"
        else:
            self.image_path = base_path + "default.png"  # Domyślny obraz, jeśli nie pasuje żadna rola/nacja

        # Przypisanie ścieżki do mapy w zależności od nacji i roli
        if self.nacja == "Polska" and self.rola == "Generał":
            self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_globalna.jpg"
        elif self.nacja == "Niemcy" and self.rola == "Generał":
            self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_globalna.jpg"
        elif self.nacja == "Polska" and self.rola == "Dowódca":
            if self.numer == 2:  # Dowódca 2 Polska
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca2.jpg"
            else:  # Dowódca 1 Polska
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca1.jpg"
        elif self.nacja == "Niemcy" and self.rola == "Dowódca":
            if self.numer == 6:  # Dowódca 2 Niemcy
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca2.jpg"
            else:  # Dowódca 1 Niemcy
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca1.jpg"
        else:
            self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_hex.jpg"  # Domyślna mapa, jeśli nie pasuje żadna rola/nacja

        # Przypisanie nazwy gracza w zależności od nacji i roli
        if self.nacja == "Polska" and self.rola == "Generał":
            self.name = "Marszałek Polski Edward Rydz-Śmigły"
        elif self.nacja == "Niemcy" and self.rola == "Generał":
            self.name = "Generał pułkownik Walther von Brauchitsch"
        elif self.nacja == "Polska" and self.rola == "Dowódca":
            if self.numer == 2:  # Dowódca 2 Polska
                self.name = "Generał Juliusz Rómmel"
            else:  # Dowódca 1 Polska
                self.name = "Generał Tadeusz Kutrzeba"
        elif self.nacja == "Niemcy" and self.rola == "Dowódca":
            if self.numer == 6:  # Dowódca 2 Niemcy
                self.name = "Generał Walther von Reichenau"
            else:  # Dowódca 1 Niemcy
                self.name = "Generał Fedor von Bock"
        else:
            self.name = "Nieznany Gracz"  # Domyślna nazwa, jeśli nie pasuje żadna rola/nacja

    def __str__(self):
        return f"Gracz {self.numer}: {self.nacja} - {self.rola} - {self.czas} minut"
