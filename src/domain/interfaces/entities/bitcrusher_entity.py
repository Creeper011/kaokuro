
from dataclasses import dataclass
from pathlib import Path

@dataclass
class BitCrushResult():
    file_path: Path = None
    drive_link: str = None
    elapsed: float = None