import logging
import subprocess
from pathlib import Path

from .base_speed_service import BaseSpeedService
from src.domain.exceptions import InvalidSpeedRequest
from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput
from src.infrastructure.services.get_info import MediaInfoExtractor

logger = logging.getLogger(__name__)

class AudioSpeedService(BaseSpeedService):
    """Handles audio speed modification using ffmpeg for all operations."""

    def __init__(self, url: str, factor: float, preserve_pitch: bool):
        super().__init__(service_name="audio_speed", url=url, factor=factor, preserve_pitch=preserve_pitch)

    def _process_media(self, input_path: Path) -> Path:
        logger.debug(f"Processing audio media at: {input_path}")
        output_path = self.temp_dir / f"speed_{self.factor}_output.{self._input_format}"

        if self.preserve_pitch:
            # Use ffmpeg with rubberband filter for high-quality pitch preservation
            logger.debug("Using ffmpeg with rubberband for pitch preservation.")
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-filter:a', f'rubberband=tempo={self.factor}',
                '-y', str(output_path)
            ]
        else:
            # Use ffmpeg with asetrate for speed change without pitch preservation
            logger.debug("Using ffmpeg with asetrate for speed change without pitch preservation.")
            sample_rate = MediaInfoExtractor.get_audio_sample_rate(input_path)
            if not sample_rate:
                logger.error("Could not determine original audio sample rate.")
                raise InvalidSpeedRequest("Could not determine original audio sample rate.")
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-filter:a', f'asetrate={sample_rate * self.factor}',
                '-y', str(output_path)
            ]
        
        logger.debug(f"Executing ffmpeg command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug("FFmpeg audio processing completed successfully.")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed for audio processing: {e.stderr}")
            raise InvalidSpeedRequest(f"FFmpeg processing failed: {e.stderr}")


