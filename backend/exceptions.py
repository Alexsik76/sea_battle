class GameError(Exception):
    """Base exception for all game-related errors."""
    pass

class GameNotFoundError(GameError):
    """Raised when a requested game ID does not exist."""
    pass

class PlayerNotFoundError(GameError):
    """Raised when a player is not part of the game."""
    pass

class InvalidMoveError(GameError):
    """Raised when a player makes an invalid move (e.g., out of turn, already shot)."""
    pass

class ShipPlacementError(GameError):
    """Raised when ship placement fails validation."""
    pass

class GameStateError(GameError):
    """Raised when an action is performed in an inappropriate game status."""
    pass
