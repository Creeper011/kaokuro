import logging
import discord
import validators
import os
from discord.ext import commands
from discord import app_commands
from src.commands.services.downloaderService import DownloaderService
from src.commands.services.adapters.utils.drive import Drive
from trashbin.create_error import create_error, ErrorTypes

logger = logging.getLogger(__name__)

class DownloadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.drive = Drive("")
        self.FILE_SIZE_LIMIT = 120 * 1024 * 1024  # 120 MB

    @app_commands.command(name="download", description="Download from multiple sites")
    @app_commands.choices(
        format=[
            app_commands.Choice(name="mp4", value="mp4"),
            app_commands.Choice(name="mp3", value="mp3"),
            app_commands.Choice(name="mkv", value="mkv"),
            app_commands.Choice(name="webm", value="webm"),
            app_commands.Choice(name="ogg", value="ogg"),
        ]
    )
    @app_commands.describe(url="A query or a url (Playlist not supported)",  format="The format to download")
    async def download(self, interaction: discord.Interaction, url: str, format: app_commands.Choice[str] = "mp4"):
        await interaction.response.defer()

        if not validators.url(url):
            url = f"ytsearch:{url}"

        if isinstance(format, app_commands.Choice):
            format = format.value
        
        try:
            downloader_service = DownloaderService(url, format, cancel_at_seconds=240)
            file_path, elapsed = await downloader_service.download()

            if not file_path or elapsed is None:
                await interaction.followup.send("Download has been cancelled.")
                return

            logger.info(f"File downloaded to: {file_path}")
            if not os.path.exists(file_path):
                await interaction.followup.send(embed=create_error(error="Download failed: File not found.", 
                                                                   type=ErrorTypes.FILE_NOT_FOUND))
                return

            if os.path.getsize(file_path) > self.FILE_SIZE_LIMIT:
                link = await self.drive.upload(file_path)
                await interaction.followup.send(f"File is too large. Download link: {link}")
                return
            
            await interaction.followup.send("Sending file...")
            file = discord.File(file_path, filename=os.path.basename(file_path))
            file_size = os.path.getsize(file_path)
            try:
                await interaction.edit_original_response(content=f"Download completed! {elapsed:.2f} seconds elapsed, {file_size / (1024 * 1024):.2f}mb.", attachments=[file])
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                await interaction.followup.send(f"Download completed! {elapsed:.2f} seconds elapsed, {file_size / (1024 * 1024):.2f}mb.", file=file)

        except Exception as error:
            await interaction.followup.send(embed=create_error(error="Download failed", code=str(error), 
                                                               type=ErrorTypes.UNKNOWN))

async def setup(bot: commands.Bot):
    """Load the Download cog."""
    await bot.add_cog(DownloadCog(bot))