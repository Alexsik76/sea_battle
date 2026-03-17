import pytest
from models import Game, Board
from exceptions import ShipPlacementError

def test_game_creation():
    game = Game(game_id="test", name="Test Game")
    assert game.game_id == "test"
    assert game.status == "waiting"

def test_add_players():
    game = Game(game_id="test", name="Test Game")
    game.add_player("p1", "Player 1")
    assert len(game.players) == 1
    game.add_player("p2", "Player 2")
    assert len(game.players) == 2
    assert game.status == "setup"

def test_ship_placement_valid():
    board = Board()
    # Horizontal ship of size 3
    board.place_ship("carrier", 3, [(0, 0), (1, 0), (2, 0)])
    assert len(board.ships) == 1
    assert board.grid[0][0] == "ship"

def test_ship_placement_invalid_touching():
    board = Board()
    board.place_ship("ship1", 1, [(0, 0)])
    with pytest.raises(ShipPlacementError):
        # Touching diagonally
        board.place_ship("ship2", 1, [(1, 1)])

def test_shooting():
    game = Game(game_id="test", name="Test Game")
    game.add_player("p1", "Player 1")
    game.add_player("p2", "Player 2")
    
    # Setup ships for both
    game.place_ships("p1", [{"name": "s1", "size": 1, "coords": [(0, 0)]}])
    game.place_ships("p2", [{"name": "s1", "size": 1, "coords": [(0, 0)]}])
    
    assert game.status == "playing"
    
    # Player 1 shoots and hits
    result = game.shoot("p1", 0, 0)
    assert result["hit"] is True
    assert result["game_over"] is True
    assert result["winner"] == "p1"
