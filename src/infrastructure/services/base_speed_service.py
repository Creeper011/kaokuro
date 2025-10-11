from pathlib import Path
import uuid
import shutil
import logging
import requests
import time
import asyncio
from abc import ABC, abstractmethod

from src.domain.exceptions import InvalidSpeedRequest
from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput

logger = logging.getLogger(__name__)

class BaseSpeedService(ABC):
    """Abstract base class for speed modification services."""

    def __init__(self, service_name: str, url: str, factor: float, preserve_pitch: bool):
        if not service_name:
            raise ValueError("service_name cannot be empty")
        self.service_name = service_name
        self.url = url
        self.factor = factor
        self.preserve_pitch = preserve_pitch
        self.session_id = uuid.uuid4()
        self.temp_dir = Path("./temp/") / self.service_name / str(self.session_id)
        self.start_time = time.time()
        self._output_path: Path | None = None
        self._metadata_preserved: bool = False
        self._input_format: str | None = None
        logger.debug(f"BaseSpeedService '{self.service_name}' initialized with session ID: {self.session_id}")

    async def __aenter__(self) -> "BaseSpeedService":
        logger.debug(f"Entering context for session ID: {self.session_id}")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            input_path = await asyncio.to_thread(self._download_media)
            self._output_path = await asyncio.to_thread(self._process_media, input_path)
            if self._output_path and self._output_path.exists():
                self._metadata_preserved = await asyncio.to_thread(self._preserve_mp3_metadata, input_path, self._output_path)
        except Exception as e:
            logger.error(f"An error occurred in session {self.session_id}: {e}", exc_info=True)
            await asyncio.to_thread(self._cleanup)
            raise e
        return self

    async def __aexit__(self, exc_type, exc_val, tb) -> None:
        pass

    def _cleanup(self):
        logger.debug(f"Performing cleanup for session ID: {self.session_id}")
        if not self.temp_dir.exists():
            logger.debug("Temporary directory does not exist, cleanup not needed.")
            return
        if self.temp_dir.parent.name != self.service_name or not self.temp_dir.is_dir():
            logger.error(f"Cleanup aborted on unsafe path: {self.temp_dir}")
            return
        shutil.rmtree(self.temp_dir)
        logger.debug(f"Successfully removed temporary directory: {self.temp_dir}")

    def _download_media(self) -> Path:
        logger.debug(f"Starting media download from URL: {self.url}")
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            
            self._input_format = content_type.split('/')[-1]
            if self._input_format == 'mpeg': self._input_format = 'mp3'

            input_path = self.temp_dir / f"input.{self._input_format}"
            logger.debug(f"Downloading to temporary file: {input_path}")
            with open(input_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.debug("Media download completed successfully.")
            return input_path
        except requests.RequestException as e:
            logger.error(f"Failed to download media from {self.url}: {e}", exc_info=True)
            raise InvalidSpeedRequest(f"Failed to download media from {self.url}: {e}")

    @abstractmethod
    def _process_media(self, input_path: Path) -> Path:
        """Process the media file to change its speed. Must be implemented by subclasses."""
        ...

    def _preserve_mp3_metadata(self, input_path: Path, output_path: Path) -> bool:
        # This is concrete as it's the same for any service dealing with MP3s
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3
        if not (self._input_format == 'mp3' and output_path.exists()):
            logger.debug("Skipping metadata preservation: not an MP3 or output file does not exist.")
            return False
        try:
            logger.debug(f"Attempting to preserve MP3 metadata from {input_path} to {output_path}")
            original_audio = MP3(input_path, ID3=ID3)
            if not original_audio.tags:
                logger.debug("No metadata found in original audio.")
                return False
            new_audio = MP3(output_path, ID3=ID3)
            new_audio.tags = original_audio.tags
            new_audio.save()
            logger.debug("MP3 metadata preserved successfully.")
            return True
        except Exception as e:
            logger.warning(f"Failed to preserve MP3 metadata: {e}", exc_info=True)
            return False

    async def get_response(self) -> SpeedMediaOutput:
        """Builds the final DTO with the results and cleanup callable."""
        logger.debug("Building final response DTO.")
        from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput
        elapsed_time = time.time() - self.start_time
        response = SpeedMediaOutput(
            file_path=self._output_path,
            metadata_preserved=self._metadata_preserved,
            elapsed=elapsed_time,
            cleanup=self._cleanup
        )
        logger.debug(f"Final response DTO created: {response}")
        return response
