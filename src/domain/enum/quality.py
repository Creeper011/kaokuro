from enum import Enum

class Quality(Enum):
    _360 = "360p"
    _480 = "480p"
    _720 = "720p"
    _1080 = "1080p"
    _1440 = "1440p"
    _2160 = "2160p"

    DEFAULT = _720