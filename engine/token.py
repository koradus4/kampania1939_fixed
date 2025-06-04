import json
from typing import Any, Dict, Optional

class Token:
    def __init__(self, id: str, owner: str, stats: Dict[str, Any], q: int = None, r: int = None, movement_mode: str = 'combat'):
        self.id = id
        self.owner = owner
        self.stats = stats  # np. {'move': 12, 'combat_value': 6, ...}
        self.q = q
        self.r = r
        # Inicjalizacja punktów ruchu
        self.maxMovePoints = getattr(self, 'maxMovePoints', stats.get('move', 0))
        self.currentMovePoints = getattr(self, 'currentMovePoints', self.maxMovePoints)
        # --- PALIWO ---
        self.maxFuel = stats.get('maintenance', 0)
        self.currentFuel = getattr(self, 'currentFuel', self.maxFuel)
        # --- ZASOBY BOJOWE ---
        self.combat_value = getattr(self, 'combat_value', stats.get('combat_value', 0))
        # --- TRYB RUCHU ---
        self.movement_mode = getattr(self, 'movement_mode', movement_mode)
        self.movement_mode_locked = False  # Blokada zmiany trybu ruchu do końca tury

    def can_move_to(self, dist: int) -> bool:
        """Sprawdza, czy żeton może się ruszyć na daną odległość (uwzględnia limit ruchu i paliwa)."""
        return dist <= self.stats.get('move', 0) and self.currentFuel > 0

    def set_position(self, q: int, r: int):
        self.q = q
        self.r = r

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'owner': self.owner,
            'stats': self.stats,
            'q': self.q,
            'r': self.r,
            'maxMovePoints': getattr(self, 'maxMovePoints', self.stats.get('move', 0)),
            'currentMovePoints': getattr(self, 'currentMovePoints', getattr(self, 'maxMovePoints', self.stats.get('move', 0))),
            'maxFuel': getattr(self, 'maxFuel', self.stats.get('maintenance', 0)),
            'currentFuel': getattr(self, 'currentFuel', getattr(self, 'maxFuel', self.stats.get('maintenance', 0))),
            'movement_mode': getattr(self, 'movement_mode', 'combat'),
            'movement_mode_locked': getattr(self, 'movement_mode_locked', False),
            'combat_value': getattr(self, 'combat_value', self.stats.get('combat_value', 0)),
        }

    @staticmethod
    def from_json(data: Dict[str, Any], pos: Optional[Dict[str, int]] = None):
        q = pos['q'] if pos else None
        r = pos['r'] if pos else None
        # Ustalanie nacji
        nation = data.get('nation', '')
        if not nation:
            if '_PL_' in data['id']:
                nation = 'Polska'
            elif '_N_' in data['id']:
                nation = 'Niemcy'
            else:
                nation = ''
        # Ustalanie ownera
        owner = data.get('owner', '')
        player_id = ''
        if pos and 'id' in pos:
            # Wyciągnięcie player_id z id żetonu, np. AC_Pluton__2_PL_AC_Pluton
            parts = data['id'].split('__')
            if len(parts) > 1:
                player_id = parts[1].split('_')[0]
        if not owner:
            owner = f"{player_id} ({nation})" if player_id and nation else player_id or nation
        stats = {
            'move': data.get('move', 0),
            'combat_value': data.get('combat_value', 0),
            'defense_value': data.get('defense_value', 0),
            'maintenance': data.get('maintenance', 0),
            'price': data.get('price', 0),
            'sight': data.get('sight', 0),
            'unitType': data.get('unitType', ''),
            'unitSize': data.get('unitSize', ''),
            'label': data.get('label', ''),
            'unit_full_name': data.get('unit_full_name', ''),  # NOWE POLE
            'attack': data.get('attack', 0),  # <-- poprawka: zachowaj dict jeśli jest
            'image': data.get('image', ''),
            'shape': data.get('shape', ''),
            'w': data.get('w', 0),
            'h': data.get('h', 0),
            'nation': nation
        }
        movement_mode = data.get('movement_mode', 'combat')
        token = Token(
            id=data['id'],
            owner=owner,
            stats=stats,
            q=q,
            r=r,
            movement_mode=movement_mode
        )
        # Odczytaj punkty ruchu i paliwa jeśli są w pliku
        token.maxMovePoints = data.get('maxMovePoints', stats.get('move', 0))
        token.currentMovePoints = data.get('currentMovePoints', token.maxMovePoints)
        token.maxFuel = data.get('maxFuel', stats.get('maintenance', 0))
        token.currentFuel = data.get('currentFuel', token.maxFuel)
        token.movement_mode = data.get('movement_mode', 'combat')
        return token

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        # Pozwala odtworzyć Token z serialize()
        token = Token(
            id=data['id'],
            owner=data['owner'],
            stats=data['stats'],
            q=data.get('q'),
            r=data.get('r'),
            movement_mode=data.get('movement_mode', 'combat')
        )
        token.maxMovePoints = data.get('maxMovePoints', token.stats.get('move', 0))
        token.currentMovePoints = data.get('currentMovePoints', token.maxMovePoints)
        token.maxFuel = data.get('maxFuel', token.stats.get('maintenance', 0))
        token.currentFuel = data.get('currentFuel', token.maxFuel)
        token.movement_mode = data.get('movement_mode', 'combat')
        token.movement_mode_locked = data.get('movement_mode_locked', False)
        print(f"[DEBUG][from_dict] {token.id} movement_mode_locked={token.movement_mode_locked}")
        token.combat_value = data.get('combat_value', token.stats.get('combat_value', 0))
        return token

    def apply_movement_mode(self, reset_mp: bool = False):
        base_move = self.stats.get('move', 0)
        base_def = self.stats.get('defense_value', 0)
        # Ustal mnożniki
        if self.movement_mode == 'combat':
            move_mult = 1.0
            def_mult = 1.0
        elif self.movement_mode == 'march':
            move_mult = 1.5
            def_mult = 0.5
        elif self.movement_mode == 'recon':
            move_mult = 0.5
            def_mult = 1.25
        else:
            move_mult = 1.0
            def_mult = 1.0
        move = base_move * move_mult
        defense = base_def * def_mult
        prev_max = getattr(self, 'maxMovePoints', base_move)
        prev_current = getattr(self, 'currentMovePoints', prev_max)
        self.maxMovePoints = int(round(move))
        self.defense_value = int(round(defense))
        self.base_move = base_move
        self.base_defense = base_def
        if reset_mp:
            self.currentMovePoints = self.maxMovePoints
        else:
            # Zachowaj liczbę zużytych punktów ruchu (nowy max - zużyte)
            used = prev_max - prev_current
            self.currentMovePoints = max(0, min(self.maxMovePoints, self.maxMovePoints - used))


def load_tokens(index_path: str, start_path: str):
    """Ładuje żetony z plików JSON (index + start) i zwraca listę obiektów Token."""
    with open(index_path, encoding='utf-8') as f:
        index_data = json.load(f)
    with open(start_path, encoding='utf-8') as f:
        start_data = json.load(f)

    # Tworzymy mapę id -> dane żetonu
    index_map = {item['id']: item for item in index_data if 'id' in item}
    tokens = []
    for pos in start_data:
        token_id = pos['id']
        if token_id in index_map:
            tokens.append(Token.from_json(index_map[token_id], pos))
    return tokens
