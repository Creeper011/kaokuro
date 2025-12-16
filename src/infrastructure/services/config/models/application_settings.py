from typing import Optional
from discord import Intents
from dataclasses import dataclass

@dataclass(frozen=True)
class BotSettings():
    """All settings related to discord bot"""
    token: Optional[str] = None
    intents: Optional[Intents] = None

@dataclass(frozen=True)
class ApplicationSettings():
    """All settings"""
    bot_settings: Optional[BotSettings] = None
    
