from pydantic import BaseModel
from typing import List

class CreateGameRequest(BaseModel):
    name: str
    player_id: str
    player_name: str

class JoinGameRequest(BaseModel):
    game_id: str
    player_id: str

class PlaceShipsRequest(BaseModel):
    game_id: str
    player_id: str
    ships: List[dict] # {name: str, coords: List[List[int, int]]}

class ShootRequest(BaseModel):
    game_id: str
    player_id: str
    x: int
    y: int
