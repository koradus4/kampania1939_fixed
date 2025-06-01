import pytest
import json
from engine.token import Token
from engine.action import MoveAction
from engine.engine import GameEngine
import os

@pytest.fixture
def real_tokens():
    with open('assets/tokens/index.json', encoding='utf-8') as f:
        index_data = json.load(f)
    with open('assets/start_tokens.json', encoding='utf-8') as f:
        start_data = json.load(f)
    # Użyj pierwszego żetonu z mapy
    token_data = index_data[0]
    pos_data = start_data[0]
    token = Token.from_json(token_data, pos_data)
    return token

@pytest.fixture
def all_real_tokens():
    with open('assets/tokens/index.json', encoding='utf-8') as f:
        index_data = json.load(f)
    with open('assets/start_tokens.json', encoding='utf-8') as f:
        start_data = json.load(f)
    tokens = []
    for pos_data in start_data:
        token_data = next((item for item in index_data if item['id'] == pos_data['id']), None)
        if token_data:
            tokens.append(Token.from_json(token_data, pos_data))
    return tokens

def test_default_movement_mode(real_tokens):
    token = real_tokens
    assert hasattr(token, 'movement_mode')
    assert token.movement_mode == 'combat'

def test_mode_switch_cycle(real_tokens):
    token = real_tokens
    # combat -> march -> recon -> combat
    for mode in ['combat', 'march', 'recon', 'combat']:
        assert token.movement_mode == mode
        # symulacja zmiany trybu
        if token.movement_mode == 'combat':
            token.movement_mode = 'march'
        elif token.movement_mode == 'march':
            token.movement_mode = 'recon'
        else:
            token.movement_mode = 'combat'

def test_movement_and_defense_multiplier(real_tokens):
    token = real_tokens
    base_mp = token.stats.get('move', 0)
    # combat
    token.movement_mode = 'combat'
    assert int(base_mp * 1.0) == int(getattr(token, 'maxMovePoints', base_mp) * 1.0)
    # march
    token.movement_mode = 'march'
    assert int(base_mp * 1.5) == int(base_mp * 1.5)
    # recon
    token.movement_mode = 'recon'
    assert int(base_mp * 2.0) == int(base_mp * 2.0)

def test_all_tokens_have_movement_mode(all_real_tokens):
    for token in all_real_tokens:
        assert hasattr(token, 'movement_mode')
        assert token.movement_mode in ['combat', 'march', 'recon'] or token.movement_mode == 'combat'

def test_serialize_deserialize_cycle(real_tokens):
    token = real_tokens
    data = token.serialize()
    token2 = Token.from_dict(data)
    assert token2.id == token.id
    assert token2.movement_mode == token.movement_mode
    assert token2.stats == token.stats

def test_switch_and_serialize(all_real_tokens):
    for token in all_real_tokens:
        orig_mode = token.movement_mode
        # Zmień tryb i serializuj
        for mode in ['combat', 'march', 'recon']:
            token.movement_mode = mode
            data = token.serialize()
            token2 = Token.from_dict(data)
            assert token2.movement_mode == mode
        token.movement_mode = orig_mode

# Test integracyjny z ruchem na mapie (jeśli plik mapy istnieje)
def test_move_action_with_modes(real_tokens):
    if not os.path.exists('data/map_data.json'):
        pytest.skip('Brak mapy testowej')
    engine = GameEngine(
        map_path='data/map_data.json',
        tokens_index_path='assets/tokens/index.json',
        tokens_start_path='assets/start_tokens.json',
        seed=42
    )
    token = engine.tokens[0]
    start_q, start_r = token.q, token.r
    for mode, mult in [('combat', 1.0), ('march', 1.5), ('recon', 2.0)]:
        token.movement_mode = mode
        token.currentMovePoints = int(token.maxMovePoints * mult)
        neighbors = engine.board.neighbors(start_q, start_r)
        dest = None
        for n in neighbors:
            tile = engine.board.get_tile(*n)
            if tile and tile.move_mod >= 0 and not engine.board.is_occupied(*n):
                dest = n
                break
        if dest is None:
            continue
        move_action = MoveAction(token.id, dest[0], dest[1])
        result, msg = engine.execute_action(move_action)
        assert result, f'Ruch nie powiódł się: {msg}!'
        assert token.q == dest[0] and token.r == dest[1], 'Żeton nie przesunął się na nowe pole!'
