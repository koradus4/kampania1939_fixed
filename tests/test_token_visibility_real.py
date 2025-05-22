import pytest
import json
from engine.engine import GameEngine
from engine.player import Player
from engine.token import Token
from pathlib import Path

def load_real_tokens(nation_folder):
    tokens = []
    for token_json in Path(nation_folder).rglob('token.json'):
        with open(token_json, encoding='utf-8') as f:
            data = json.load(f)
        # uproszczony Token (nie wymaga pozycji)
        t = Token(
            id=data['id'],
            owner=data.get('owner', ''),
            stats=data,
            q=0, r=0
        )
        tokens.append(t)
    return tokens

@pytest.fixture(scope="module")
def real_engine():
    engine = GameEngine.__new__(GameEngine)
    # Załaduj żetony polskie i niemieckie
    tokens = load_real_tokens('assets/tokens/Polska') + load_real_tokens('assets/tokens/Niemcy')
    engine.tokens = tokens
    return engine

def test_real_visible_tokens_for_polish_general(real_engine):
    player = Player(1, 'Polska', 'Generał')
    visible = real_engine.get_visible_tokens(player)
    for t in visible:
        assert t.stats['nation'] == 'Polska'
    # Sprawdź, że są żetony różnych ownerów
    owners = {t.owner for t in visible}
    assert '2 (Polska)' in owners and '3 (Polska)' in owners

def test_real_visible_tokens_for_polish_commander_2(real_engine):
    player = Player(2, 'Polska', 'Dowódca')
    visible = real_engine.get_visible_tokens(player)
    for t in visible:
        assert t.owner == '2 (Polska)'
    # Sprawdź, że są żetony
    assert len(visible) > 0

def test_real_visible_tokens_for_german_general(real_engine):
    player = Player(5, 'Niemcy', 'Generał')
    visible = real_engine.get_visible_tokens(player)
    for t in visible:
        assert t.stats['nation'] == 'Niemcy'
    owners = {t.owner for t in visible}
    assert '5 (Niemcy)' in owners and '6 (Niemcy)' in owners

def test_real_visible_tokens_for_german_commander_6(real_engine):
    player = Player(6, 'Niemcy', 'Dowódca')
    visible = real_engine.get_visible_tokens(player)
    for t in visible:
        assert t.owner == '6 (Niemcy)'
    assert len(visible) > 0
