import logging
from typing import cast
from discord.ext.commands import Bot, AutoShardedBot
from src.bootstrap.models.application import Application
from src.bootstrap.startup import (
    ArgParser,
    DiscordExtensionStartup,
    LoggingConfigurator,
    LoggingSetup,
    SettingsBuilder,
    ExtensionServicesBuilder,
    DriveSetup,
)
from src.infrastructure.services.config.models import ApplicationSettings
from src.infrastructure.services.discord import BaseBot
from src.infrastructure.services.discord.factories.bot_factory import BotFactory

class ApplicationBuilder:
    """Builds the application and all its runtime dependencies."""

    def __init__(self) -> None:
        self.settings: ApplicationSettings | None = None
        self.bot: BaseBot | None = None
        self.logger: logging.Logger | None = None

    def _configure_logging(self) -> None:
        """Configures logging."""
        logging_configurator = LoggingConfigurator(
            arg_parser=ArgParser(),
            logging_setup=LoggingSetup(),
        )
        logging_configurator.configure()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _build_settings(self) -> None:
        """Builds application settings."""
        if not self.logger:
            raise RuntimeError("Logger must be configured before building settings.")
        self.logger.info("Building application settings")

        self.settings = SettingsBuilder().build_settings()

    async def _build_google_drive(self) -> None:
        """Builds Google Drive-related components."""
        if self.settings is None or not self.logger:
            raise RuntimeError("Settings and logger must be configured before Google Drive components.")

        if self.settings.drive_settings is None:
            raise RuntimeError("Drive settings must be configured.")


        self.drive_login_service = await DriveSetup(
            drive_settings=self.settings.drive_settings,
        ).build_login_service()

        self.logger.info("Google Drive login service built successfully")
        
    async def _build_discord(self) -> None:
        """Builds Discord-related components."""
        if self.settings is None or not self.logger:
            raise RuntimeError("Settings and logger must be configured before Discord components.")

        if self.settings.bot_settings is None:
            raise RuntimeError("Bot settings must be configured.")

        if self.settings.download_settings is None:
            raise RuntimeError("Download settings must be configured.")
        
        if not self.drive_login_service:
            raise RuntimeError("Drive login service must be built before Discord components.")

        self.logger.info("Building Discord bot")

        self.bot = BotFactory(
            basebot=BaseBot,
            logger=self.logger,
        ).create_bot(settings=self.settings.bot_settings)

        discord_startup = DiscordExtensionStartup(
            bot=cast(Bot, self.bot),
        )

        extension_services = ExtensionServicesBuilder(
            drive_login=self.drive_login_service,
        ).build_services(settings=self.settings)

        await discord_startup.load_extensions(services=extension_services)
        self.logger.info("Discord bot built successfully")

    async def build(self) -> Application:
        """Builds the full application."""
        self._configure_logging()

        if not self.logger:
            raise RuntimeError("Logging configuration failed.")

        self._build_settings()
        await self._build_google_drive()
        await self._build_discord()

        if self.bot is None or self.settings is None:
            raise RuntimeError("Application not fully built")

        self.logger.info("Assembling application")

        return Application(
            bot=cast(AutoShardedBot, self.bot),
            drive=self.drive_login_service,
            settings=self.settings,
        )
