from enum import Enum

class ErrorTypes(Enum):
    """Defines error types"""
    UNKNOWN = "UNKNOWN"
    BOT_DISCORD_ERROR = "BOT_DISCORD_ERROR"
    PLAYER_ERROR = "PLAYER_ERROR"
    VOICE_ERROR = "VOICE_ERROR"
    NOT_CONNECTED_TO_VOICE = "NOT_CONNECTED_TO_VOICE"