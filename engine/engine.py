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

def get_token_vision_hexes(token, board):
    """
    Zwraca zbiór (q, r) heksów w zasięgu widzenia żetonu na podstawie pola 'sight'.
    Używa dystansu heksagonalnego (axial/cube).
    """
    if token.q is None or token.r is None:
        return set()
    vision_range = token.stats.get('sight', 0)
    visible = set()
    for dq in range(-vision_range, vision_range + 1):
        for dr in range(-vision_range, vision_range + 1):
            q = token.q + dq
            r = token.r + dr
            if board.hex_distance((token.q, token.r), (q, r)) <= vision_range:
                if board.get_tile(q, r) is not None:
                    visible.add((q, r))
    return visible

def update_player_visibility(player, all_tokens, board):
    """
    Aktualizuje widoczność gracza: zbiera wszystkie heksy w zasięgu widzenia jego żetonów
    oraz żetony znajdujące się na tych heksach. Uwzględnia tymczasową widoczność (temp_visible_hexes, temp_visible_tokens).
    """
    visible_hexes = set()
    # Dowódca: tylko własne żetony; Generał: sumuje widoczność dowódców swojej nacji
    if player.role.lower() == 'dowódca':
        own_tokens = [t for t in all_tokens if t.owner == f"{player.id} ({player.nation})"]
    elif player.role.lower() == 'generał':
        own_tokens = [t for t in all_tokens if t.owner.endswith(f"({player.nation})")]
    else:
        own_tokens = []
    for token in own_tokens:
        visible_hexes |= get_token_vision_hexes(token, board)
    # Dodaj tymczasową widoczność
    if hasattr(player, 'temp_visible_hexes'):
        visible_hexes |= player.temp_visible_hexes
    player.visible_hexes = visible_hexes
    # Zbierz żetony widoczne na tych heksach
    visible_tokens = set()
    for t in all_tokens:
        if (t.q, t.r) in visible_hexes:
            visible_tokens.add(t.id)
    # Dodaj tymczasowo widoczne żetony
    if hasattr(player, 'temp_visible_tokens'):
        visible_tokens |= player.temp_visible_tokens
    player.visible_tokens = visible_tokens

def update_general_visibility(general, all_players, all_tokens):
    """
    Generał widzi WSZYSTKIE żetony swojej nacji (niezależnie od dowódcy) oraz WSZYSTKIE żetony przeciwnika, które są na heksach widocznych przez jego dowódców.
    """
    nation = general.nation
    dowodcy = [p for p in all_players if p.role.lower() == 'dowódca' and p.nation == nation]
    all_hexes = set()
    for d in dowodcy:
        all_hexes |= getattr(d, 'visible_hexes', set())
    general.visible_hexes = all_hexes
    # Generał widzi wszystkie żetony swojej nacji
    own_tokens = {t.id for t in all_tokens if t.owner.endswith(f"({nation})")}
    # Oraz wszystkie żetony przeciwnika, które są na widocznych heksach
    enemy_tokens = {t.id for t in all_tokens if t.owner and not t.owner.endswith(f"({nation})") and (t.q, t.r) in all_hexes}
    general.visible_tokens = own_tokens | enemy_tokens

def update_all_players_visibility(players, all_tokens, board):
    for player in players:
        update_player_visibility(player, all_tokens, board)
    # Dodatkowa aktualizacja dla generałów (po wszystkich dowódcach!)
    for player in players:
        if player.role.lower() == 'generał':
            update_general_visibility(player, players, all_tokens)

def clear_temp_visibility(players):
    for p in players:
        if hasattr(p, 'temp_visible_hexes'):
            p.temp_visible_hexes.clear()
        if hasattr(p, 'temp_visible_tokens'):
            p.temp_visible_tokens.clear()

# Przykład użycia:
# engine = GameEngine('data/map_data.json', 'data/tokens_index.json', 'data/start_tokens.json', seed=123)
# state = engine.get_state()
