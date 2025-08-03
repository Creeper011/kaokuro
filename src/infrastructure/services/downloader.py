import yt_dlp
import logging
import uuid
import os
import shutil
import asyncio
import glob
from src.config.settings import SettingsManager

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, url: str, format: str):
        self.url = url
        self.format = format
        self.loop = None
        self.session_id = str(uuid.uuid4())
        self.settings = SettingsManager()
        self.TEMP_DIR = self.settings.get({"Downloader": "temp_dir"})
        self.CLEAN_UP_TIME = self.settings.get({"Downloader": "cleanup_time"})
        self.temp_dir = self._create_temp_directory()
        self.downloaded_filepath = None
        self.base_yt_dlp_opts = {
            'format': 'best',
            'postprocessors': [],
            'windowsfilenames': True,
            'restrictfilenames': True,
            'outtmpl': os.path.join(self.temp_dir, "%(title)s.%(ext)s"),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'concurrent_fragment_downloads': 10,
            'external_downloader': 'aria2c',
            'external_downloader_args': {
                'default': ['-x', '16', '-s', '16', '-k', '1M']
            },
            'match_filter': yt_dlp.utils.match_filter_func("!is_live"),
        }

    async def __aenter__(self):
        self.loop = asyncio.get_event_loop()
        filepath = await self.loop.run_in_executor(None, self._download)
        self.downloaded_filepath = filepath
        return self

    def _create_temp_directory(self):
        temp_dir = os.path.join(os.getcwd(), self.TEMP_DIR, self.session_id)
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def _cleanup(self):
        """Remove temporary files and directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(self.CLEAN_UP_TIME)
        self._cleanup()

    def cancel_download(self):
        """Cancel the download process."""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self._cleanup)
        else:
            logger.warning("No active download to cancel.")
        self._cleanup()

    def _resolve_format(self, format: str):
        match format:
            case "mp4":
                fmt = "bestvideo+bestaudio"
                post = [{'key': 'FFmpegVideoRemuxer', 'preferedformat': "mp4"}]
            case "mp3":
                fmt = "bestaudio/best"
                post = [{'key': 'FFmpegExtractAudio', 'preferredcodec': "mp3", 'preferredquality': '0'}]
            case "mkv":
                fmt = "bestvideo+bestaudio"
                post = [{'key': 'FFmpegVideoRemuxer', 'preferedformat': "mkv"}]
            case "webm":
                fmt = "bestvideo+bestaudio"
                post = [{'key': 'FFmpegVideoRemuxer', 'preferedformat': "webm"}]
            case "ogg":
                fmt = "bestaudio/best"
                post = [{'key': 'FFmpegExtractAudio', 'preferredcodec': "vorbis", 'preferredquality': '0'}]
            case _:
                logger.error("error: Invalid format specified.")
                raise ValueError("Invalid format specified.")
        return fmt, post

    def _download(self):
        """Video download"""
        fmt, post = self._resolve_format(self.format)
        opts = self.base_yt_dlp_opts.copy()
        opts.update({'format': fmt, 'postprocessors': post})
    
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            filename = ydl.prepare_filename(info, outtmpl=fr"{self.temp_dir}\%(title)s.%(ext)s")

        self.downloaded_filepath = filename
        pattern = os.path.join(self.temp_dir, f"*.{self.format}")
        files = glob.glob(pattern)

        if files:
            self.downloaded_filepath = files[0]
        else:
            files = glob.glob(os.path.join(self.temp_dir, "*"))
            self.downloaded_filepath = files[0] if files else None
            
        return self.downloaded_filepath

    def get_filepath(self):
        """Returns the filepath"""
        return self.downloaded_filepath