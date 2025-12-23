import argparse

class ArgParser:
    """Parse all CLI arguments"""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self._add_args()

    def _add_args(self) -> None:
        self.parser.add_argument(
            "-d", "--debug",
            action="store_true",
            help="Enable debug logging"
        )

    def parse(self) -> argparse.Namespace:
        return self.parser.parse_args()
