from pathlib import Path
from src.core.constants import DEFAULT_LOADERS_PATH

class LoadersFinder():
    """A class to automatically find any config loader in the loaders directory"""

    def __init__(self, loader_path: Path = DEFAULT_LOADERS_PATH) -> None:
        self.loader_path = loader_path
        
    def find_loaders(self) -> list[Path]:
        ...