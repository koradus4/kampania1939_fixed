import os
import json
from engine.token import Token

def save_state(engine, path):
    """Zapisuje stan gry do pliku JSON (snapshot)."""
    state = {
        'turn_number': getattr(engine, 'turn_number', 0),
        'current_player': getattr(engine, 'current_player', None),
        'tokens': [t.serialize() for t in engine.tokens],
        'map': getattr(engine.board, 'terrain', {}),
        'logs': getattr(engine, 'logs', [])
    }
    os.makedirs(path, exist_ok=True)
    tmp_file = os.path.join(path, 'latest.json.tmp')
    final_file = os.path.join(path, 'latest.json')
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, final_file)

def load_state(path):
    """Wczytuje stan gry z pliku JSON (snapshot). Zwraca dict z danymi."""
    with open(path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    # Proste asserty bezpieczeństwa
    assert 'tokens' in state and isinstance(state['tokens'], list)
    assert 0 <= state['turn_number'] < 1000
    return state
