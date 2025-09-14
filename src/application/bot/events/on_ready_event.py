import discord
import logging
from discord.ext import commands
from src.application.bot.load_extensions import ExtensionLoader

logger = logging.getLogger(__name__)


class OnReadyEvent:
    """Event handler for bot ready state following clean architecture principles."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def handle_on_ready(self):
        """Handle the bot ready event with proper separation of concerns."""
        await self._load_extensions()
        await self._sync_commands()
        logger.info(f"commands synced")
        await self._set_bot_presence()
        logger.info(f"{self.bot.user} loaded")
    
    async def _load_extensions(self):
        """Load all bot extensions."""
        return await ExtensionLoader(self.bot).load_extensions()
    
    async def _sync_commands(self):
        """Sync slash commands with Discord."""
        return await self.bot.tree.sync()
    
    async def _set_bot_presence(self):
        """Set the bot's presence and status."""
        await self.bot.change_presence(
            activity=discord.CustomActivity(name=self.bot.custom_status_name, emoji=discord.PartialEmoji(name="🍰")),
            status=self.bot.status_presence
        )
        logger.debug(f"Status customization applied: Status: {self.bot.status_presence.name}, Mobile: {self.bot.mobile_identify}, Name: `{self.bot.custom_status_name}")
