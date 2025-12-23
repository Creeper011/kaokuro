from logging import Logger
from src.infrastructure.services.config.utils.loaders_finder import LoadersFinder
from src.infrastructure.services.config.parsers import SettingsParser
from src.infrastructure.services.config.mappers import SettingsMapper
from src.infrastructure.services.config.settings_factory import SettingsFactory
from src.infrastructure.services.config.models.application_settings import ApplicationSettings

class SettingsBuilder():
    """Contains all process to build the settings (config) system"""

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def build_settings(self) -> ApplicationSettings:
        loaders_finder = LoadersFinder(self.logger)
        loader_classes = loaders_finder.find_loader_classes()
        loaders = [loader(logger=self.logger) for loader in loader_classes]

        parser = SettingsParser(logger=self.logger)
        mapper = SettingsMapper(logger=self.logger)

        settings_factory = SettingsFactory(self.logger, loaders, parser, mapper)
        return settings_factory.build_settings()