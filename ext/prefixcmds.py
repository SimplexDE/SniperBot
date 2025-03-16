from discord.ext import commands
from util.logger import log

class PrefixCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.hybrid_command(name="help")
    async def help_hybridcommand(self, context: commands.Context):
        await context.reply("For help, inspect the [GitHub Page](https://github.com/SimplexDE/SniperBot).")
    
    @commands.command(name="don", aliases=["donovan", "songbird"])
    async def don_prefixcommand(self, context: commands.Context):
        await context.reply("Don ist ein cooler dude.")
        
    @commands.command(name="simplex", aliases=["simpi", "smplx"])
    async def simplex_prefixcommand(self, context: commands.Context):
        await context.reply("Simplex ist ein cooler dude.")
    
async def setup(bot):
    await bot.add_cog(PrefixCommands(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(PrefixCommands(bot))
    log.debug(f"{__name__} unloaded")