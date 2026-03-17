import uuid
from typing import Dict, List, Optional
from models import Game
from connection_manager import ConnectionManager

class GameService:
    def __init__(self, manager: ConnectionManager):
        self.games: Dict[str, Game] = {}
        self.manager = manager

    def create_game(self, name: str, player_id: str, player_name: str) -> str:
        """Create a new game and add the first player."""
        game_id = str(uuid.uuid4())[:8]
        game = Game(game_id=game_id, name=name)
        game.add_player(player_id, player_name)
        self.games[game_id] = game
        return game_id

    def get_game(self, game_id: str) -> Optional[Game]:
        """Retrieve a game by ID."""
        return self.games.get(game_id)

    def list_games(self) -> List[dict]:
        """Return summaries of all active games."""
        return [game.to_summary() for game in self.games.values()]

    async def broadcast_lobby_update(self):
        """Notify all lobby users of game changes."""
        await self.manager.broadcast_lobby({
            "event": "lobby_update", 
            "games": self.list_games()
        })
