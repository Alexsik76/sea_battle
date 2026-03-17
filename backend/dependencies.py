from connection_manager import ConnectionManager
from typing import Dict
from models import Game

# Singletons for dependency injection
_manager = ConnectionManager()
_games: Dict[str, Game] = {}

def get_manager() -> ConnectionManager:
    return _manager

def get_games() -> Dict[str, Game]:
    return _games
