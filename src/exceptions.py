class LifeLensException(Exception):
    """Base exception for all LifeLens related errors."""
    pass

class EngineInitializationError(LifeLensException):
    """Raised when the engine fails to initialize (e.g., missing API key)."""
    pass

class GenerationError(LifeLensException):
    """Raised when the AI model fails to generate a response."""
    pass

class ParsingError(LifeLensException):
    """Raised when the AI output cannot be parsed into expected Pydantic models."""
    pass
