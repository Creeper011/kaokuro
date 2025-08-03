import asyncio
import os
import time
import logging
from typing import Optional, Tuple
from src.infrastructure.services.downloader import Downloader
from src.infrastructure.services.drive import Drive
from src.domain.entities import DownloadResult
from src.infrastructure.constants.result import Result

logger = logging.getLogger(__name__)

class DownloaderService:
    def __init__(self, url: str, format: str, cancel_at_seconds: int = None, max_file_size: int = 120 * 1024 * 1024):
        self.downloader = Downloader(url, format)
        self.max_file_size = max_file_size
        self.cancel_at_seconds = cancel_at_seconds
        self.drive = Drive("")

    async def download(self) -> Tuple[DownloadResult, Result]:
        start = time.time()
        try:
            result = await asyncio.wait_for(
                self.downloader.__aenter__(),
                timeout=self.cancel_at_seconds if self.cancel_at_seconds else None
            )
            elapsed = time.time() - start
            filepath = result.get_filepath()

            download_result, result = self._resolve_filepath(filepath, elapsed)
            return download_result, result
        
        except asyncio.TimeoutError:
            self.downloader.cancel_download()
            return None, None
        except Exception as error:
            logger.error(f"Download error: {error}")
            elapsed = time.time() - start
            download_result = DownloadResult()
            download_result.elapsed = elapsed
            return download_result, Result.failure(error=str(error))
        
    def _resolve_filepath(self, file_path: str, elapsed: float) -> Tuple[DownloadResult, Result]:
        if not os.path.exists(file_path):
            raise FileNotFoundError("File does not exist")

        download_result = DownloadResult()
        download_result.elapsed = elapsed
        download_result.file_size = os.path.getsize(file_path)

        if download_result.file_size > self.max_file_size:
            try:
                download_result.link = self.drive.uploadToDrive(file_path)
                result = Result.success()
                return download_result, result
            
            except Exception as error:
                logger.error(f"Error uploading to Drive: {str(error)}")
                # Fallback to file path if drive upload fails
                download_result.filepath = file_path
                result = Result.success()
                return download_result, result
        else:
            download_result.filepath = file_path
            result = Result.success()
            return download_result, result
                

    def cancel_download(self):
        self.downloader.cancel_download()
