from dataclasses import dataclass
from typing import Optional

@dataclass
class DownloadResult:
    filepath: Optional[str] = None
    link: Optional[str] = None
    file_size: Optional[int] = None
    elapsed: Optional[float] = None