import asyncio
import time
from src.commands.services.adapters.downloader.download import Downloader

class DownloaderService:
    def __init__(self, url: str, format: str, playlist: bool = False, cancel_at_seconds: int = None, max_downloads: int = None):
        self.downloader = Downloader(url, format)
        self.cancel_at_seconds = cancel_at_seconds

    async def download(self):
        start = time.time()
        try:
            result = await asyncio.wait_for(
                self.downloader.__aenter__(),
                timeout=self.cancel_at_seconds if self.cancel_at_seconds else None
            )
            elapsed = time.time() - start
            filepath = result.get_filepath()
            return filepath, elapsed
        except asyncio.TimeoutError:
            self.downloader.cancel_download()
            return None, None
        
    def cancel_download(self):
        self.downloader.cancel_download()
