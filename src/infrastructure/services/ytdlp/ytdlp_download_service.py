import yt_dlp
import asyncio
from pathlib import Path
from logging import Logger
from typing import Any, Dict
from src.core.constants import DEFAULT_YT_DLP_SETTINGS

class YtdlpDownloadService:
    """Service for downloading files using yt-dlp."""

    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.logger.info("YtdlpDownloadService initialized")

    def _get_ydl_opts(self, output_folder: Path) -> Dict[str, Any]:
        """
        Get yt-dlp options for downloading.
        
        Args:
            output_folder: Folder where the file will be downloaded
            
        Returns:
            Dictionary with yt-dlp options
        """
        return {
            'outtmpl': str(output_folder / '%(title)s.%(ext)s'),
            **DEFAULT_YT_DLP_SETTINGS,
            'logger': self.logger,
        }

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Hook to log download progress.
        
        Args:
            d: Dictionary containing progress information
        """
        ...

    async def download(self, url: str, output_folder: Path) -> Path:
        """
        Download file from URL using yt-dlp.
        
        Args:
            url: URL to download from
            output_folder: Folder where the file will be saved
            
        Returns:
            Path to the downloaded file
            
        Raises:
            Exception: If download fails
        """
        loop = asyncio.get_running_loop()
        self._download_task = loop.run_in_executor(None, self._download_sync, url, output_folder)
        return await self._download_task
    
    def _download_sync(self, url: str, output_folder: Path) -> Path:
        self.logger.info(f"Starting download from: {url}")
        
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created output folder: {output_folder}")

        ydl_opts = self._get_ydl_opts(output_folder)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
               
                info = ydl.extract_info(url, download=True)
                
                if info is None:
                    raise ValueError("Failed to extract video information")
                
                filename = ydl.prepare_filename(info)
                file_path = Path(filename)
                
                if not file_path.exists():
                    raise FileNotFoundError(f"Downloaded file not found at: {file_path}")
                
                self.logger.info(f"Successfully downloaded file to: {file_path}")
                return file_path
                
        except yt_dlp.DownloadError as error:
            self.logger.error(f"yt-dlp download error: {error}", exc_info=True)
            raise Exception(f"Failed to download from {url}: {error}") from error
            
        except Exception as error:
            self.logger.error(f"Unexpected error during download: {error}", exc_info=True)
            raise