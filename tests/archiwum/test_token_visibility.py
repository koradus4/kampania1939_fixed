import pytest
from engine.engine import GameEngine
from engine.player import Player
from engine.token import Token

class DummyToken:
    def __init__(self, id, owner, nation, visible_for=None):
        self.id = id
        self.owner = owner
        self.stats = {'nation': nation}
        if visible_for is not None:
            self.stats['visible_for'] = visible_for
        self.q = 0
        self.r = 0

@pytest.fixture
def sample_engine():
    engine = GameEngine.__new__(GameEngine)  # nie wywołuj __init__
    # Dodaj przykładowe żetony
    engine.tokens = [
        DummyToken('t1', '2 (Polska)', 'Polska'),
        DummyToken('t2', '3 (Polska)', 'Polska'),
        DummyToken('t3', '5 (Niemcy)', 'Niemcy'),
        DummyToken('t4', '6 (Niemcy)', 'Niemcy', visible_for=[2, 5]),
    ]
    return engine

def test_visible_tokens_for_general(sample_engine):
    player = Player(1, 'Polska', 'Generał')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert ids == {'t1', 't2'}

def test_visible_tokens_for_commander_poland(sample_engine):
    player = Player(2, 'Polska', 'Dowódca')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert ids == {'t1', 't4'}  # t4 ma visible_for=[2,5]

def test_visible_tokens_for_commander_germany(sample_engine):
    player = Player(5, 'Niemcy', 'Dowódca')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert ids == {'t3', 't4'}

def test_visible_tokens_for_general_germany(sample_engine):
    player = Player(4, 'Niemcy', 'Generał')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert ids == {'t3', 't4'}

def test_visible_tokens_for_commander_poland_no_tokens(sample_engine):
    # Dowódca polski, ale nie ma żadnych żetonów z ownerem '4 (Polska)'
    player = Player(4, 'Polska', 'Dowódca')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert ids == set()  # nie ma żetonów tego dowódcy

def test_visible_tokens_for_commander_with_only_visible_for(sample_engine):
    # Dowódca niemiecki, który nie ma własnych żetonów, ale jest na liście visible_for
    player = Player(5, 'Niemcy', 'Dowódca')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert 't4' in ids  # t4 ma visible_for=[2,5]

def test_visible_tokens_for_general_with_visible_for(sample_engine):
    # Generał niemiecki widzi wszystko swojej nacji, nawet jeśli jest visible_for
    player = Player(6, 'Niemcy', 'Generał')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert 't3' in ids and 't4' in ids

def test_visible_tokens_for_commander_poland_and_visible_for(sample_engine):
    # Dowódca polski, który ma własny żeton i jest na liście visible_for żetonu niemieckiego
    player = Player(2, 'Polska', 'Dowódca')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert 't1' in ids and 't4' in ids

def test_visible_tokens_for_commander_germany_and_visible_for(sample_engine):
    # Dowódca niemiecki, który ma własny żeton i jest na liście visible_for żetonu niemieckiego
    player = Player(6, 'Niemcy', 'Dowódca')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert 't4' in ids  # t4 ma visible_for=[2,5], ale owner to '6 (Niemcy)' więc nie jest ownerem, ale jest na liście

def test_visible_tokens_for_general_poland_no_tokens(sample_engine):
    # Generał polski, ale nie ma żadnych żetonów innej nacji
    player = Player(1, 'Polska', 'Generał')
    visible = sample_engine.get_visible_tokens(player)
    ids = {t.id for t in visible}
    assert 't3' not in ids and 't4' not in ids
