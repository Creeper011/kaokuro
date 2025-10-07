import io
import discord
from discord.ext import commands

class Logs(commands.Cog):
    """A cog for handling bot logs."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_file_path = "logs/bot.log"

    @commands.command(name="logs")
    @commands.is_owner()
    async def logs_command(self, ctx: commands.Context, *args):
        """Displays log files with flexible filtering for lines and level.

        Usage:
        !logs [lines] [level]
        Examples:
        !logs 100 ERROR
        !logs DEBUG 200
        !logs 50
        !logs INFO
        """
        await ctx.defer()

        # Default values
        lines = 50
        level = None

        # Parse arguments flexibly
        for arg in args:
            if arg.isdigit():
                lines = int(arg)
            elif arg.isalpha():
                level = arg.upper()

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            
            # Filter by level if provided
            if level:
                log_lines = [line for line in log_lines if f"[{level}]" in line]

            # Get the last N lines
            log_lines = log_lines[-lines:]

            if not log_lines:
                await ctx.send("No logs found with the specified filters.")
                return

            # Create a text file in memory
            log_content = "".join(log_lines)
            log_file = io.BytesIO(log_content.encode('utf-8'))
            log_file.seek(0)

            await ctx.send(f"Displaying last {len(log_lines)} lines (filtered by level: {level or 'None'}).", file=discord.File(log_file, filename="bot_logs.txt"))

        except FileNotFoundError:
            await ctx.send("Log file not found.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
