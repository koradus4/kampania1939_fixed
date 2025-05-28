import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from engine.engine import GameEngine
from engine.token import Token

MAP_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'map_data.json')
TOKENS_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tokens', 'index.json')
START_TOKENS_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'start_tokens.json')

@pytest.mark.usefixtures("tmp_path")
def test_save_and_load_state(tmp_path):
    # 1. Utwórz silnik, zmodyfikuj stan
    engine = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    assert len(engine.tokens) > 0
    token = engine.tokens[0]
    token.q = 42
    token.r = 24
    engine.turn = 7
    engine.current_player = 1
    # 2. Zapisz stan
    save_path = tmp_path / "state.json"
    engine.save_state(str(save_path))
    # 3. Utwórz nowy silnik, wczytaj stan
    engine2 = GameEngine(MAP_PATH, TOKENS_PATH, START_TOKENS_PATH)
    engine2.load_state(str(save_path))
    # 4. Sprawdź zgodność stanu
    assert engine2.turn == 7
    assert engine2.current_player == 1
    assert any(t.q == 42 and t.r == 24 for t in engine2.tokens)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
