class PlacementError(Exception):
    """Base exception for all placement portal domain errors."""
    status_code = 500
    
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

class NotFound(PlacementError):
    status_code = 404

class Unauthorized(PlacementError):
    """Raised when a request carries no token, an expired token, or an invalid token."""
    status_code = 401

class Forbidden(PlacementError):
    status_code = 403

class Conflict(PlacementError):
    status_code = 409

class ValidationError(PlacementError):
    status_code = 400
