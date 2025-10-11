import logging
from src.domain.exceptions import InvalidSpeedRequest
from src.domain.interfaces.dto.request.speed_media_request import SpeedMediaRequest
from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput
from src.domain.interfaces.protocols.speed_media_protocol import SpeedMediaProtocol

logger = logging.getLogger(__name__)


class SpeedMediaUseCase:
    """Use case for speeding up or slowing down media files."""
    def __init__(self, service: SpeedMediaProtocol):
        self.service = service

    def _validate(self, request: SpeedMediaRequest):
        logger.debug(f"Validating speed request: {request}")
        if not request.url:
            logger.warning("Validation failed: URL is empty.")
            raise InvalidSpeedRequest("URL cannot be empty.")

        if request.file_size > request.max_file_size:
            logger.warning(f"Validation failed: File size {request.file_size} exceeds max size {request.max_file_size}.")
            raise InvalidSpeedRequest(f"File size cannot exceed {request.max_file_size}.")

        if request.factor <= 0:
            logger.warning(f"Validation failed: Speed factor {request.factor} is not positive.")
            raise InvalidSpeedRequest("Speed factor must be positive.")
        logger.debug("Speed request validation successful.")

    async def execute(self, request: SpeedMediaRequest) -> SpeedMediaOutput:
        logger.debug(f"Executing SpeedMediaUseCase with request: {request}")
        self._validate(request)

        async with self.service(request.url, request.factor, request.preserve_pitch, request.custom_pitch) as service:
            output = await service.get_response()

        logger.debug(f"SpeedMediaUseCase executed successfully, returning output: {output}")
        return output