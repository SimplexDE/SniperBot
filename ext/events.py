import discord
import random
import re
import os
import pytz
import textwrap
from PIL import Image, ImageDraw, ImageFont
from unidecode import unidecode
from discord.ext import commands
from util.antispam import Antispam
from util.starboard import Starboard
from database.mongoclient import SpongiperClient
import datetime
from ext.developer import blocklist

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]
FONTS_SRC = "./fonts"
IMAGES_SRC = "./images"
ATTACHMENTS_SRC = "./attachments"

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
        
        colors = [
            discord.Color.blue(),
            discord.Color.red(),
            discord.Color.blurple(),
            discord.Color.gold(),
            discord.Color.green(),
            discord.Color.fuchsia(),
            discord.Color.yellow(),
            discord.Color.magenta(),
            discord.Color.random(),
        ]
        
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
        desc = f"> {self.last_message[message.guild.id][message.channel.id].content}" if len(self.last_message[message.guild.id][message.channel.id].content) != 0 else ""
        footer = f"🔗 #{self.last_message[message.guild.id][message.channel.id].channel.name} — 🕒 {timestamp}"
        
        embed = discord.Embed(title="", description=desc, color=random.choice(colors), timestamp=datetime.datetime.now())
        embed.set_author(name=author, icon_url=self.last_message[message.guild.id][message.channel.id].author.avatar if self.last_message[message.guild.id][message.channel.id].author.avatar is not None else self.last_message[message.guild.id][message.channel.id].author.default_avatar)
        embed.set_footer(text=footer)
        
        embeds = [embed]
        files = []
        i = 0
        
        if not reuse:
            for f in os.listdir(f"{ATTACHMENTS_SRC}/{message.guild.id}/{message.channel.id}"):
                if i == 0:
                    embeds.pop(0)
                    embed.set_image(url=f"attachment://{f}")
                    embeds.append(embed)
                
                embed_n = discord.Embed(title="", description="", color=discord.Color.blue(), timestamp=datetime.datetime.now())
                embed_n.set_image(url=f"attachment://{f}")
                embed_n.set_author(name=author, icon_url=self.last_message[message.guild.id][message.channel.id].author.avatar if self.last_message[message.guild.id][message.channel.id].author.avatar is not None else self.last_message[message.guild.id][message.channel.id].author.default_avatar)
                embed_n.set_footer(text=footer)
                
                if i != 0:
                    embeds.append(embed_n)
                files.append(discord.File(f"{ATTACHMENTS_SRC}/{message.guild.id}/{message.channel.id}/{f}"))
                i += 1
                
        if reuse:
            embed_urls = [embed.image.url for embed in self.last_sent_from_bot[message.guild.id][message.channel.id].embeds]
            for url in embed_urls:
                if i == 0:
                    embeds.pop(0)
                    embed.set_image(url=url)
                    embeds.append(embed)
                
                embed_n = discord.Embed(title="", description="", color=discord.Color.blue(), timestamp=datetime.datetime.now())
                embed_n.set_image(url=url)
                embed_n.set_author(name=author, icon_url=self.last_message[message.guild.id][message.channel.id].author.avatar if self.last_message[message.guild.id][message.channel.id].author.avatar is not None else self.last_message[message.guild.id][message.channel.id].author.default_avatar)
                embed_n.set_footer(text=footer)
                
                if i != 0:
                    embeds.append(embed_n)
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
    
    def truncate_text(self, text, max_chars=100, suffix="..."):
        return text[:max_chars] + suffix if len(text) > max_chars else text
    
    def replace_mentions(self, text: str, guild: discord.Guild):        
        pattern = "<(@|#|@&?)(\\d+)>"
        mentions = re.findall(pattern, text)
        
        for mention in mentions:
            match (mention[0]):
                case ("@&"):
                    text = text.replace(f"<{mention[0] + str(mention[1])}>", f"@{guild.get_role(int(mention[1])).name}")      
                case ("@"):
                    text = text.replace(f"<{mention[0] + str(mention[1])}>", f"@{guild.get_member(int(mention[1])).name}")
                case ("#"):
                    text = text.replace(f"<{mention[0] + str(mention[1])}>", f"#{guild.get_channel(int(mention[1])).name}") 
                case (_):
                    continue

        return text
    
    def normalize_text(self, text: str):
        return unidecode(text)
    
    @commands.Cog.listener(name="on_message")
    async def make_that_a_quote(self, message: discord.Message):
        mentions = message.mentions
        
        if self.bot.user in mentions:
            if message.type != discord.MessageType.reply:
                await message.reply("> :warning: Ohne Nachricht, kein Zitat :person_shrugging:", allowed_mentions=None, delete_after=5)
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
            
            if not os.path.exists(f"{IMAGES_SRC}/out"):
                os.mkdir(f"{IMAGES_SRC}/out")
            
            avatar_path = "images/out/avatar.png"
            
            avatar = msg.author.display_avatar if msg.author.display_avatar is not None else msg.author.default_avatar
            await avatar.save(avatar_path)
            
            AVATAR_SIZE = (256, 256)
            BACKGROUND_SIZE = (256*2, 256)
            
            FONT_LARGE = ImageFont.truetype(font=f"{FONTS_SRC}/arial.ttf", size=24)
            FONT_SMALL = ImageFont.truetype(font=f"{FONTS_SRC}/arial.ttf", size=18)
            FONT_XSMALL = ImageFont.truetype(font=f"{FONTS_SRC}/arial.ttf", size=12)
            
            mask = Image.open(f"{IMAGES_SRC}/mask.png")
            background = Image.new("RGBA", BACKGROUND_SIZE, color=(0,0,0))
            avatar_image = Image.open(avatar_path).resize(AVATAR_SIZE)
            background.paste(avatar_image, mask=mask.convert("L").resize(AVATAR_SIZE))
            
            draw = ImageDraw.Draw(background)
            
            message_text = self.replace_mentions(msg.content, message.guild)
            message_text = self.normalize_text(message_text)
            final_message = "\n".join(textwrap.wrap(message_text, 25))
            final_message = self.truncate_text(final_message)
            
            textbox_LARGE = draw.textbbox((0, 0), text=f"„{final_message}“", font=FONT_LARGE)
            textbox_SMALL = draw.textbbox((0, 0), text=self.normalize_text(msg.author.display_name), font=FONT_SMALL)
            textbox_XSMALL = draw.textbbox((0, 0), text=msg.author.name, font=FONT_XSMALL)

            textbox_middle_L = (textbox_LARGE[2] / 2, textbox_LARGE[3] / 2)
            textbox_middle_S = (textbox_SMALL[2] / 2, textbox_SMALL[3] / 2)
            textbox_middle_XS = (textbox_XSMALL[2] / 2, textbox_XSMALL[3] / 2)
            
            draw.text((512 / 2 - textbox_middle_L[0] + 90, 256 / 2 - textbox_middle_L[1]), font=FONT_LARGE, text=f"„{final_message}“", fill="white", align="center")
            draw.text((512 / 2 - textbox_middle_S[0] + 90, 256 / 2 - textbox_middle_S[1] + 90), font=FONT_SMALL, text=self.normalize_text(msg.author.display_name), fill="white", align="center")
            draw.text((512 / 2 - textbox_middle_XS[0] + 90, 256 / 2 - textbox_middle_S[1] + 115), font=FONT_XSMALL, text=msg.author.name, fill="gray", align="center")
            
            background.save(f"{IMAGES_SRC}/out/out.png")
            
            colors = [
                discord.Color.blue(),
                discord.Color.red(),
                discord.Color.blurple(),
                discord.Color.gold(),
                discord.Color.green(),
                discord.Color.fuchsia(),
                discord.Color.yellow(),
                discord.Color.magenta(),
                discord.Color.random(),
            ]
            
            attachment = discord.File(f"{IMAGES_SRC}/out/out.png")
            
            tz = pytz.timezone("Europe/Berlin")
            timestamp = msg.created_at.astimezone(tz).strftime("%d.%m.%Y %H:%M")
            author = f"📜 {msg.author.display_name}"
            desc = f"> {msg.content}" if len(msg.content) != 0 else ""
            footer = f"🔗 #{msg.channel.name} — 🕒 {timestamp}"
            
            embed = discord.Embed(title="", description=desc, color=random.choice(colors), timestamp=datetime.datetime.now())
            embed.set_author(name=author, icon_url=msg.author.avatar if msg.author.avatar is not None else msg.author.default_avatar, url=msg.jump_url)
            embed.set_footer(text=footer)
            embed.set_image(url="attachment://out.png")
            
            db_guild = await self.client.get_guild(message.guild.id)
            settings = db_guild.settings

            channel = message.channel

            if "quote_channel" in settings:
                channel = self.bot.get_channel(settings["quote_channel"])
            
            await origin.delete(delay=1)
            quote = await channel.send(embed=embed, allowed_mentions=None, file=attachment)
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
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")