from discord.ext import commands
from util.logger import log

class PrefixCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.command(name="don", aliases=["donovan", "songbird"])
    async def don_prefixcommand(self, context: commands.Context):
        await context.reply("Don ist ein cooler dude.")
        
    @commands.command(name="simplex", aliases=["simpi", "smplx"])
    async def simplex_prefixcommand(self, context: commands.Context):
        await context.reply("Simplex ist ein cooler dude.")

    @commands.command(name="juox", aliases=["juxl", "juxi"])
    async def juox_prefixcommand(self, context: commands.Context):
        await context.reply("Juox ist ein cooler dude.")
        
    @commands.command(name="adosa", aliases=["adoser", "adobsi"])
    async def adosa_prefixcommand(self, context: commands.Context):
        await context.reply("Adosa ist ein cooler dude.")
        
    @commands.command(name="nuna", aliases=["nuner"])
    async def nuna_prefixcommand(self, context: commands.Context):
        await context.reply("Nuna ist cool.")
    
async def setup(bot):
    await bot.add_cog(PrefixCommands(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(PrefixCommands(bot))
    log.debug(f"{__name__} unloaded")