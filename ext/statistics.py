import discord
import pytz
from datetime import datetime
from discord.ext import commands, tasks

from stats.client import BOT_LATENCY, BOT_UPTIME, MESSAGES, SERVER_COUNT, USER_COUNT
from util.logger import log

class Statistic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.websocket_latency.start()
        self.uptime_checker.start()
        self.calculate_user.start()
        self.up_since = datetime.now(pytz.timezone("Europe/Berlin"))

    
    @tasks.loop(minutes=1)
    async def websocket_latency(self):
        lat = self.bot.latency * 1000
        BOT_LATENCY.set(lat)
        
    @tasks.loop(minutes=5)
    async def calculate_user(self):
        count = 0
        for guild in self.bot.guilds:
            count += guild.member_count
        USER_COUNT.set(count)
    
    @tasks.loop(minutes=0.1)
    async def uptime_checker(self):
        tz = pytz.timezone("Europe/Berlin")
        uptime = (datetime.now(tz) - self.up_since).total_seconds()
        BOT_UPTIME.set(uptime)
    
    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        MESSAGES.inc(1)

    @commands.Cog.listener(name="on_guild_add")
    async def guild_add(self, guild: discord.Guild):
        SERVER_COUNT.inc(1)
        USER_COUNT.inc(guild.member_count)

    @commands.Cog.listener(name="on_guild_remove")
    async def guild_remove(self, guild: discord.Guild):
        SERVER_COUNT.dec(1)
        USER_COUNT.dec(guild.member_count)
    
async def setup(bot):
    await bot.add_cog(Statistic(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Statistic(bot))
    log.debug(f"{__name__} unloaded")