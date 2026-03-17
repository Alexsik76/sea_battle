import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from models import Game
from dto.game_dto import CreateGameRequest
from connection_manager import ConnectionManager
from dependencies import get_manager, get_games
from exceptions import GameError

app = FastAPI(title="Sea Battle API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

game_names: Dict[str, str] = {} # game_id -> game_name

def get_game_list(games: Dict[str, Game]):
    return [{"id": gid, 
             "name": game_names.get(gid, "Unknown"), 
             "players": len(game.players), 
             "online_players": len([p for p in game.player_map.values() if p.online]),
             "player_names": [p.name for p in game.player_map.values()],
             "player_ids": game.players,
             "status": game.status} 
            for gid, game in games.items()]

@app.get("/games")
async def list_games(games: Dict[str, Game] = Depends(get_games)):
    return get_game_list(games)

async def broadcast_lobby_update(games, manager):
    await manager.broadcast_lobby({"event": "lobby_update", "games": get_game_list(games)})

@app.post("/games/create")
async def create_game(
    request: CreateGameRequest, 
    games: Dict[str, Game] = Depends(get_games),
    manager: ConnectionManager = Depends(get_manager)
):
    game_id = str(uuid.uuid4())[:8]
    game = Game(game_id=game_id)
    game.add_player(request.player_id, request.player_name)
    games[game_id] = game
    game_names[game_id] = request.name
    await broadcast_lobby_update(games, manager)
    return {"game_id": game_id}

@app.websocket("/ws/lobby")
async def lobby_websocket(
    websocket: WebSocket,
    manager: ConnectionManager = Depends(get_manager),
    games: Dict[str, Game] = Depends(get_games)
):
    await manager.connect_lobby(websocket)
    try:
        # Send initial list
        await manager.send_personal_message({"event": "lobby_update", "games": get_game_list(games)}, websocket)
        
        while True:
            await websocket.receive_text() # Just keep alive
    except WebSocketDisconnect:
        manager.disconnect_lobby(websocket)

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    game_id: str, 
    player_id: str,
    name: str = None, # Optional query param
    manager: ConnectionManager = Depends(get_manager),
    games: Dict[str, Game] = Depends(get_games)
):
    try:
        game = games[game_id]
        game.add_player(player_id, name)
        player_obj = game.player_map[player_id]
        
        await manager.connect(websocket, game_id)
        player_obj.online = True
        await broadcast_lobby_update(games, manager)
        
        # Send current state for reconnection
        ship_data = [{"name": s.name, "size": s.size, "coords": s.coordinates} for s in player_obj.board.ships]

        await manager.send_personal_message({
            "event": "sync_state",
            "status": game.status,
            "players": game.players,
            "player_names": {p.id: p.name for p in game.player_map.values()},
            "board": player_obj.board.grid,
            "ships": ship_data,
            "turn": game.players[game.turn] if game.status == "playing" else None
        }, websocket)

        # Broadcast updates
        if game.status == "setup":
            await manager.broadcast({"event": "game_setup", "players": game.players, "player_names": {p.id: p.name for p in game.player_map.values()}}, game_id)
        elif game.status == "playing":
            await manager.broadcast({"event": "player_reconnected", "player_id": player_id}, game_id)
        else:
            await manager.broadcast({"event": "player_joined", "player_id": player_id, "name": player_obj.name}, game_id)

    except (KeyError, GameError) as e:
        await websocket.close(code=1008, reason=str(e))
        return

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            
            try:
                if event == "place_ships":
                    game.place_ships(player_id, data.get("ships", []))
                    if game.status == "playing":
                        await manager.broadcast({"event": "game_start", "turn": game.players[game.turn]}, game_id)
                    else:
                        await manager.send_personal_message({"event": "waiting_for_opponent"}, websocket)

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

    except WebSocketDisconnect:
        player_obj.online = False
        manager.disconnect(websocket)
        await manager.broadcast({"event": "player_disconnected", "player_id": player_id}, game_id)
        await broadcast_lobby_update(games, manager)
