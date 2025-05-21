import random
from engine.board import Board
from engine.token import load_tokens

class GameEngine:
    def __init__(self, map_path: str, tokens_index_path: str, tokens_start_path: str, seed: int = 42):
        self.random = random.Random(seed)
        self.board = Board(map_path)
        self.tokens = load_tokens(tokens_index_path, tokens_start_path)
        self.board.set_tokens(self.tokens)
        self.turn = 1
        self.current_player = 0
        # Możesz dodać listę graczy, pogodę, itp.

    def next_turn(self):
        self.turn += 1
        self.current_player = (self.current_player + 1) % self.get_player_count()
        # Reset ruchów, morale, pogoda itp.

    def get_player_count(self):
        # Zaimplementuj zgodnie z logiką graczy
        return 2  # tymczasowo

    def get_state(self):
        """Zwraca uproszczony stan gry do GUI."""
        return {
            'turn': self.turn,
            'tokens': [t.serialize() for t in self.tokens]
        }

    def execute_action(self, action):
        """Rejestruje i wykonuje akcję (np. ruch, walka)."""
        return action.execute(self)

# Przykład użycia:
# engine = GameEngine('data/map_data.json', 'data/tokens_index.json', 'data/start_tokens.json', seed=123)
# state = engine.get_state()
