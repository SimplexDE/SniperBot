from discord.ext import commands
from util.logger import log

class PrefixCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.command(name="help")
    async def help_prefixcommand(self, context: commands.Context):
        await context.reply("¯\\_(ツ)_/¯")
    
async def setup(bot):
    await bot.add_cog(PrefixCommands(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(PrefixCommands(bot))
    log.debug(f"{__name__} unloaded")