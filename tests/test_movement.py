import pytest
from engine.board import Board
from engine.token import Token
from engine.action import MoveAction

class DummyEngine:
    def __init__(self, board, tokens):
        self.board = board
        self.tokens = tokens

@pytest.fixture
def simple_board_and_token(tmp_path):
    # Tworzymy minimalny map_data.json
    map_data = {
        "meta": {"hex_size": 40, "cols": 3, "rows": 3},
        "terrain": {
            "0,0": {}, "1,0": {}, "2,0": {},
            "0,1": {}, "1,1": {}, "2,1": {},
            "0,2": {}, "1,2": {}, "2,2": {}
        }
    }
    map_path = tmp_path / "map_data.json"
    with open(map_path, "w", encoding="utf-8") as f:
        import json; json.dump(map_data, f)
    board = Board(str(map_path))
    token = Token(id="T1", owner="A", stats={"move": 2}, q=0, r=0)
    board.set_tokens([token])
    return board, token

def test_astar_pathfinding(simple_board_and_token):
    board, token = simple_board_and_token
    path = board.find_path((0,0), (1,1), max_cost=2)
    assert path is not None
    assert path[0] == (0,0)
    assert path[-1] == (1,1)
    assert len(path) <= 3  # max 2 ruchy

def test_move_action_success(simple_board_and_token):
    board, token = simple_board_and_token
    engine = DummyEngine(board, [token])
    action = MoveAction("T1", 1, 1)
    success, msg = action.execute(engine)
    assert success
    assert token.q == 1 and token.r == 1

def test_move_action_too_far(simple_board_and_token):
    board, token = simple_board_and_token
    engine = DummyEngine(board, [token])
    action = MoveAction("T1", 2, 2)
    success, msg = action.execute(engine)
    assert not success
    assert token.q == 0 and token.r == 0
