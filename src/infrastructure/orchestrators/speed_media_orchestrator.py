import mimetypes
import logging

from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput
from src.infrastructure.services.audio_speed_service import AudioSpeedService
from src.infrastructure.services.video_speed_service import VideoSpeedService

logger = logging.getLogger(__name__)

class SpeedMediaOrchestrator:
    """Orchestrates the speed modification process by delegating to the correct service."""

    def __init__(self, url: str, factor: float, preserve_pitch: bool, custom_pitch: float | None = None):
        self.url = url
        self.factor = factor
        self.preserve_pitch = preserve_pitch
        self.custom_pitch = custom_pitch
        self._processor = None

    async def __aenter__(self):
        logger.debug(f"SpeedMediaOrchestrator entering with url: {self.url}")
        mime_type, _ = mimetypes.guess_type(self.url)
        if not mime_type:
            logger.warning(f"Could not determine file type from URL: {self.url}")
            raise ValueError("Could not determine file type from URL.")

        logger.debug(f"Guessed MIME type: {mime_type} for URL: {self.url}")

        if mime_type.startswith('audio/'):
            logger.debug("Selected AudioSpeedService as processor.")
            self._processor = AudioSpeedService(self.url, self.factor, self.preserve_pitch)
        elif mime_type.startswith('video/'):
            logger.debug("Selected VideoSpeedService as processor.")
            self._processor = VideoSpeedService(self.url, self.factor, self.preserve_pitch)
        else:
            logger.warning(f"Unsupported MIME type: {mime_type}")
            raise ValueError(f"Unsupported MIME type: {mime_type}")
        
        await self._processor.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        if self._processor:
            await self._processor.__aexit__(exc_type, exc_val, tb)

    async def get_response(self) -> SpeedMediaOutput:
        logger.debug("Getting response from processor.")
        if not self._processor:
            logger.warning("Processor was not initialized before getting response.")
            raise RuntimeError("Processor was not initialized.")
        
        response = await self._processor.get_response()
        logger.debug(f"Got response from processor: {response}")
        return response
