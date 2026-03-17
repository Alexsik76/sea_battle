from typing import List, Tuple, Optional, Dict
from pydantic import BaseModel, Field
from exceptions import (
    ShipPlacementError, 
    InvalidMoveError, 
    GameStateError, 
    PlayerNotFoundError,
    GameError
)

class Ship(BaseModel):
    name: str
    size: int
    coordinates: List[Tuple[int, int]] = []
    hits: int = 0

    @property
    def is_sunk(self) -> bool:
        return self.hits >= self.size

class Board(BaseModel):
    size: int = 10
    grid: List[List[Optional[str]]] = Field(default_factory=lambda: [[None for _ in range(10)] for _ in range(10)])
    ships: List[Ship] = Field(default_factory=list)

    def place_ship(self, ship_name: str, size: int, coords: List[Tuple[int, int]]):
        if len(coords) != size:
            raise ShipPlacementError(f"Ship {ship_name} requires {size} coordinates, got {len(coords)}")
        
        # Check boundaries and duplicates
        coord_set = set()
        for x, y in coords:
            if not (0 <= x < self.size and 0 <= y < self.size):
                raise ShipPlacementError(f"Coordinate ({x}, {y}) out of bounds")
            if (x, y) in coord_set:
                raise ShipPlacementError(f"Duplicate coordinate ({x}, {y}) in ship")
            coord_set.add((x, y))

        # Check if straight line and contiguous
        xs = sorted([c[0] for c in coords])
        ys = sorted([c[1] for c in coords])
        
        is_horizontal = all(y == ys[0] for y in ys) and all(xs[i+1] == xs[i] + 1 for i in range(len(xs)-1))
        is_vertical = all(x == xs[0] for x in xs) and all(ys[i+1] == ys[i] + 1 for i in range(len(ys)-1))
        
        if not (is_horizontal or is_vertical) and size > 1:
            raise ShipPlacementError("Ship must be placed in a straight horizontal or vertical line")

        # Check "no touching" rule
        for x, y in coords:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        for existing_ship in self.ships:
                            if (nx, ny) in existing_ship.coordinates:
                                raise ShipPlacementError("Ships cannot touch each other, even diagonally")
        
        # Update grid and add ship
        for x, y in coords:
            self.grid[y][x] = "ship"
            
        self.ships.append(Ship(name=ship_name, size=size, coordinates=[(x, y) for x, y in coords]))

    def receive_shot(self, x: int, y: int) -> Tuple[bool, Optional[Ship]]:
        if self.grid[y][x] in ["hit", "miss"]:
             raise InvalidMoveError("Already shot at this coordinate")
             
        for ship in self.ships:
            if (x, y) in ship.coordinates:
                ship.hits += 1
                self.grid[y][x] = "hit"
                return True, ship if ship.is_sunk else None
        
        self.grid[y][x] = "miss"
        return False, None

    def all_sunk(self) -> bool:
        return all(ship.is_sunk for ship in self.ships)

class Player(BaseModel):
    id: str
    name: str = "Player"
    board: Board = Field(default_factory=Board)
    ready: bool = False
    online: bool = True

class Game(BaseModel):
    game_id: str
    players: List[str] = Field(default_factory=list) # List of IDs for order
    player_map: Dict[str, Player] = Field(default_factory=dict)
    turn: int = 0
    status: str = "waiting" # waiting, setup, playing, finished

    def add_player(self, player_id: str, name: str = None):
        if player_id in self.player_map:
            return # Re-joining
            
        if len(self.players) >= 2:
            raise GameStateError("Game is already full")
            
        self.players.append(player_id)
        default_name = f"Player {len(self.players)}"
        self.player_map[player_id] = Player(id=player_id, name=name or default_name)
        
        if len(self.players) == 2:
            self.status = "setup"

    def place_ships(self, player_id: str, ship_data: List[dict]):
        try:
            player = self.player_map[player_id]
        except KeyError:
            raise PlayerNotFoundError(f"Player {player_id} not found in game")
            
        player.board.ships = [] # Reset
        
        try:
            for s in ship_data:
                player.board.place_ship(s['name'], s['size'], s['coords'])
        except ShipPlacementError:
            player.board.ships = []
            raise
        
        player.ready = True
        
        # Check if both ready
        if all(p.ready for p in self.player_map.values()) and len(self.players) == 2:
            self.status = "playing"
            self.turn = 0

    def shoot(self, player_id: str, x: int, y: int) -> Dict:
        if self.status != "playing":
            raise GameStateError("Game not in playing state")
        
        try:
            current_player_id = self.players[self.turn]
        except IndexError:
             raise GameError("Game state inconsistency: turn refers to non-existent player")

        if player_id != current_player_id:
            raise InvalidMoveError("Not your turn")

        opponent_id = self.players[1 - self.turn]
        try:
            opponent = self.player_map[opponent_id]
        except KeyError:
            raise PlayerNotFoundError("Opponent information not found")
        
        is_hit, sunk_ship = opponent.board.receive_shot(x, y)
        
        if opponent.board.all_sunk():
            self.status = "finished"
            return {"hit": is_hit, "sunk": True, "game_over": True, "winner": player_id}
        
        if not is_hit:
            self.turn = 1 - self.turn
            
        return {"hit": is_hit, "sunk": sunk_ship is not None, "game_over": False, "next_turn": self.players[self.turn]}
