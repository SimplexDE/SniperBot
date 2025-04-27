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

# Image file extensions that should be treated as images when quoting/sniping
image_exts = [
    ".jpg",
    ".png",
    ".jpeg",
    ".webp",
    ".gif",
]


class Events(commands.Cog):
    """All message‑related event listeners for the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.starboard: Starboard = Starboard(bot)
        self.client: SpongiperClient = SpongiperClient(bot)

        # Caches for the snipe feature (guild‑id → channel‑id → message)
        self.last_message: dict[int, dict[int, discord.Message | None]] = {}
        self.last_sent_from_bot: dict[int, dict[int, discord.Message | None]] = {}
        self.last_sent: dict[int, dict[int, discord.Message | None]] = {}

        # User‑IDs that should be ignored globally
        self.blocklist = blocklist

    # ────────────────────────────────────────────────────────────
    # "s"  →  Snipe the last deleted message or image
    # ────────────────────────────────────────────────────────────
    @commands.Cog.listener(name="on_message")
    async def snipe(self, message: discord.Message):
        """If a user sends just the letter "s", repost the last deleted message / image."""

        if message.author.bot or message.guild is None or message.author.id in self.blocklist:
            return

        # Ensure we have something cached for this guild/channel
        self.last_message.setdefault(message.guild.id, {})
        self.last_message[message.guild.id].setdefault(message.channel.id, None)
        if self.last_message[message.guild.id][message.channel.id] is None:
            return

        # Trigger must be exactly the single letter "s"
        if message.content.lower() != "s":
            return
        if await Antispam().spamming(message):
            return

        reuse_previous_embeds = False
        self.last_sent.setdefault(message.guild.id, {}).setdefault(message.channel.id, None)
        self.last_sent_from_bot.setdefault(message.guild.id, {}).setdefault(message.channel.id, None)

        if (
            self.last_message[message.guild.id][message.channel.id]
            == self.last_sent[message.guild.id][message.channel.id]
        ):
            reuse_previous_embeds = True

        self.last_sent[message.guild.id][message.channel.id] = self.last_message[message.guild.id][
            message.channel.id
        ]

        # Build base embed
        tz = pytz.timezone("Europe/Berlin")
        target_msg = self.last_message[message.guild.id][message.channel.id]
        timestamp = target_msg.created_at.astimezone(tz).strftime("%d.%m.%Y %H:%M")
        author = f"📸 {target_msg.author.display_name or target_msg.author.name}"
        author_avatar = target_msg.author.avatar or target_msg.author.default_avatar
        description = f"> {target_msg.content}" if target_msg.content else ""
        footer = f"🔗 #{target_msg.channel.name} — 🕒 {timestamp}"
        color = random.choice(COLORS)

        base_embed = Embed(
            title=author,
            description=description,
            color=color,
            title_icon_url=author_avatar,
            footer=footer,
        )

        embeds: list[discord.Embed] = [base_embed.StandardEmbed()]
        files: list[discord.File] = []
        img_counter = 0

        # Fresh delete → use cached files from disk
        if not reuse_previous_embeds:
            cache_dir = f"{ATTACHMENTS_SRC}/{message.guild.id}/{message.channel.id}"
            if os.path.isdir(cache_dir):
                for f in os.listdir(cache_dir):
                    if img_counter == 0:
                        embeds.pop(0)
                        base_embed.image_url = f"attachment://{f}"
                        embeds.append(base_embed.BigEmbed())
                    else:
                        extra = Embed(
                            title=author,
                            color=color,
                            title_icon_url=author_avatar,
                            footer=footer,
                            image_url=f"attachment://{f}",
                        )
                        embeds.append(extra.BigEmbed())
                    files.append(discord.File(f"{cache_dir}/{f}"))
                    img_counter += 1
        # Re‑use images from the bot's previous post
        else:
            prev_embeds = self.last_sent_from_bot[message.guild.id][message.channel.id].embeds
            for url in (e.image.url for e in prev_embeds if e.image):
                if img_counter == 0:
                    embeds.pop(0)
                    base_embed.image_url = url
                    embeds.append(base_embed.BigEmbed())
                else:
                    extra = Embed(
                        title=author,
                        color=color,
                        title_icon_url=author_avatar,
                        footer=footer,
                        image_url=url,
                    )
                    embeds.append(extra.BigEmbed())
                img_counter += 1

        self.last_sent_from_bot[message.guild.id][message.channel.id] = await message.channel.send(
            embeds=embeds,
            files=files if not reuse_previous_embeds else None,
        )

    # ────────────────────────────────────────────────────────────
    # Cache images when a message gets deleted (cached delete)
    # ────────────────────────────────────────────────────────────
    @commands.Cog.listener(name="on_message_delete")
    async def save(self, message: discord.Message):
        if (
            message.author.id in (*self.blocklist, self.bot.user.id)
            or message.guild is None
            or message.embeds
        ):
            return

        guild_dir = f"{ATTACHMENTS_SRC}/{message.guild.id}"
        chan_dir = f"{guild_dir}/{message.channel.id}"
        os.makedirs(chan_dir, exist_ok=True)

        # Clear old files
        for f in os.listdir(chan_dir):
            os.remove(f"{chan_dir}/{f}")

        if message.attachments:
            for idx, att in enumerate(message.attachments, start=1):
                if att.filename.lower().endswith(tuple(image_exts)):
                    _, ext = os.path.splitext(att.filename)
                    await att.save(fp=f"{chan_dir}/{idx}{ext}")

        self.last_message.setdefault(message.guild.id, {})[message.channel.id] = message

    # ────────────────────────────────────────────────────────────
    # Cache images for uncached deletes (raw delete)
    # ────────────────────────────────────────────────────────────
    @commands.Cog.listener(name="on_raw_message_delete")
    async def save_raw(self, payload: discord.RawMessageDeleteEvent):
        if payload.cached_message is not None:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        cached_list = self.bot.message_cache.get(channel.id)
        if not cached_list:
            return

        message: discord.Message | None = next((m for m in cached_list if m.id == payload.message_id), None)
        if (
            message is None
            or message.author.id == self.bot.user.id
            or message.guild is None
            or message.embeds
        ):
            return

        guild_dir = f"{ATTACHMENTS_SRC}/{message.guild.id}"
        chan_dir = f"{guild_dir}/{message.channel.id}"
        os.makedirs(chan_dir, exist_ok=True)

        for f in os.listdir(chan_dir):
            os.remove(f"{chan_dir}/{f}")

        if message.attachments:
            for idx, att in enumerate(message.attachments, start=1):
                if att.filename.lower().endswith(tuple(image_exts)):
                    _, ext = os.path.splitext(att.filename)
                    await att.save(fp=f"{chan_dir}/{idx}{ext}")

        self.last_message.setdefault(message.guild.id, {})[message.channel.id] = message

    # ────────────────────────────────────────────────────────────
    # Mention‑reply  →  turn message (text **and images**) into a quote
    # ────────────────────────────────────────────────────────────
    @commands.Cog.listener(name="on_message")
    async def make_that_a_quote(self, message: discord.Message):
        """Create a quote (embed + all images) when the bot is mentioned in a reply."""

        if self.bot.user not in message.mentions:
            return

        # Must be a reply
        if message.type != discord.MessageType.reply:
            await message.reply(
                "> :warning: No message to quote :person_shrugging:",
                allowed_mentions=None,
                delete_after=5,
            )
            return

        # NSFW gatekeeping
        if message.channel.is_nsfw():
            db
