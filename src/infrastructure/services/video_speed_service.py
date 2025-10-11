import logging
import subprocess
from pathlib import Path

from .base_speed_service import BaseSpeedService
from src.domain.exceptions import InvalidSpeedRequest
from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput
from src.infrastructure.services.get_info import MediaInfoExtractor

logger = logging.getLogger(__name__)

class VideoSpeedService(BaseSpeedService):
    """Handles video speed modification using direct ffmpeg calls."""

    def __init__(self, url: str, factor: float, preserve_pitch: bool):
        super().__init__(service_name="video_speed", url=url, factor=factor, preserve_pitch=preserve_pitch)

    def _process_media(self, input_path: Path) -> Path:
        logger.debug(f"Processing video media at: {input_path}")
        output_path = self.temp_dir / f"speed_{self.factor}_output.{self._input_format}"
        pts_factor = 1.0 / self.factor

        if self.preserve_pitch:
            logger.debug("Using ffmpeg with atempo for pitch preservation.")
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-filter:v', f'setpts={pts_factor}*PTS',
                '-filter:a', f'atempo={self.factor}',
                '-y', str(output_path)
            ]
        else:
            logger.debug("Using ffmpeg with asetrate for speed change without pitch preservation.")
            sample_rate = MediaInfoExtractor.get_audio_sample_rate(input_path)
            if not sample_rate:
                logger.error("Could not determine original audio sample rate for video.")
                raise InvalidSpeedRequest("Could not determine original audio sample rate for video.")

            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-filter_complex', f'[0:v]setpts={pts_factor}*PTS[v];[0:a]asetrate={sample_rate}*{self.factor}[a]',
                '-map', '[v]', '-map', '[a]',
                '-y', str(output_path)
            ]
        
        logger.debug(f"Executing ffmpeg command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug("FFmpeg video processing completed successfully.")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed for video processing: {e.stderr}")
            raise InvalidSpeedRequest(f"FFmpeg processing failed.")


