from enum import Enum

class DownloadDestination(Enum):
    """
    Enum to specify the intended storage destination for a downloaded file.
    """
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
