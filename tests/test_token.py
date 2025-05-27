import pytest
from engine.token import Token

def test_token_to_dict_and_from_json():
    # Tworzymy przykładowy token
    stats = {
        'move': 5,
        'combat_value': 2,
        'maintenance': 1,
        'price': 10,
        'sight': 3,
        'unitType': 'P',
        'unitSize': 'Pluton',
        'label': 'Test',
        'attack': 1,
        'image': 'img.png',
        'shape': 'heks',
        'w': 240,
        'h': 240,
        'nation': 'Polska'
    }
    token = Token(id='P_Pluton__2_PL_P_Pluton', owner='2 (Polska)', stats=stats, q=1, r=2)
    d = token.serialize()
    # Test serializacji
    assert d['id'] == token.id
    assert d['owner'] == token.owner
    assert d['stats'] == token.stats
    assert d['q'] == 1 and d['r'] == 2
    # Test deserializacji
    token2 = Token.from_json(d, {'q': 1, 'r': 2})
    assert token2.id == token.id
    assert token2.owner == token.owner
    assert token2.stats['move'] == 5
    assert token2.q == 1 and token2.r == 2

def test_token_to_dict_and_from_dict():
    stats = {
        'move': 5,
        'combat_value': 2,
        'maintenance': 1,
        'price': 10,
        'sight': 3,
        'unitType': 'P',
        'unitSize': 'Pluton',
        'label': 'Test',
        'attack': 1,
        'image': 'img.png',
        'shape': 'heks',
        'w': 240,
        'h': 240,
        'nation': 'Polska'
    }
    token = Token(id='P_Pluton__2_PL_P_Pluton', owner='2 (Polska)', stats=stats, q=1, r=2)
    d = token.serialize()
    token2 = Token.from_dict(d)
    assert token2.id == token.id
    assert token2.owner == token.owner
    assert token2.stats == token.stats
    assert token2.q == 1 and token2.r == 2
