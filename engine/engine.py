import random
from engine.board import Board
from engine.token import load_tokens
from engine.save_manager import save_state

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
        # Reset punktów ruchu dla wszystkich żetonów
        for token in self.tokens:
            max_mp = getattr(token, 'maxMovePoints', token.stats.get('move', 0))
            token.maxMovePoints = max_mp
            token.currentMovePoints = max_mp
        # Reset morale, pogoda itp. (jeśli dotyczy)

    def end_turn(self):
        self.next_turn()
        save_state(self, "saves/")

    def get_player_count(self):
        # Zaimplementuj zgodnie z logiką graczy
        return 2  # tymczasowo

    def get_state(self):
        """Zwraca uproszczony stan gry do GUI."""
        return {
            'turn': self.turn,
            'tokens': [t.serialize() for t in self.tokens]
        }

    def execute_action(self, action, player=None):
        """Rejestruje i wykonuje akcję (np. ruch, walka). Weryfikuje właściciela żetonu."""
        # Sprawdzenie właściciela żetonu
        token = next((t for t in self.tokens if t.id == getattr(action, 'token_id', None)), None)
        if player and token:
            expected_owner = f"{player.id} ({player.nation})"
            if token.owner != expected_owner:
                return False, "Ten żeton nie należy do twojego dowódcy."
        return action.execute(self)

    def get_visible_tokens(self, player):
        """Zwraca listę żetonów widocznych dla danego gracza (elastyczne filtrowanie)."""
        visible = []
        player_role = getattr(player, 'role', '').strip().lower()
        player_nation = getattr(player, 'nation', '').strip().lower()
        player_id = getattr(player, 'id', None)
        for token in self.tokens:
            token_nation = str(token.stats.get('nation', '')).strip().lower()
            token_owner = str(token.owner).strip()
            # 1. Mgła wojny i pole 'visible_for' (jeśli istnieje)
            if 'visible_for' in token.stats:
                if player_id in token.stats['visible_for']:
                    visible.append(token)
                    continue
            # 2. Generał widzi wszystkie żetony swojej nacji
            if player_role == 'generał' and token_nation == player_nation:
                visible.append(token)
            # 3. Dowódca widzi tylko swoje żetony
            elif player_role == 'dowódca' and token_owner == f"{player_id} ({player_nation.title()})":
                visible.append(token)
        return visible

# Przykład użycia:
# engine = GameEngine('data/map_data.json', 'data/tokens_index.json', 'data/start_tokens.json', seed=123)
# state = engine.get_state()
