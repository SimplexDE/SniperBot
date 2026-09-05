import discord
import random
import os
import pytz
import datetime
import asyncio
import re
import secrets
from types import SimpleNamespace
from discord.ext import commands
from util.antispam import Antispam
from util.starboard import Starboard
from database.mongoclient import SpongiperClient
from database.message_history import MessageHistory

from stats.client import MESSAGES_SNIPED
from util.quote import Quote
from util.embed import Embed
from util.logger import log
from ext.developer import get_blocklist
from util.constants import COLORS, ATTACHMENTS_SRC, Emote

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]

LAURA_PATTERN = re.compile(r'\blaura\b')
AURA_PATTERN = re.compile(r'\baura\b')
SOMEONE_PATTERN = re.compile(r'(@someone)')

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.starboard: Starboard = Starboard(bot)
        self.client: SpongiperClient = SpongiperClient(bot)
        self.message_history: MessageHistory = MessageHistory()
        self.last_message = {}
        self.last_sent_from_bot = {}
        self.last_sent = {}
        self.scheduled = False

    @commands.Cog.listener(name="on_message")
    async def remember_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id or message.guild is None:
            return

        self.message_history.remember(message)

    @commands.Cog.listener(name="on_message")
    async def horse(self, message: discord.Message):
        
        if message.author.bot:
            return
        
        if secrets.randbelow(10000) < 20:
            keywords = ["Horse", "Tomate"]
            
            await message.channel.send(random.choice(keywords))
    
    @commands.Cog.listener(name="on_member_update")
    async def anti_nick(self, before: discord.Member, after: discord.Member):
        if before.guild.id != 1247839863408164868:
            return
        if before.id != 579111799794958377:
            return
        if before.nick == after.nick:
            return
        if after.nick is None:
            return

        beforeNick = before.nick

        async for entry in after.guild.audit_logs(
            action=discord.AuditLogAction.member_update, limit=5
        ):
            if entry.target.id != after.id:
                continue
            if entry.user.id == 579111799794958377 or entry.user.bot:
                return
            break

        await after.edit(nick=beforeNick)
    
    @commands.Cog.listener(name="on_message")
    async def laura_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.lower()

        laura_count = len(LAURA_PATTERN.findall(content))
        aura_count = len(AURA_PATTERN.findall(content))

        if laura_count > 0:
            await message.reply(" ".join(["Aura"] * laura_count))

        if aura_count > 0:
            await message.reply(" ".join(["Laura"] * aura_count))
        
    @commands.Cog.listener(name="on_message")
    async def snipe(self, message: discord.Message):
        content = message.content.lower()
        
        if message.author.bot \
        or message.guild is None \
        or message.author.id in get_blocklist() \
        or len(message.content) != 1:
            return
        
        if content[0] != "s":
            return

        guild_id = message.guild.id
        channel_id = message.channel.id

        if not self.last_message.get(guild_id):
            self.last_message[guild_id] = {}

        if self.last_message[guild_id] is None:
            return

        if not self.last_message[guild_id].get(channel_id):
            self.last_message[guild_id][channel_id] = None

        last = self.last_message[guild_id][channel_id]

        if last is None:
            return

        if await Antispam().spamming(message):
            return

        reuse = False

        if not self.last_sent.get(guild_id):
            self.last_sent[guild_id] = {}

        if not self.last_sent[guild_id].get(channel_id):
            self.last_sent[guild_id][channel_id] = None

        if not self.last_sent_from_bot.get(guild_id):
            self.last_sent_from_bot[guild_id] = {}

        if not self.last_sent_from_bot[guild_id].get(channel_id):
            self.last_sent_from_bot[guild_id][channel_id] = None

        if last == self.last_sent[guild_id][channel_id]:
            reuse = True
        self.last_sent[guild_id][channel_id] = last

        tz = pytz.timezone("Europe/Berlin")
        timestamp = last.created_at.astimezone(tz).strftime("%d.%m.%Y %H:%M")
        author = f"📸 {last.author.global_name}"
        author_url = last.author.avatar if last.author.avatar is not None else last.author.default_avatar
        desc = f"> {last.content}" if len(last.content) != 0 else ""
        footer = f"🔗 #{last.channel.name} — 🕒 {timestamp}"
        color = random.choice(COLORS)

        embed = Embed(title=author, description=desc, color=color, title_icon_url=author_url, footer=footer)

        embeds = [embed.StandardEmbed()]
        files = []
        i = 0

        if not reuse:
            if os.listdir(f"{ATTACHMENTS_SRC}/{guild_id}/{channel_id}") is None:
                pass
            else:
                for f in os.listdir(f"{ATTACHMENTS_SRC}/{guild_id}/{channel_id}"):
                    if i == 0:
                        embeds.pop(0)
                        embed.image_url = f"attachment://{f}"
                        embeds.append(embed.BigEmbed())

                    embed_n = Embed(title=author, color=color, title_icon_url=author_url, footer=footer, image_url=f"attachment://{f}")

                    if i != 0:
                        embeds.append(embed_n.BigEmbed())
                    files.append(discord.File(f"{ATTACHMENTS_SRC}/{guild_id}/{channel_id}/{f}"))
                    i += 1

        if reuse:
            embed_urls = [embed.image.url for embed in self.last_sent_from_bot[guild_id][channel_id].embeds]
            for url in embed_urls:
                if i == 0:
                    embeds.pop(0)
                    embed.image_url = url
                    embeds.append(embed.BigEmbed())

                embed_n = Embed(title=author, color=color, title_icon_url=author_url, footer=footer, image_url=url)

                if i != 0:
                    embeds.append(embed_n.BigEmbed())
                i += 1

        MESSAGES_SNIPED.inc(1)
        self.last_sent_from_bot[guild_id][channel_id] = await message.channel.send(embeds=embeds, files=files if reuse is False else None)
        
    async def _persist_attachments(self, message: discord.Message):
        guild_dir = f"{ATTACHMENTS_SRC}/{message.guild.id}"
        channel_dir = f"{guild_dir}/{message.channel.id}"

        if not os.path.exists(ATTACHMENTS_SRC):
            os.mkdir(ATTACHMENTS_SRC)

        if not os.path.exists(guild_dir):
            os.mkdir(guild_dir)

        if not os.path.exists(channel_dir):
            os.mkdir(channel_dir)

        for f in os.listdir(channel_dir):
            os.remove(f"{channel_dir}/{f}")

        if message.attachments:
            i = 1
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(image_exts)):
                    _, extension = os.path.splitext(attachment.filename)
                    await attachment.save(fp=f"{channel_dir}/{i}{extension}")
                i += 1

    async def _message_from_history(self, doc: dict):
        try:
            channel = self.bot.get_channel(doc["channel_id"]) or await self.bot.fetch_channel(doc["channel_id"])
        except discord.HTTPException:
            return None

        author = self.bot.get_user(doc["author_id"])
        if author is None:
            try:
                author = await self.bot.fetch_user(doc["author_id"])
            except discord.HTTPException:
                return None

        return SimpleNamespace(
            id=doc["_id"],
            content=doc["content"],
            created_at=discord.utils.snowflake_time(doc["_id"]),
            author=author,
            channel=channel,
            guild=channel.guild,
            attachments=[],
        )

    def _remember_last_message(self, message: discord.Message):
        if not self.last_message.get(message.guild.id):
            self.last_message[message.guild.id] = {}

        if not self.last_message[message.guild.id].get(message.channel.id):
            self.last_message[message.guild.id][message.channel.id] = None

        self.last_message[message.guild.id][message.channel.id] = message

    @commands.Cog.listener(name="on_message_delete")
    async def save(self, message: discord.Message):
        if self.bot.user.id == message.author.id \
        or message.guild is None \
        or len(message.embeds) != 0:
            return

        await self._persist_attachments(message)
        self._remember_last_message(message)

    @commands.Cog.listener(name="on_raw_message_delete")
    async def save_raw(self, payload: discord.RawMessageDeleteEvent):

        if payload.cached_message is not None:
            return

        doc = self.message_history.get(payload.message_id)

        if doc is None:
            return

        if doc["author_id"] == self.bot.user.id:
            return

        if doc.get("has_embeds"):
            return

        message = await self._message_from_history(doc)

        if message is None:
            return

        await self._persist_attachments(message)
        self._remember_last_message(message)

    
    @commands.Cog.listener("on_message")
    async def disboard_listener(self, message: discord.Message):  

        DISBOARD_ID = 302050872383242240
        # DISBOARD_ID = 862859543700176896 # Test id Spongiper

        # Nur DISBOARD-Nachrichten berücksichtigen
        if not message.author or message.author.id != DISBOARD_ID:
            return

        if not message.embeds:
            return
        
        if message.guild.id != 1247839863408164868:
            return

        for embed in message.embeds:
            text_to_check = []

            # Description prüfen
            if embed.description:
                text_to_check.append(embed.description.lower())

            # Alle Felder prüfen
            for field in embed.fields:
                if field.name:
                    text_to_check.append(field.name.lower())
                if field.value:
                    text_to_check.append(field.value.lower())

            # Alles zusammenfassen
            combined_text = " ".join(text_to_check)

            # Auf "bump erfolgreich" prüfen
            if "bump erfolgreich!" in combined_text:

                # Datenbank updaten
                db_guild = await self.client.get_guild(message.guild.id)
                guild = db_guild.settings
                guild["last_bump"] = round(datetime.datetime.now().timestamp())
                guild["last_bump_channel"] = message.channel.id
                db_guild.settings = guild

                # User aus der Interaction, falls vorhanden
                user = None
                if message.interaction_metadata:
                    user = message.interaction_metadata.user

                if user:
                    await message.channel.send(
                        f"Vielen Dank für das Bumpen unseres Kellers, {user.mention}! "
                        f"Ich werde in zwei Stunden wieder daran erinnern!"
                    )
                else:
                    await message.channel.send(
                        "Vielen Dank für das Bumpen unseres Kellers! Ich werde in 2 Stunden wieder daran erinnern!"
                    )

                # Reminder planen (2 Stunden = 7200 Sekunden)
                await self.schedule_reminder()
                break  # Kein doppeltes Triggern, wenn mehrere Felder passen
    
    async def schedule_reminder(self, guild: int=1247839863408164868, delay: int=7200):
        _guild = self.bot.get_guild(guild)
        
        if _guild is None:
            return
        
        db_guild = await self.client.get_guild(_guild.id)
        guild = db_guild.settings
        
        if "last_bump" not in guild or "last_bump_channel" not in guild:
            return
        
        last_bump = guild["last_bump"]
        last_channel = guild["last_bump_channel"]
        
        now = round(datetime.datetime.now().timestamp())
        elapsed = now - last_bump
        remaining = delay - elapsed
        
        remaining = max(0, remaining)
        
        chn = self.bot.get_channel(last_channel)
        
        await self.remind(chn, remaining)

            
    async def remind(self, channel, remaining):
        if self.scheduled:
            return
        self.scheduled = True

        print(f"reminder scheduled ({remaining})")
        await asyncio.sleep(remaining)
        await channel.send("Zwei Stunden sind vorbei! Zeit zu `/bump`en, Kellerfreunde!\n<@&1271932301885968484>")
        self.scheduled = False
    
    @commands.Cog.listener(name="on_message")
    async def make_that_a_quote(self, message: discord.Message):
        mentions = message.mentions
        
        db_guild = await self.client.get_guild(message.guild.id)
        settings = db_guild.settings
        
        if self.bot.user in mentions:
            if message.type != discord.MessageType.reply:
                await message.add_reaction("🏓")
                return
            
            if "blacklist" in settings:
                if str(message.channel.id) in settings["blacklist"]:
                    await message.reply(f"> {Emote.WARNING} Dieser Channel ist auf der Blacklist!", allowed_mentions=None, delete_after=5)
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
                await message.add_reaction("🤖")
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
            
            quote = await channel.send(embed=embed.BigEmbed(), allowed_mentions=None, file=attachment)
            await origin.edit(content=f"Zitat erstellt: {quote.jump_url}")
            
    @commands.Cog.listener(name="on_message")
    async def someone(self, message: discord.Message):
        
        if message.author.bot \
        or message.guild is None \
        or message.author.id in get_blocklist() \
        or await Antispam().spamming(message):
            return
        
        res = SOMEONE_PATTERN.findall(message.content)
        
        if len(res) == 0:
            return            
        
        members: list = message.guild.members

        the_choosen_one = None

        for i in range(9):
            if i > 0:
                await asyncio.sleep(3)
            pre: discord.Member = random.choice(members)
            if pre.bot:
                continue
            the_choosen_one = pre
            break

        if the_choosen_one is None:
            await message.reply("Ich konnte keinen Nutzer finden...")
            return

        if message.guild.id == 1247839863408164868:
            file = discord.File("./images/MeisterKellerWaehltDich.png", "bild.png")
            await message.reply(silent=True, content=f"Ich wähle dich {the_choosen_one.mention}!", file=file)
        else:
            await message.reply(silent=True, content=f"Ich wähle dich {the_choosen_one.mention}!")
            await message.channel.send(silent=True, content="https://tenor.com/view/pokemon-poke-ball-ash-i-choose-you-gif-4444793")
    
    @commands.Cog.listener(name="on_guild_join")
    async def on_guild_join(self, guild: discord.Guild):
        await self.bot.get_user(579111799794958377).send("+"+guild.name)
    
    @commands.Cog.listener(name="on_guild_remove")
    async def on_guild_remove(self, guild: discord.Guild):
        await self.bot.get_user(579111799794958377).send("-"+guild.name)
    
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