import discord

from datetime import datetime

TIME_WINDOW_SECS = 2
MAX_MESSAGES = 3

cache = {}

class Antispam:
    def __init__(self):
        self.antispam_guilds = None
        self.BLOCK_COMMANDS = False
        
        if not cache.get("guilds"):
            cache["guilds"] = {}
            
        self.antispam_guilds = cache["guilds"]
    
    def _add_point(self, guild_id, points: int=1):
        if not self.antispam_guilds.get(guild_id):
            self.antispam_guilds[guild_id] = {
                "last_message": datetime.now(),
                "messages": 0,
            }
        
        antispam_guild = self.antispam_guilds[guild_id]
        last_message = antispam_guild["last_message"]
        messages = antispam_guild["messages"]

        if messages >= MAX_MESSAGES:
            self.BLOCK_COMMANDS = True

        if (datetime.now() - last_message).seconds >= TIME_WINDOW_SECS:
            self.BLOCK_COMMANDS = False
            del cache["guilds"][guild_id]
            return
        
        self.antispam_guilds[guild_id]["last_message"] = datetime.now()
        antispam_guild["messages"] += 1
    
    async def spamming(self, message: discord.Message) -> bool:
        self._add_point(message.guild.id)
        return self.BLOCK_COMMANDS