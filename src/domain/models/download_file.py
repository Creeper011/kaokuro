from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DownloadedFile:
    file_path: Path
    file_size: int