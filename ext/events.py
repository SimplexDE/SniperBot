import discord
import random
import os
import pytz
from discord.ext import commands
from util.antispam import Antispam
from util.starboard import Starboard
from database.mongoclient import SpongiperClient

from util.quote import Quote
from util.embed import Embed
from util.logger import log
from ext.developer import blocklist
from util.constants import COLORS, ATTACHMENTS_SRC, Emote

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.starboard: Starboard = Starboard(bot)
        self.client: SpongiperClient = SpongiperClient(bot)
        self.last_message = {}
        self.last_sent_from_bot = {}
        self.last_sent = {}
        self.blocklist = blocklist
        
    @commands.Cog.listener(name="on_message")
    async def snipe(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.guild is None:
            return
    
        if message.author.id in self.blocklist:
            return
        
        if not self.last_message.get(message.guild.id):
            self.last_message[message.guild.id] = {}
        
        if self.last_message[message.guild.id] is None:
            return
        
        if not self.last_message[message.guild.id].get(message.channel.id):
            self.last_message[message.guild.id][message.channel.id] = None
        
        if self.last_message[message.guild.id][message.channel.id] is None:
            return
        
        if len(message.content) != 1:
            return
            
        content = message.content.lower()
        
        if content[0] != "s":
            return
        
        if await Antispam().spamming(message):
            return
        
        reuse = False
        
        if not self.last_sent.get(message.guild.id):
            self.last_sent[message.guild.id] = {}
            
        if not self.last_sent[message.guild.id].get(message.channel.id):
            self.last_sent[message.guild.id][message.channel.id] = None
            
        if not self.last_sent_from_bot.get(message.guild.id):
            self.last_sent_from_bot[message.guild.id] = {}
            
        if not self.last_sent_from_bot[message.guild.id].get(message.channel.id):
            self.last_sent_from_bot[message.guild.id][message.channel.id] = None
            
        if self.last_message[message.guild.id][message.channel.id] == self.last_sent[message.guild.id][message.channel.id]:
            reuse = True
        self.last_sent[message.guild.id][message.channel.id] = self.last_message[message.guild.id][message.channel.id]
        
        tz = pytz.timezone("Europe/Berlin")
        timestamp = self.last_message[message.guild.id][message.channel.id].created_at.astimezone(tz).strftime("%d.%m.%Y %H:%M")
        author = f"📸 {self.last_message[message.guild.id][message.channel.id].author.global_name}"
        author_url = self.last_message[message.guild.id][message.channel.id].author.avatar if self.last_message[message.guild.id][message.channel.id].author.avatar is not None else self.last_message[message.guild.id][message.channel.id].author.default_avatar
        desc = f"> {self.last_message[message.guild.id][message.channel.id].content}" if len(self.last_message[message.guild.id][message.channel.id].content) != 0 else ""
        footer = f"🔗 #{self.last_message[message.guild.id][message.channel.id].channel.name} — 🕒 {timestamp}"
        color = random.choice(COLORS)
        
        embed = Embed(title=author, description=desc, color=color, title_icon_url=author_url, footer=footer)
        
        embeds = [embed.StandardEmbed()]
        files = []
        i = 0
        
        if not reuse:
            if os.listdir(f"{ATTACHMENTS_SRC}/{message.guild.id}/{message.channel.id}") is None:
                pass
            else:
                for f in os.listdir(f"{ATTACHMENTS_SRC}/{message.guild.id}/{message.channel.id}"):
                    if i == 0:
                        embeds.pop(0)
                        embed.image_url = f"attachment://{f}"
                        embeds.append(embed.BigEmbed())
                    
                    embed_n = Embed(title=author, color=color, title_icon_url=author_url, footer=footer, image_url=f"attachment://{f}")
                    
                    if i != 0:
                        embeds.append(embed_n.BigEmbed())
                    files.append(discord.File(f"{ATTACHMENTS_SRC}/{message.guild.id}/{message.channel.id}/{f}"))
                    i += 1
                
        if reuse:
            embed_urls = [embed.image.url for embed in self.last_sent_from_bot[message.guild.id][message.channel.id].embeds]
            for url in embed_urls:
                if i == 0:
                    embeds.pop(0)
                    embed.image_url = url
                    embeds.append(embed.BigEmbed())
                
                embed_n = Embed(title=author, color=color, title_icon_url=author_url, footer=footer, image_url=url)
                
                if i != 0:
                    embeds.append(embed_n.BigEmbed())
                i += 1
                
        self.last_sent_from_bot[message.guild.id][message.channel.id] = await message.channel.send(embeds=embeds, files=files if reuse is False else None)
        
    @commands.Cog.listener(name="on_message_delete")
    async def save(self, message: discord.Message):
        if self.bot.user.id == message.author.id:
            return
        
        if message.author.id in self.blocklist:
            return
        
        if message.guild is None:
            return
        
        if len(message.embeds) != 0:
            return
                
        if not os.path.exists(ATTACHMENTS_SRC):
            os.mkdir(ATTACHMENTS_SRC)
            
        if not os.path.exists("{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id))):
            os.mkdir("{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id)))
            
        if not os.path.exists("{}/{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id), str(message.channel.id))):
            os.mkdir("{}/{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id), str(message.channel.id)))
        
        for f in os.listdir(f"{ATTACHMENTS_SRC}/{str(message.guild.id)}/{str(message.channel.id)}"):
            os.remove(f"{ATTACHMENTS_SRC}/{str(message.guild.id)}/{str(message.channel.id)}/{f}")
        
        if message.attachments:
            i = 1
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(image_exts)):
                    _, extension = os.path.splitext(attachment.filename)
                    await attachment.save(fp="{}/{}/{}/{}{}".format(ATTACHMENTS_SRC, str(message.guild.id), str(message.channel.id), i, extension))
                i += 1
        
        if not self.last_message.get(message.guild.id):
            self.last_message[message.guild.id] = {}
            
        if not self.last_message[message.guild.id].get(message.channel.id):
            self.last_message[message.guild.id][message.channel.id] = None

        self.last_message[message.guild.id][message.channel.id] = message
        
    @commands.Cog.listener(name="on_raw_message_delete")
    async def save_raw(self, payload: discord.RawMessageDeleteEvent):
        
        message = None

        if payload.cached_message is not None:
            return        
        
        channel = await self.bot.fetch_channel(payload.channel_id)
        
        if not self.bot.message_cache.get(channel.id):
            return
        
        for msg in self.bot.message_cache[channel.id]:
            if msg.id == payload.message_id:
                message = msg
                break
        
        if message is None:
            return
            
        if self.bot.user.id == message.author.id:
            return
        
        if message.guild is None:
            return
        
        if len(message.embeds) != 0:
            return
                
        if not os.path.exists(ATTACHMENTS_SRC):
            os.mkdir(ATTACHMENTS_SRC)
            
        if not os.path.exists("{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id))):
            os.mkdir("{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id)))
            
        if not os.path.exists("{}/{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id), str(message.channel.id))):
            os.mkdir("{}/{}/{}".format(ATTACHMENTS_SRC, str(message.guild.id), str(message.channel.id)))
        
        for f in os.listdir(f"{ATTACHMENTS_SRC}/{str(message.guild.id)}/{str(message.channel.id)}"):
            os.remove(f"{ATTACHMENTS_SRC}/{str(message.guild.id)}/{str(message.channel.id)}/{f}")
        
        if message.attachments:
            i = 1
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(image_exts)):
                    _, extension = os.path.splitext(attachment.filename)
                    await attachment.save(fp="{}/{}/{}/{}{}".format(ATTACHMENTS_SRC, str(message.guild.id), str(message.channel.id), i, extension))
                i += 1
        
        if not self.last_message.get(message.guild.id):
            self.last_message[message.guild.id] = {}
            
        if not self.last_message[message.guild.id].get(message.channel.id):
            self.last_message[message.guild.id][message.channel.id] = None

        self.last_message[message.guild.id][message.channel.id] = message
    
    @commands.Cog.listener(name="on_message")
    async def make_that_a_quote(self, message: discord.Message):
        mentions = message.mentions
        
        if self.bot.user in mentions:
            if message.type != discord.MessageType.reply:
                await message.reply("> :warning: Ohne Nachricht, kein Zitat :person_shrugging:", allowed_mentions=None, delete_after=5)
                return
            
            if message.channel.is_nsfw():
                db_guild = await self.client.get_guild(message.guild.id)
                settings = db_guild.settings
                
                if "nsfw_allow" not in settings:
                    settings["nsfw_allow"] = False
                    db_guild.settings = settings
                
                if not settings["nsfw_allow"]:
                    await message.reply(f"> {Emote.NSFW} NSFW Content ist nicht erlaubt. (`/nsfw`)", allowed_mentions=None, delete_after=5)
                    return
            
            ref: discord.MessageReference = message.reference
            
            if not ref.cached_message:
                try:
                    msg = await message.channel.fetch_message(ref.message_id)
                except discord.NotFound:
                    return
            else:
                msg = ref.cached_message
                
            if msg.author.bot:
                await message.reply("> :warning: Roboter zitiert man nicht! :robot:", allowed_mentions=None, delete_after=5)
                return
            
            origin = await message.reply("Wird generiert...")
            attachment = await Quote(message=msg).create()
            
            tz = pytz.timezone("Europe/Berlin")
            timestamp = msg.created_at.astimezone(tz).strftime("%d.%m.%Y %H:%M")
            author = f"📜 {msg.author.display_name}"
            desc = f"> {msg.content}" if len(msg.content) != 0 else ""
            footer = f"🔗 #{msg.channel.name} — 🕒 {timestamp}"
            
            embed = Embed(title=author, 
                        title_icon_url=msg.author.avatar if msg.author.avatar is not None else msg.author.default_avatar,
                        title_url=msg.jump_url,
                        description=desc, 
                        footer=footer,
                        image_url="attachment://out.png",
                        color=random.choice(COLORS))
            
            db_guild = await self.client.get_guild(message.guild.id)
            settings = db_guild.settings

            channel = message.channel

            if "quote_channel" in settings:
                channel = self.bot.get_channel(settings["quote_channel"])
            
            await origin.delete(delay=1)
            quote = await channel.send(embed=embed.BigEmbed(), allowed_mentions=None, file=attachment)
            await message.reply(f"Zitat erstellt: {quote.jump_url}", silent=True, delete_after=5)
            
    @commands.Cog.listener(name="on_raw_reaction_add")
    async def star_added_raw(self, payload: discord.RawReactionActionEvent):
        await self.starboard.process(payload)
    
    @commands.Cog.listener(name="on_raw_reaction_remove")
    async def star_remove_raw(self, payload: discord.RawReactionActionEvent):
        await self.starboard.process(payload)
        
    @commands.Cog.listener(name="on_raw_reaction_clear")
    async def star_clear_raw(self, payload: discord.RawReactionActionEvent):
        await self.starboard.process(payload)
        
    @commands.Cog.listener(name="on_raw_reaction_clear_emoji")
    async def star_clear_emoji_raw(self, payload: discord.RawReactionActionEvent):
        await self.starboard.process(payload)
        
    @commands.Cog.listener(name="on_guild_remove")
    async def guild_remove(self, guild: discord.Guild):
        self.client.delete_guild(guild.id)
    
async def setup(bot):
    await bot.add_cog(Events(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    log.debug(f"{__name__} unloaded")