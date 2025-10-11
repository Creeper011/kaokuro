from typing import Optional, Protocol, runtime_checkable
from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput

@runtime_checkable
class SpeedMediaProtocol(Protocol):
    def __init__(self, url: str, factor: float, preserve_pitch: bool, custom_pitch: Optional[float] = None):
        ...

    async def __aenter__(self) -> "SpeedMediaProtocol":
        ...

    async def __aexit__(self, exc_type, exc_val, tb) -> None:
        ...

    async def get_response(self) -> SpeedMediaOutput:
        """Fetches the speed response and returns a SpeedMediaOutput object."""
        ...