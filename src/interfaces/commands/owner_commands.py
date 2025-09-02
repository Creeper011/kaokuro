import discord
from discord.ext import commands
from discord import app_commands
from src.infrastructure.services.drive_loader import DriveLoader
from src.application.utils.error_embed import create_error
from src.application.constants import ErrorTypes

class OwnerCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="cleanup_drive", description="Cleanup all files from drive")
    async def cleanup_drive(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        drive = DriveLoader().get_drive()
        try: 
            await drive.deleteAllFiles()
            await interaction.followup.send("Drive cleaned up")
        except Exception as e:
            await interaction.followup.send(embed=create_error(error=str(e), type=ErrorTypes.UNKNOWN))

async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCommands(bot))