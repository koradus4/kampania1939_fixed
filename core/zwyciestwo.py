# Plik do dalszej implementacji

class VictoryConditions:
    def __init__(self, max_turns=10):
        """
        Inicjalizuje warunki zwycięstwa.
        :param max_turns: Maksymalna liczba tur, po której gra się kończy.
        """
        self.max_turns = max_turns

    def check_game_over(self, current_turn):
        """
        Sprawdza, czy gra się zakończyła.
        :param current_turn: Aktualny numer tury.
        :return: True, jeśli gra się zakończyła, False w przeciwnym razie.
        """
        return current_turn >= self.max_turns

    def get_victory_message(self):
        """
        Zwraca wiadomość o zakończeniu gry.
        :return: Komunikat o zakończeniu gry.
        """
        return "Gra zakończona! Osiągnięto maksymalną liczbę tur."
