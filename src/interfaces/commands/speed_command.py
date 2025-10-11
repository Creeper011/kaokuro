import discord
import logging
from discord.ext import commands
from discord import app_commands

from src.domain.interfaces.dto.request.speed_media_request import SpeedMediaRequest
from src.domain.interfaces.dto.output.speed_media_output import SpeedMediaOutput
from src.domain.exceptions import InvalidSpeedRequest
from src.application.utils.error_embed import create_error
from src.application.constants import ErrorTypes

logger = logging.getLogger(__name__)

class SpeedCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="speed", description="Changes the speed of a media file.")
    @app_commands.describe(
        factor="Speed factor (e.g., 2 for 2x speed, 0.5 for half speed).",
        attachment="The video or audio file to modify.",
        preserve_pitch="Try to preserve the audio pitch."
    )
    async def speed_command(self, interaction: discord.Interaction, factor: app_commands.Range[float, 0.1, 2.0], attachment: discord.Attachment,
                            preserve_pitch: bool = False):
        await interaction.response.defer(thinking=True)
        result: SpeedMediaOutput = None
        try:
            logger.debug(f"Speed command received from user: {interaction.user.name} ({interaction.user.id}) with factor: {factor}, attachment: {attachment.filename}, preserve_pitch: {preserve_pitch}")
            max_file_size = 100 * 1024 * 1024

            use_case = self.bot.container.build_speed_media_usecase()

            speed_request = SpeedMediaRequest(
                url=attachment.url,
                file_size=attachment.size,
                factor=factor,
                preserve_pitch=preserve_pitch,
                max_file_size=max_file_size
            )
            logger.debug(f"Speed request created: {speed_request}")

            result = await use_case.execute(speed_request)
            logger.debug(f"Speed use case executed with result: {result}")

            file = discord.File(result.file_path, filename=attachment.filename)
            
            await interaction.followup.send("Sending file...")

            if result.metadata_preserved:
                message = f"Speed Concluded: Elapsed: {result.elapsed:.2f}s (metadata preserved)"
            else:
                message = f"Speed Concluded: Elapsed: {result.elapsed:.2f}s (metadata not preserved)"

            await interaction.edit_original_response(content=message, attachments=[file])

        except InvalidSpeedRequest as e:
            logger.warning(f"Invalid speed request: {e}")
            error_embed = create_error(
                error="Invalid request for speed modification.",
                type=ErrorTypes.INVALID_INPUT,
                note=str(e)
            )
            await interaction.followup.send(embed=error_embed)
        
        except Exception as e:
            logger.error("An unexpected error occurred in the speed command.", exc_info=True)
            error_embed = create_error(
                error="An unexpected error occurred.",
                type=ErrorTypes.UNKNOWN,
                note="Please contact support if the issue persists."
            )
            await interaction.followup.send(embed=error_embed)

        finally:
            if result and result.cleanup:
                logger.debug(f"Cleaning up file: {result.file_path}")
                result.cleanup()
            elif result:
                logger.warning(f"No cleanup method found for result: {result}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SpeedCommand(bot))
