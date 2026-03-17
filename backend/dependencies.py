from connection_manager import ConnectionManager
from game_service import GameService

# Singletons for dependency injection
_manager = ConnectionManager()
_game_service = GameService(_manager)

def get_manager() -> ConnectionManager:
    return _manager

def get_game_service() -> GameService:
    return _game_service
