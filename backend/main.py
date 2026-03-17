import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dto.game_dto import CreateGameRequest
from connection_manager import ConnectionManager
from dependencies import get_manager, get_game_service
from game_service import GameService
from exceptions import GameError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sea Battle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for game-related errors
@app.exception_handler(GameError)
async def game_error_handler(request: Request, exc: GameError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )

@app.get("/games")
async def list_games(service: GameService = Depends(get_game_service)):
    return service.list_games()

@app.post("/games/create")
async def create_game(
    request: CreateGameRequest, 
    service: GameService = Depends(get_game_service)
):
    game_id = service.create_game(request.name, request.player_id, request.player_name)
    await service.broadcast_lobby_update()
    return {"game_id": game_id}

@app.websocket("/ws/lobby")
async def lobby_websocket(
    websocket: WebSocket,
    manager: ConnectionManager = Depends(get_manager),
    service: GameService = Depends(get_game_service)
):
    await manager.connect_lobby(websocket)
    try:
        # Send initial list
        await manager.send_personal_message({"event": "lobby_update", "games": service.list_games()}, websocket)
        while True:
            await websocket.receive_text() # Keep-alive
    except WebSocketDisconnect:
        manager.disconnect_lobby(websocket)

@app.websocket("/ws/{game_id}/{player_id}")
async def game_websocket_endpoint(
    websocket: WebSocket, 
    game_id: str, 
    player_id: str,
    name: str = None, 
    manager: ConnectionManager = Depends(get_manager),
    service: GameService = Depends(get_game_service)
):
    game = service.get_game(game_id)
    if not game:
        await websocket.close(code=1008, reason="Game not found")
        return

    try:
        game.add_player(player_id, name)
        player_obj = game.player_map[player_id]
        
        await manager.connect(websocket, game_id)
        player_obj.online = True
        await service.broadcast_lobby_update()
        
        # Initial state sync
        opponent_id = next((id for id in game.players if id != player_id), None)
        opponent_view = None
        if opponent_id:
            opponent_view = game.player_map[opponent_id].board.get_opponent_view()

        await manager.send_personal_message({
            "event": "sync_state",
            "status": game.status,
            "players": game.players,
            "player_names": {p.id: p.name for p in game.player_map.values()},
            "board": player_obj.board.grid,
            "opponent_board": opponent_view,
            "ships": [{"name": s.name, "size": s.size, "coords": s.coordinates} for s in player_obj.board.ships],
            "turn": game.players[game.turn] if game.status == "playing" else None
        }, websocket)

        # Broadcast join info
        if game.status == "setup":
            await manager.broadcast({"event": "game_setup", "players": game.players, "player_names": {p.id: p.name for p in game.player_map.values()}}, game_id)
        elif game.status == "playing":
            await manager.broadcast({"event": "player_reconnected", "player_id": player_id}, game_id)
        else:
            await manager.broadcast({"event": "player_joined", "player_id": player_id, "name": player_obj.name}, game_id)

        while True:
            data = await websocket.receive_json()
            await handle_game_event(websocket, game, player_id, data, manager, service)

    except (WebSocketDisconnect, ConnectionResetError):
        player_obj.online = False
        manager.disconnect(websocket)
        await manager.broadcast({"event": "player_disconnected", "player_id": player_id}, game_id)
        await service.broadcast_lobby_update()
    except Exception as e:
        logger.error(f"Error in game WebSocket: {e}", exc_info=True)
        if websocket.client_state.name != 'DISCONNECTED':
            await websocket.close(code=1011)

async def handle_game_event(websocket: WebSocket, game, player_id, data, manager, service):
    event = data.get("event")
    game_id = game.game_id
    
    try:
        if event == "place_ships":
            game.place_ships(player_id, data.get("ships", []))
            if game.status == "playing":
                await manager.broadcast({"event": "game_start", "turn": game.players[game.turn]}, game_id)
            else:
                await manager.broadcast({"event": "player_ready", "player_id": player_id}, game_id)
        
        elif event == "shoot":
            result = game.shoot(player_id, data.get("x"), data.get("y"))
            broadcast_data = {
                "event": "move_made",
                "player_id": player_id,
                "x": data.get("x"),
                "y": data.get("y"),
                "is_hit": result["hit"],
            }
            if result.get("game_over"):
                broadcast_data["event"] = "game_over"
                broadcast_data["winner"] = result["winner"]
            else:
                broadcast_data["next_turn"] = result["next_turn"]
            await manager.broadcast(broadcast_data, game_id)
            
    except GameError as e:
        await manager.send_personal_message({"event": "error", "message": str(e)}, websocket)
