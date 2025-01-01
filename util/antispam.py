import discord

from datetime import datetime

TIME_WINDOW_SECS = 3
MAX_MESSAGES = 5

cache = {}

class Antispam:
    def __init__(self):
        self.antispam_guilds = None
        
        if not cache.get("guilds"):
            cache["guilds"] = {}
            
        self.antispam_guilds = cache["guilds"]
    
    def _check(self, guild_id):
        if not self.antispam_guilds.get(guild_id):
            self.antispam_guilds[guild_id] = {
                "last_message": datetime.now(),
                "count": 0,
            }
    
    def _add_point(self, guild_id, points: int=1):
        self._check(guild_id)
        
        antispam_guild = self.antispam_guilds[guild_id]
        last_message = antispam_guild["last_message"]
        
        if (datetime.now() - last_message).seconds >= TIME_WINDOW_SECS:
            del cache["guilds"][guild_id]
        
        antispam_guild["count"] += 1
        
    async def spamming(self, message: discord.Message) -> bool:
        self._add_point(message.guild.id)                
        self._check(message.guild.id)
        if self.antispam_guilds[message.guild.id]["count"] >= MAX_MESSAGES:
            return True
        return False