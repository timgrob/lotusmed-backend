class NotFoundError(Exception):
    """Raised when a lookup finds no matching row."""


class AlreadyExistsError(Exception):
    """Raised when a write violates a uniqueness rule."""


class UserNotFoundError(NotFoundError):
    """Raised when a user lookup finds no matching row."""


class UserAlreadyExistsError(AlreadyExistsError):
    """Raised when a write violates a unique user constraint."""


class UpstreamAIError(Exception):
    """Raised when an upstream AI provider fails or returns no output."""


class ProviderNotConfiguredError(Exception):
    """Raised when a requested AI provider has no API key configured."""
