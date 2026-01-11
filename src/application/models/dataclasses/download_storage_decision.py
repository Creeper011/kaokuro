from dataclasses import dataclass
from pathlib import Path
from src.domain.enum.download_destination import DownloadDestination

@dataclass
class DownloadStorageDecision():
    destination: DownloadDestination
