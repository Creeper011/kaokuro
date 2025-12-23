from logging import Logger
from discord.ext.commands import Cog, Bot
from src.core.constants import DEFAULT_COMMANDS_PATH
from src.infrastructure.services.discord.utils.extension_loader import ExtensionLoader
from src.infrastructure.filesystem.module_finder import ModuleFinder
from src.bootstrap.models.services import Services

class DiscordExtensionStartup():
    """Startup Extension Loader system injecting their dependencies"""

    def __init__(self, *, bot: Bot, logger: Logger) -> None:
        self.bot = bot
        self.logger = logger

    async def load_extensions(self, services: Services) -> None:
        extension_loader = ExtensionLoader(
            logger=self.logger,
            extension_finder=ModuleFinder(
                self.logger,
                DEFAULT_COMMANDS_PATH,
                Cog
            ),
            bot=self.bot,
            services=services
        )

        await extension_loader.load_extensions()
