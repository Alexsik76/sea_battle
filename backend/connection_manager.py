from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # game_id -> [player1_ws, player2_ws]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # ws -> game_id
        self.ws_to_game: Dict[WebSocket, str] = {}
        # lobby connections
        self.lobby_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        self.ws_to_game[websocket] = game_id

    async def connect_lobby(self, websocket: WebSocket):
        await websocket.accept()
        self.lobby_connections.append(websocket)

    def disconnect_lobby(self, websocket: WebSocket):
        if websocket in self.lobby_connections:
            self.lobby_connections.remove(websocket)

    def disconnect(self, websocket: WebSocket):
        game_id = self.ws_to_game.get(websocket)
        if game_id and game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
        if websocket in self.ws_to_game:
            del self.ws_to_game[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, game_id: str):
        if game_id in self.active_connections:
            # Create a copy of the list to avoid issues if a disconnect happens during iteration
            connections = list(self.active_connections[game_id])
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Cleanup will be handled by the disconnect handler in main.py
                    pass

    async def broadcast_lobby(self, message: dict):
        for connection in self.lobby_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass # Already disconnected probably
