class TurnManager:
    def __init__(self, players):
        """
        Inicjalizuje menedżera tur.
        :param players: Lista obiektów klasy Gracz w ustalonej kolejności.
        """
        self.players = players
        self.current_turn = 1
        self.current_player_index = 0

        # Inicjalizacja raportu pogodowego na początku gry
        from core.pogoda import Pogoda
        pogoda = Pogoda()
        pogoda.generuj_pogode()
        self.current_weather = pogoda.generuj_raport_pogodowy()

    def next_turn(self):
        """
        Przechodzi do następnego gracza w kolejności.
        Zwraca True, jeśli wszyscy gracze zakończyli swoje tury.
        """
        self.current_player_index += 1
        print(f"[DEBUG] Przechodzenie do następnego gracza. Index: {self.current_player_index}")

        if self.current_player_index >= len(self.players):
            self.current_player_index = 0
            self.current_turn += 1
            print(f"[DEBUG] Rozpoczęcie nowej tury: {self.current_turn}")

            if self.current_turn % 6 == 0:  # Co 6 tur generujemy nowy raport pogodowy
                from core.pogoda import Pogoda
                pogoda = Pogoda()
                pogoda.generuj_pogode()
                self.current_weather = pogoda.generuj_raport_pogodowy()
                print(f"[DEBUG] Nowy raport pogodowy: {self.current_weather}")

            return True  # Zakończono pełną turę

        return False

    def get_current_player(self):
        """
        Zwraca aktualnego gracza.
        :return: Obiekt klasy Gracz.
        """
        current_player = self.players[self.current_player_index]
        print(f"[DEBUG] Aktualny gracz: {current_player}")
        print(f"[DEBUG] Numer tury: {self.current_turn}")
        print(f"[DEBUG] Raport pogodowy: {self.current_weather}")
        return current_player

    def get_turn_info(self):
        """
        Zwraca informacje o aktualnej turze.
        :return: Słownik z informacjami o turze.
        """
        current_player = self.get_current_player()
        return {
            "turn": self.current_turn,
            "player": current_player.numer,
            "nation": current_player.nacja,
            "role": current_player.rola,
        }

    def is_game_over(self, max_turns=10):
        """
        Sprawdza, czy gra powinna się zakończyć po osiągnięciu maksymalnej liczby tur.
        :param max_turns: Maksymalna liczba tur.
        :return: True, jeśli gra się zakończyła, False w przeciwnym razie.
        """
        return self.current_turn > max_turns