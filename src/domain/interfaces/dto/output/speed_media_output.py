from dataclasses import dataclass
from pathlib import Path
from typing import Callable

@dataclass
class SpeedMediaOutput:
    file_path: Path = None
    metadata_preserved: bool = None
    elapsed: float = None
    cleanup: Callable = None