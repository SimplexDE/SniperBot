import discord
import random

from discord.ext import commands
from datetime import datetime
from pytz import timezone

from database.mongoclient import SpongiperClient

class Starboard:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.tz: timezone = timezone("Europe/Berlin")
        self.client: SpongiperClient() = SpongiperClient(bot)
    
    def _get_random_color(self) -> discord.Colour:
        _colors = [
                discord.Color.blue(),
                discord.Color.red(),
                discord.Color.blurple(),
                discord.Color.gold(),
                discord.Color.green(),
                discord.Color.fuchsia(),
                discord.Color.yellow(),
                discord.Color.magenta(),
            ]
        return random.choice(_colors)
    
    def _get_embed(self, message: discord.Message, reaction_count: int) -> discord.Embed: 
        embed = discord.Embed(
            title="",
            description=message.content,
            timestamp=datetime.now(),
            color=self._get_random_color(),
            )
        embed.set_author(name=f"{message.author.display_name} ({message.author.name}) — {reaction_count} ⭐",
                        icon_url=message.author.avatar if message.author.avatar is not None else message.author.default_avatar,
                        url=message.jump_url)

        timestamp = message.created_at.astimezone(self.tz).strftime("%d.%m.%Y %H:%M")
        embed.set_footer(text=f"🔗 #{message.channel} — 🕒 {timestamp}")
        
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        
        return embed
    
    def _get_emoji_count(self, emoji: str, reactions: list[discord.Reaction]) -> int:
        for reaction in reactions:
            if reaction.emoji == emoji:
                return reaction.count

    async def _add_to_board(self, starboard: discord.TextChannel, message: discord.Message, stars: int):
        db_guild = await self.client.get_guild(message.guild.id)
        settings = db_guild.settings
        
        board_message = await starboard.send(embed=self._get_embed(message, stars))
        
        settings["starredMessages"][str(message.id)] = {}
        settings["starredMessages"][str(message.id)]["message_id"] = str(message.id)
        settings["starredMessages"][str(message.id)]["starMessage_id"] = str(board_message.id)
        self.bot.message_cache[message.id] = board_message
        
        db_guild.settings = settings
    
    async def _remove_from_board(self, starboard: discord.TextChannel, message: discord.Message):
        db_guild = await self.client.get_guild(message.guild.id)
        settings = db_guild.settings

        if message.id in self.bot.message_cache:
            await self.bot.message_cache[message.id].delete()
            self.bot.message_cache.pop(message.id)
            del settings["starredMessages"][str(message.id)]
            db_guild.settings = settings
            return
        
        message = await starboard.fetch_message(settings["starredMessages"][str(message.id)]["starMessage_id"])
        
        del settings["starredMessages"][str(message.id)]
        await message.delete()
        db_guild.settings = settings
    
    async def _refresh_board_message(self, starboard: discord.TextChannel, message: discord.Message, stars: int):
        if message.id in self.bot.message_cache:
            try:
                await self.bot.message_cache[message.id].edit(embed=self._get_embed(message, stars))
            except discord.NotFound:
                await self._add_to_board(starboard, message, stars)
            return
        
        db_guild = await self.client.get_guild(message.guild.id)
        settings = db_guild.settings
        
        try:
            message = await starboard.fetch_message(settings["starredMessages"][str(message.id)]["starMessage_id"])
            await message.edit(embed=self._get_embed(message, stars))
        except discord.NotFound:
            await self._add_to_board(starboard, message, stars)
        except KeyError:
            pass
    
    async def process(self, payload: discord.RawReactionActionEvent | discord.RawReactionClearEvent | discord.RawReactionClearEmojiEvent):
        db_guild = await self.client.get_guild(payload.guild_id)
        settings = db_guild.settings

        channel: discord.GuildChannel = self.bot.get_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)
        emoji = None
        action = None
        try:
            emoji: discord.PartialEmoji = payload.emoji
        
            if emoji != discord.PartialEmoji(name="⭐"):
                return

            action = payload.event_type
        except Exception:
            pass    
        
        stars = self._get_emoji_count("⭐", message.reactions)
        
        if "starboard_channel" not in settings:
            return
        
        starboard = self.bot.get_channel(settings["starboard_channel"])
        
        if starboard is None:
            return
        
        if message is None:
            return

        if "stars" not in settings:
            settings["stars"] = 3 # Default

        if "starredMessages" not in settings:
            settings["starredMessages"] = {}
        
        db_guild.settings = settings
        
        match (action):
            case ("REACTION_ADD"):
                if message.author.id == payload.user_id:
                    await message.remove_reaction("⭐", message.author)
                    return await self._refresh_board_message(starboard, message, stars)  
                if str(message.id) in settings["starredMessages"]:
                    return await self._refresh_board_message(starboard, message, stars)
                
                if stars >= settings["stars"]:                    
                    return await self._add_to_board(starboard, message, stars)
                return
            
            case ("REACTION_REMOVE"):                
                if stars is None:
                    if str(message.id) not in settings["starredMessages"]:
                        return
                    return await self._remove_from_board(starboard, message)
                
                if stars < settings["stars"]:
                    if str(message.id) not in settings["starredMessages"]:
                        return
                    return await self._remove_from_board(starboard, message)
                
                if str(message.id) in settings["starredMessages"]:
                    return await self._refresh_board_message(starboard, message, stars)
                
                if stars >= settings["stars"]:                    
                    return await self._add_to_board(starboard, message, stars)
                return
            
                
            case (_):
                if stars is None:
                    if str(message.id) not in settings["starredMessages"]:
                        return
                    return await self._remove_from_board(starboard, message)
                
                if stars < settings["stars"]:
                    if str(message.id) not in settings["starredMessages"]:
                        return
                    return await self._remove_from_board(starboard, message)
    