
class DiscordException(Exception):
    """Base exception for all Discord-related errors, excluding presentation errors."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class BotException(DiscordException):
    """Raised when a general bot error occurs."""