from dataclasses import dataclass
from pathlib import Path

@dataclass
class SpeedMediaRequest:
    url: Path
    file_size: int
    max_file_size: int
    factor: float
    preserve_pitch: bool
    custom_pitch: float | None = None