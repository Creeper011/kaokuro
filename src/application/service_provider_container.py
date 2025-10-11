from typing import Set
from src.application.config.yaml_settings import YamlSettingsManager
from src.domain.usecases import DownloadUsecase, ExtractAudioUsecase, SpeedMediaUseCase
from src.infrastructure.orchestrators import DownloadOrchestrator, SpeedMediaOrchestrator
from src.infrastructure.services import AudioExtractService

class ServiceProviderContainer:
    """
    Container responsible for building and providing use cases (domain services),
    injecting necessary configurations and dependencies.
    """
    def __init__(self, settings_manager: YamlSettingsManager):
        self._settings_manager = settings_manager
        blacklist_list = self._settings_manager.get({"Download": "blacklist_sites"}) or []
        self._blacklist_sites: Set[str] = set(blacklist_list)

    def build_download_usecase(self) -> DownloadUsecase:
        """Builds the DownloadUsecase, injecting the site blacklist."""
        return DownloadUsecase(
            service=DownloadOrchestrator,
            blacklist=self._blacklist_sites
        )

    def build_extract_audio_usecase(self) -> ExtractAudioUsecase:
        """Builds the ExtractAudioUsecase."""
        return ExtractAudioUsecase(service=AudioExtractService)
    
    def build_speed_media_usecase(self):
        """Builds the SpeedMediaUseCase."""
        return SpeedMediaUseCase(service=SpeedMediaOrchestrator)