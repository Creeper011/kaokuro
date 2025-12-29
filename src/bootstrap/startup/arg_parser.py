import argparse
from src.core.constants import DEFAULT_DEBUG_FLAG

class ArgParser:
    """Parse all CLI arguments"""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self._add_args()

    def _add_args(self) -> None:
        self.parser.add_argument(
            *DEFAULT_DEBUG_FLAG,
            action="store_true",
            help="Enable debug logging"
        )

    def parse_cli(self) -> argparse.Namespace:
        return self.parser.parse_args()
