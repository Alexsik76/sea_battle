import pytest
from fastapi.testclient import TestClient
from main import app
from dependencies import get_game_service
from models import Game, Board
from exceptions import ShipPlacementError, InvalidMoveError, GameStateError, PlayerNotFoundError, GameError
from connection_manager import ConnectionManager
from game_service import GameService

client = TestClient(app)

# --- ConnectionManager Tests ---

@pytest.mark.asyncio
async def test_connection_manager():
    manager = ConnectionManager()
    
    # Mock WebSocket
    class MockWebSocket:
        def __init__(self):
            self.sent = []
            self.accepted = False
            self.closed = False
        async def accept(self):
            self.accepted = True
        async def send_json(self, data):
            self.sent.append(data)
        async def close(self, code=1000):
            self.closed = True

    ws1 = MockWebSocket()
    async def mock_accept(): pass
    ws1.accept = mock_accept

    await manager.connect(ws1, "game1")
    assert manager.active_connections["game1"] == [ws1]
    assert manager.ws_to_game[ws1] == "game1"

    ws_lobby = MockWebSocket()
    ws_lobby.accept = mock_accept
    await manager.connect_lobby(ws_lobby)
    assert ws_lobby in manager.lobby_connections

    await manager.send_personal_message({"msg": "hi"}, ws1)
    assert ws1.sent == [{"msg": "hi"}]

    await manager.broadcast({"msg": "bcast"}, "game1")
    assert ws1.sent == [{"msg": "hi"}, {"msg": "bcast"}]

    await manager.broadcast_lobby({"msg": "lobby"})
    assert ws_lobby.sent == [{"msg": "lobby"}]

    manager.disconnect_lobby(ws_lobby)
    assert ws_lobby not in manager.lobby_connections

    manager.disconnect(ws1)
    assert "game1" not in manager.active_connections
    assert ws1 not in manager.ws_to_game

    # Test broadcast with exception
    ws2 = MockWebSocket()
    ws2.accept = mock_accept
    await manager.connect(ws2, "game2")
    async def raise_err(data): raise Exception("fail")
    ws2.send_json = raise_err
    await manager.broadcast({"msg": "fail"}, "game2") # Should not raise

    # Test broadcast_lobby with exception
    await manager.connect_lobby(ws_lobby)
    ws_lobby.send_json = raise_err
    await manager.broadcast_lobby({"msg": "fail"}) # Should not raise

# --- GameService Tests ---

def test_game_service():
    manager = ConnectionManager()
    service = GameService(manager)
    
    gid = service.create_game("Test", "p1", "Player 1")
    assert len(gid) == 8
    assert gid in service.games
    
    game = service.get_game(gid)
    assert game.name == "Test"
    
    assert service.get_game("nonexistent") is None
    
    summaries = service.list_games()
    assert len(summaries) == 1
    assert summaries[0]["name"] == "Test"

# --- Model Edge Cases ---

def test_board_edge_cases():
    board = Board(size=5)
    
    # Wrong size
    with pytest.raises(ShipPlacementError, match="requires 2 coordinates"):
        board.place_ship("s1", 2, [(0,0)])
        
    # Out of bounds
    with pytest.raises(ShipPlacementError, match="out of bounds"):
        board.place_ship("s1", 1, [(5,5)])
        
    # Duplicate coords
    with pytest.raises(ShipPlacementError, match="Duplicate coordinate"):
        board.place_ship("s1", 2, [(0,0), (0,0)])
        
    # Not straight
    with pytest.raises(ShipPlacementError, match="straight horizontal or vertical"):
        board.place_ship("s1", 3, [(0,0), (1,1), (2,2)])
        
    # touching diagonally
    board.place_ship("s1", 1, [(0,0)])
    with pytest.raises(ShipPlacementError, match="cannot touch each other"):
        board.place_ship("s2", 1, [(1,1)])

    # Double shot
    board.receive_shot(4,4)
    with pytest.raises(InvalidMoveError, match="Already shot"):
        board.receive_shot(4,4)

    # Sunk info
    board.place_ship("s3", 1, [(3,3)])
    hit, ship = board.receive_shot(3,3)
    assert hit is True
    assert ship is not None
    assert ship.is_sunk is True
    
    # View
    view = board.get_opponent_view()
    assert view[3][3] == "hit"
    assert view[4][4] == "miss"
    assert view[0][0] is None

def test_game_edge_cases():
    game = Game(game_id="g1", name="G1")
    game.add_player("p1", "P1")
    game.add_player("p2", "P2")
    
    # Full game
    with pytest.raises(GameStateError, match="already full"):
        game.add_player("p3", "P3")
        
    # Re-join
    game.add_player("p1") # Should just return
    
    # place_ships invalid player
    with pytest.raises(PlayerNotFoundError):
        game.place_ships("p3", [])
        
    # place_ships error reset
    with pytest.raises(ShipPlacementError):
        game.place_ships("p1", [{"name":"s1", "size":1, "coords":[(0,0)]}, {"name":"s2", "size":1, "coords":[(0,0)]}])
    assert len(game.player_map["p1"].board.ships) == 0

    # Shoot not playing
    with pytest.raises(GameStateError, match="not in playing state"):
        game.shoot("p1", 0, 0)
        
    # Setup for play
    game.place_ships("p1", [{"name":"s1", "size":1, "coords":[(0,0)]}])
    game.place_ships("p2", [{"name":"s1", "size":1, "coords":[(0,0)]}])
    assert game.status == "playing"
    
    # Not your turn
    with pytest.raises(InvalidMoveError, match="Not your turn"):
        game.shoot("p2", 0, 0)
        
    # Turn out of range
    game.turn = 5
    with pytest.raises(GameError, match="Game state inconsistency"):
        game.shoot("p1", 0, 0)
        
    # Opponent not found (inconsistent state)
    game.turn = 0
    game.players = ["p1", "p3"]
    with pytest.raises(PlayerNotFoundError):
        game.shoot("p1", 0, 0)

# --- API Tests ---

def test_api_list_games():
    response = client.get("/games")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_create_game():
    response = client.post("/games/create", json={
        "name": "API Game",
        "player_id": "p_api",
        "player_name": "P API"
    })
    assert response.status_code == 200
    assert "game_id" in response.json()

# --- WebSocket Tests ---

def test_websocket_lobby():
    with client.websocket_connect("/ws/lobby") as websocket:
        data = websocket.receive_json()
        assert data["event"] == "lobby_update"

def test_websocket_full_game_play():
    # Create game
    resp = client.post("/games/create", json={"name": "WS Play", "player_id": "p1", "player_name": "P1"})
    gid = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{gid}/p1?name=P1") as ws1:
        ws1.receive_json() # sync
        
        with client.websocket_connect(f"/ws/{gid}/p2?name=P2") as ws2:
            ws2.receive_json() # sync
            
            # Place ships
            ws1.send_json({"event": "place_ships", "ships": [{"name": "s1", "size": 1, "coords": [[0,0]]}]})
            ws2.send_json({"event": "place_ships", "ships": [{"name": "s1", "size": 1, "coords": [[0,0]]}]})
            
            # Wait for game_start
            msg = ws1.receive_json()
            while msg["event"] != "game_start":
                msg = ws1.receive_json()
            
            # P1 shoots and wins
            ws1.send_json({"event": "shoot", "x": 0, "y": 0})
            
            # ws1 should receive move_made or game_over
            msg = ws1.receive_json()
            assert msg["event"] == "game_over"
            assert msg["winner"] == "p1"

def test_websocket_errors_and_disconnect():
    resp = client.post("/games/create", json={"name": "Err Test", "player_id": "p1", "player_name": "P1"})
    gid = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{gid}/p1") as ws1:
        ws1.receive_json() # sync_state
        # Invalid shoot (not playing)
        ws1.send_json({"event": "shoot", "x": 0, "y": 0})
        
        # We might receive 'player_joined' broadcast before 'error'
        msg = ws1.receive_json()
        while msg["event"] != "error":
            msg = ws1.receive_json()
            
        assert msg["event"] == "error"

def test_websocket_not_found():
    with client.websocket_connect("/ws/wrongid/p1") as ws:
        data = ws.receive_json()
        assert data["event"] == "error"
        assert "not found" in data["message"]

def test_websocket_invalid_json():
    resp = client.post("/games/create", json={"name": "JSON test", "player_id": "p1", "player_name": "P1"})
    gid = resp.json()["game_id"]
    with client.websocket_connect(f"/ws/{gid}/p1") as ws:
        ws.receive_json() # sync_state
        ws.send_text("not json")
        ws.send_json({"event": "place_ships", "ships": []})
        data = ws.receive_json()
        assert data["event"] in ["player_ready", "game_setup", "player_joined"]

@pytest.mark.asyncio
async def test_lobby_broadcast_coverage():
    service = get_game_service()
    await service.broadcast_lobby_update()
