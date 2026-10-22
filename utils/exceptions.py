"""Application errors that the CLI can explain to the user."""


class AppError(Exception):
    """Base class for expected application failures."""


class ValidationError(AppError):
    """Raised when user input does not meet a field rule."""


class NotFoundError(AppError):
    """Raised when a requested record does not exist."""


class StorageError(AppError):
    """Raised when the JSON database cannot be read or written safely."""
