from typing import Protocol, Dict, Any
from pathlib import Path
from logging import Logger

class ConfigLoader(Protocol):
    """Protocol for configuration loaders."""
    def __init__(self, logger: Logger, config_path: Path | None = None) -> None:
        ...

    def load(self) -> Dict[str, Any]:
        ...