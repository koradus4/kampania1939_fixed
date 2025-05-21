import json
from typing import Any, Dict, Optional

class Token:
    def __init__(self, id: str, owner: str, stats: Dict[str, Any], q: int = None, r: int = None):
        self.id = id
        self.owner = owner
        self.stats = stats  # np. {'move': 12, 'combat_value': 6, ...}
        self.q = q
        self.r = r

    def can_move_to(self, dist: int) -> bool:
        """Sprawdza, czy żeton może się ruszyć na daną odległość (uwzględnia limit ruchu)."""
        return dist <= self.stats.get('move', 0)

    def set_position(self, q: int, r: int):
        self.q = q
        self.r = r

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'owner': self.owner,
            'stats': self.stats,
            'q': self.q,
            'r': self.r
        }

    @staticmethod
    def from_json(data: Dict[str, Any], pos: Optional[Dict[str, int]] = None):
        q = pos['q'] if pos else None
        r = pos['r'] if pos else None
        return Token(
            id=data['id'],
            owner=data.get('owner', ''),
            stats={
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
                'h': data.get('h', 0)
            },
            q=q,
            r=r
        )


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
