import random
import os
import json
from engine.board import Board
from engine.token import load_tokens, Token

class GameEngine:
    def __init__(self, map_path: str, tokens_index_path: str, tokens_start_path: str, seed: int = 42):
        self.random = random.Random(seed)
        self.board = Board(map_path)
        state_path = os.path.join("saves", "latest.json")
        if os.path.exists(state_path):
            self.load_state(state_path)
        else:
            self.tokens = load_tokens(tokens_index_path, tokens_start_path)
            self.board.set_tokens(self.tokens)
            self.turn = 1
            self.current_player = 0
        # Możesz dodać listę graczy, pogodę, itp.

    def save_state(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        state = {
            "tokens": [t.serialize() for t in self.tokens],
            "turn": self.turn,
            "current_player": self.current_player
        }
        tmp_file = filepath + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, filepath)

    def load_state(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.tokens = [Token.from_dict(t) for t in state["tokens"]]
        self.board.set_tokens(self.tokens)
        self.turn = state["turn"]
        self.current_player = state["current_player"]

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
        self.save_state(os.path.join("saves", "latest.json"))

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
