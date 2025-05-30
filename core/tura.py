class TurnManager:
    def __init__(self, players, game_engine=None):
        """
        Inicjalizuje menedżera tur.
        :param players: Lista obiektów klasy Player w ustalonej kolejności.
        :param game_engine: Instancja GameEngine przechowująca stan gry.
        """
        self.players = players
        self.current_turn = 1
        self.current_player_index = 0
        self.game_engine = game_engine

        # Inicjalizacja obiektu Pogoda jako atrybutu klasy
        from core.pogoda import Pogoda
        self.weather = Pogoda()
        self.weather.generuj_pogode()
        self.current_weather = self.weather.generuj_raport_pogodowy()

    def rozpocznij_nowa_ture(self):
        """Rozpoczyna nową turę i generuje pogodę raz na dzień."""

        if self.current_turn % 6 == 1:  # Generowanie pogody raz na dzień (co 6 tur)
            self.weather.generuj_pogode()

        # Inkrementacja tury
        self.current_turn += 1

    def next_turn(self):
        """
        Przechodzi do następnego gracza w kolejności.
        Zwraca True, jeśli wszyscy gracze zakończyli swoje tury.
        """
        self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            self.current_player_index = 0
            self.current_turn += 1

            # Reset punktów ruchu wszystkich żetonów na początku nowej tury
            if self.game_engine is not None and hasattr(self.game_engine, 'tokens'):
                for token in self.game_engine.tokens:
                    max_mp = getattr(token, 'maxMovePoints', token.stats.get('move', 0))
                    token.maxMovePoints = max_mp
                    token.currentMovePoints = max_mp

            if self.current_turn % 6 == 0:  # Co 6 tur generujemy nowy raport pogodowy
                self.weather.generuj_pogode()
                self.current_weather = self.weather.generuj_raport_pogodowy()

            return True  # Zakończono pełną turę

        return False

    def get_current_player(self):
        """
        Zwraca aktualnego gracza.
        :return: Obiekt klasy Player.
        """
        return self.players[self.current_player_index]

    def get_turn_info(self):
        """
        Zwraca informacje o aktualnej turze.
        :return: Słownik z informacjami o turze.
        """
        current_player = self.get_current_player()
        return {
            "turn": self.current_turn,
            "player": current_player.id,
            "nation": current_player.nation,
            "role": current_player.role,
        }

    def is_game_over(self, max_turns=10):
        """
        Sprawdza, czy gra powinna się zakończyć po osiągnięciu maksymalnej liczby tur.
        :param max_turns: Maksymalna liczba tur.
        :return: True, jeśli gra się zakończyła, False w przeciwnym razie.
        """
        return self.current_turn > max_turns