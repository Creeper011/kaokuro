from discord.ext import commands
from infrastructure.bot.load_extensions import ExtensionLoader
from trashbin.create_error import ErrorTypes, create_error

class DynamicCogs(commands.Cog):
    """Cog for dynamically loading, unloading, and reloading extensions."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.extensionloader = ExtensionLoader(self.bot)

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload_command(self, ctx, extension_name: str) -> None:
        """Unload a specified extension.
        Args:
            ctx: The context of the command.
            extension_name (str): The name of the extension to unload.
        """
        try:
            extension = await self.extensionloader.find_extension(extension_name)
            if extension in self.bot.extensions:
                await self.bot.unload_extension(extension)
                await ctx.send(f"Extension {extension_name} unloaded.")
            else:
                await ctx.send(embed=create_error(error="Extension not found or not loaded", 
                                                  type=ErrorTypes.EXTENSION_NOT_FOUND))
        except Exception as e:
            await ctx.send(embed=create_error(error="Error when unload extension", code=str(e), 
                                              type=ErrorTypes.EXTENSION_UNLOAD_ERROR))

    @commands.command(name="load")
    @commands.is_owner()
    async def load_command(self, ctx, extension_name: str) -> None:
        """Load a specified extension.
        Args:
            ctx: The context of the command.
            extension_name (str): The name of the extension to load.
        """
        try:
            extension = await self.extensionloader.find_extension(extension_name)
            if extension and extension not in self.bot.extensions:
                await self.bot.load_extension(extension)
                await ctx.send(f"Extension {extension_name} loaded.")
        except Exception as e:
            await ctx.send(embed=create_error(error="Error when load extension", code=str(e), 
                                              type=ErrorTypes.EXTENSION_LOAD_ERROR))

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_command(self, ctx, extension_name: str) -> None:
        """Reload a specified extension.
        Args:
            ctx: The context of the command.
            extension_name (str): The name of the extension to reload.
        """
        try:
            extension = await self.extensionloader.find_extension(extension_name)
            if extension and extension in self.bot.extensions:
                await self.bot.reload_extension(extension)
                await ctx.send(f"Extension {extension_name} reloaded.")
            else:
                await ctx.send(embed=create_error(error="Extension not found or not loaded", 
                                                  type=ErrorTypes.EXTENSION_NOT_FOUND))
        except Exception as e:
            await ctx.send(embed=create_error(error="Error when reload extension", code=str(e), 
                                              type=ErrorTypes.EXTENSION_RELOAD_ERROR))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DynamicCogs(bot))
