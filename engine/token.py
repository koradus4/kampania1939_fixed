import json
from typing import Any, Dict, Optional

class Token:
    def __init__(self, id: str, owner: str, stats: Dict[str, Any], q: int = None, r: int = None):
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
            'currentFuel': getattr(self, 'currentFuel', getattr(self, 'maxFuel', self.stats.get('maintenance', 0)))
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
            'maintenance': data.get('maintenance', 0),
            'price': data.get('price', 0),
            'sight': data.get('sight', 0),
            'unitType': data.get('unitType', ''),
            'unitSize': data.get('unitSize', ''),
            'label': data.get('label', ''),
            'attack': data.get('attack', {}).get('value', 0),
            'image': data.get('image', ''),
            'shape': data.get('shape', ''),
            'w': data.get('w', 0),
            'h': data.get('h', 0),
            'nation': nation
        }
        token = Token(
            id=data['id'],
            owner=owner,
            stats=stats,
            q=q,
            r=r
        )
        # Odczytaj punkty ruchu i paliwa jeśli są w pliku
        token.maxMovePoints = data.get('maxMovePoints', stats.get('move', 0))
        token.currentMovePoints = data.get('currentMovePoints', token.maxMovePoints)
        token.maxFuel = data.get('maxFuel', stats.get('maintenance', 0))
        token.currentFuel = data.get('currentFuel', token.maxFuel)
        return token

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        # Pozwala odtworzyć Token z serialize()
        token = Token(
            id=data['id'],
            owner=data['owner'],
            stats=data['stats'],
            q=data.get('q'),
            r=data.get('r')
        )
        token.maxMovePoints = data.get('maxMovePoints', token.stats.get('move', 0))
        token.currentMovePoints = data.get('currentMovePoints', token.maxMovePoints)
        token.maxFuel = data.get('maxFuel', token.stats.get('maintenance', 0))
        token.currentFuel = data.get('currentFuel', token.maxFuel)
        return token


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
