import time
import yt_dlp
import logging
import uuid
import shutil
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.domain.exceptions import (
    DownloadFailed,
    MediaFilepathNotFound,
    UnsupportedFormat,
)

logger = logging.getLogger(__name__)

DEFAULT_YT_DLP_SETTINGS = {
    'format': 'best',
    'postprocessors': [],
    'restrictfilenames': True,
    'noplaylist': True,
    'no_warnings': True,
    'concurrent_fragment_downloads': 10,
    'continue_dl': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': {'default': ['-x', '16', '-s', '16', '-k', '1M']},
    'match_filter': yt_dlp.utils.match_filter_func("!is_live"),
    'extractor_args': {
        #'youtubepot-bgutilhttp': 'base_url=http://127.0.0.1:4416'
    },
}

class YtDlpDownloader:
    """
    Basic downloader class that handles video/audio downloads using yt_dlp.
    Returns primitive data only - no metadata extraction or complex processing.
    """

    def __init__(self, url: str, format: str, quality: Optional[str] = None, should_transcode: bool = False):
        """Initialize downloader with URL, format, and optional quality."""
        logger.debug(f"Initializing YtDlpDownloader with url={url}, format={format}, quality={quality}, should_transcode={should_transcode}")
        self.url = url
        self.format = format.lower()
        self.quality = quality
        self.should_transcode = should_transcode
        self.is_audio = False

        self.FORMAT_MAP = {
            "mp4": {
                "format": "bestvideo{video_quality}[vcodec=avc1][ext=mp4]+bestaudio{audio_quality}/bestvideo[vcodec=avc1]{video_quality}+bestaudio{audio_quality}/bestvideo{video_quality}[ext=mp4]+bestaudio{audio_quality}/bestvideo{video_quality}+bestaudio{audio_quality}/bestvideo+bestaudio/best",
                "post": [{'key': 'FFmpegVideoConvertor', 'preferedformat': "mp4"} if should_transcode else {'key': 'FFmpegVideoRemuxer', 'preferedformat': "mp4"}],
                "is_audio": False
            },
            "mp3": {
                "format": "bestaudio{audio_quality}/bestaudio",
                "post": [{'key': 'FFmpegExtractAudio', 'preferredcodec': "mp3", 'preferredquality': '0'}],
                "is_audio": True
            },
            "mkv": {
                "format": "bestvideo{video_quality}+bestaudio{audio_quality}",
                "post": [{'key': 'FFmpegVideoConvertor', 'preferedformat': "mkv"} if should_transcode else {'key': 'FFmpegVideoRemuxer', 'preferedformat': "mkv"}],
                "is_audio": False
            },
            "webm": {
                "format": "bestvideo{video_quality}[ext=webm]+bestaudio{audio_quality}[ext=webm]/bestvideo{video_quality}+bestaudio{audio_quality}/bestvideo[ext=webm]+bestaudio/bestvideo+bestaudio",
                "post": [{'key': 'FFmpegVideoConvertor', 'preferedformat': "webm"} if should_transcode else {'key': 'FFmpegVideoRemuxer', 'preferedformat': "webm"}],
                "is_audio": False
            },
            "ogg": {
                "format": "bestaudio{audio_quality}/bestaudio",
                "post": [{'key': 'FFmpegExtractAudio', 'preferredcodec': "vorbis", 'preferredquality': '0'}],
                "is_audio": True
            }
        }

        self.session_id = str(uuid.uuid4())
        logger.debug(f"Generated session ID: {self.session_id}")

        self.temp_dir = self._create_temp_directory("temp/downloads")
        logger.debug(f"Created temp directory: {self.temp_dir}")

        self.downloaded_filepath: Optional[Path] = None
        self._download_task: Optional[asyncio.Future] = None
        self.start_time: Optional[float] = None
        self.media_info: Optional[Dict[str, Any]] = None

        self.yt_dlp_opts = DEFAULT_YT_DLP_SETTINGS.copy()
        self.yt_dlp_opts['outtmpl'] = str(Path(self.temp_dir) / "%(title)s.%(ext)s")
        logger.debug(f"yt-dlp output template: {self.yt_dlp_opts['outtmpl']}")

        self._set_level_logging(logger.level)

    def _set_level_logging(self, level: int):
        """Set the logging level for yt_dlp. Quiet if level is not DEBUG."""
        yt_logger = logging.getLogger('yt_dlp')
        if level == logging.DEBUG:
            yt_logger.setLevel(logging.DEBUG)
            self.yt_dlp_opts['quiet'] = False
            self.yt_dlp_opts['verbose'] = True
        else:
            self.yt_dlp_opts['quiet'] = True
            self.yt_dlp_opts['verbose'] = False
        self.yt_dlp_opts['logger'] = yt_logger

    async def download(self):
        """Download the media file using yt-dlp."""
        logger.debug("Starting download task")
        loop = asyncio.get_running_loop()
        self._download_task = loop.run_in_executor(None, self._download)
        logger.debug("Download task submitted to executor")
        self.downloaded_filepath = await self._download_task
        logger.debug(f"Download task completed, file path: {self.downloaded_filepath}")
        return self

    def get_file_path(self) -> Optional[Path]:
        """Get the downloaded file path."""
        logger.debug(f"Getting file path: {self.downloaded_filepath}")
        return self.downloaded_filepath

    def get_elapsed_time(self) -> Optional[float]:
        """Get the elapsed download time."""
        elapsed = (time.time() - self.start_time) if self.start_time else None
        logger.debug(f"Elapsed time: {elapsed}s")
        return elapsed

    def get_is_audio(self) -> bool:
        """Get whether the downloaded file is audio."""
        logger.debug(f"Is audio: {self.is_audio}")
        return self.is_audio

    def get_media_info(self) -> Optional[Dict[str, Any]]:
        """Get the full metadata dictionary from yt-dlp."""
        logger.debug(f"Getting media info. Keys: {list(self.media_info.keys()) if self.media_info else 'None'}")
        return self.media_info

    def cleanup(self):
        """Remove the temporary download directory."""
        logger.debug(f"Starting cleanup for temp directory: {self.temp_dir}")
        try:
            temp_path = Path(self.temp_dir)
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
                logger.debug(f"Successfully cleaned up temp directory: {temp_path}")
            else:
                logger.debug(f"Temp directory does not exist: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory {self.temp_dir}: {e}")

    def cancel_download(self):
        """Cancel the ongoing download task and clean up temporary files."""
        logger.debug("Cancelling download task")
        if self._download_task and not self._download_task.done():
            self._download_task.cancel()
            logger.debug("Download task cancelled successfully")
        else:
            logger.debug("No active download task to cancel")
        self.cleanup()

    def _create_temp_directory(self, base_dir: str) -> Path:
        """Create a temporary directory for downloads."""
        temp_path = Path(base_dir).absolute() / self.session_id
        logger.debug(f"Creating temp directory: {temp_path}")
        temp_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Temp directory created successfully: {temp_path}")
        return temp_path

    def _resolve_format(self, ytdl_format: str) -> tuple[str, List[Dict[str, Any]]]:
        """Resolve yt_dlp format string and postprocessors based on requested format and quality."""
        logger.debug(f"Resolving format: {ytdl_format}")
        if ytdl_format not in self.FORMAT_MAP:
            logger.error(f"Unsupported format: {ytdl_format}")
            raise UnsupportedFormat(f"Invalid format specified: {ytdl_format}")

        fmt_template = self.FORMAT_MAP[ytdl_format]["format"]
        postprocessors = self.FORMAT_MAP[ytdl_format]["post"]
        self.is_audio = self.FORMAT_MAP[ytdl_format]["is_audio"]
        logger.debug(f"Format template: {fmt_template}, is_audio: {self.is_audio}")

        video_quality, audio_quality = ("", "")
        if self.quality:
            parts = self.quality.split("_")
            video_quality = parts[0] if len(parts) > 0 else ""
            audio_quality = parts[1] if len(parts) > 1 else ""
            logger.debug(f"Quality split - video: '{video_quality}', audio: '{audio_quality}'")
        
        fmt = fmt_template.format(video_quality=video_quality, audio_quality=audio_quality)
        logger.debug(f"Final format string: {fmt}")
        return fmt, postprocessors

    def _download(self) -> Optional[Path]:
        """
        Start the download process. It first fetches metadata to determine
        if the media is audio-only, corrects the format if necessary,
        and then proceeds with the download.
        """
        self.start_time = time.time()
        logger.debug(f"Starting download process at {self.start_time}")

        try:
            # 1. Fetch info without downloading
            logger.debug(f"Fetching media info for URL: {self.url}")
            info_opts = self.yt_dlp_opts.copy()
            info_opts['postprocessors'] = []  # No post-processing for info fetching

            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.media_info = info.copy()
            logger.debug("Media info fetched successfully.")

            processing_info = self.media_info.copy()
            if "entries" in processing_info and processing_info["entries"]:
                processing_info = processing_info["entries"][0]
            elif "entries" in processing_info and not processing_info["entries"]:
                raise MediaFilepathNotFound("No entries found in playlist/search results")

            is_audio_only = processing_info.get('vcodec') == 'none'
            video_formats = ['mp4', 'mkv', 'webm']
            if is_audio_only and self.format in video_formats:
                logger.warning(
                    f"Media is audio-only, but a video format ('{self.format}') was requested. "
                    f"Forcing format to 'mp3'."
                )
                self.format = 'mp3'

            result = self._attempt_download_from_info(self.media_info)
            logger.debug(f"Download completed successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Download failed: {e}")
            logger.debug(f"Download failure details: {type(e).__name__}: {e}")
            raise DownloadFailed(str(e)) from e

    def _attempt_download_from_info(self, info: Dict[str, Any]) -> Optional[Path]:
        """Downloads media using a pre-fetched info dictionary."""
        logger.debug(f"Attempting download from info with resolved format: {self.format}")
        ytdl_format, postprocessors = self._resolve_format(self.format)

        opts = self.yt_dlp_opts.copy()
        opts.update({'format': ytdl_format, 'postprocessors': postprocessors})
        logger.debug(f"yt-dlp options for processing: {opts}")

        logger.debug("Starting yt-dlp processing from info dictionary")
        with yt_dlp.YoutubeDL(opts) as ydl:
            # Use process_info to avoid re-fetching network resources
            ydl.process_info(info)
        logger.debug("yt-dlp processing completed.")

        logger.debug("Resolving downloaded file path")
        return self._resolve_downloaded_file()

    def _resolve_downloaded_file(self) -> Optional[Path]:
        """Determine the actual downloaded file from the temporary directory."""
        logger.debug(f"Resolving downloaded file from temp directory: {self.temp_dir}")
        temp_path = Path(self.temp_dir)
        if not temp_path.exists():
            logger.error(f"Temp directory does not exist: {temp_path}")
            raise MediaFilepathNotFound(f"Temp directory does not exist: {temp_path}")

        files = [f for f in temp_path.iterdir() if f.is_file()]
        logger.debug(f"Found {len(files)} files in temp directory: {[f.name for f in files]}")
        if not files:
            logger.error(f"No files found in temp directory: {temp_path}")
            raise MediaFilepathNotFound(f"No files found in temp directory: {temp_path}")

        format_files = [f for f in files if f.suffix.lower() == f".{self.format}"]
        logger.debug(f"Files matching format '.{self.format}': {[f.name for f in format_files]}")
        selected_file = max(format_files or files, key=lambda f: f.stat().st_mtime)
        logger.debug(f"Selected file: {selected_file.name} (size: {selected_file.stat().st_size} bytes)")
        return selected_file