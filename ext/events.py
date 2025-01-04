import discord
import os
import pytz
from discord.ext import commands
from util.antispam import Antispam
import datetime

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.last_message = {}
        self.last_sent_from_bot = {}
        self.last_sent = {}
    
    @commands.Cog.listener(name="on_message")
    async def orders(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.guild is None:
            return
        
        if message.author.id != 579111799794958377:
            return
        
        msg = message.content.lower()
        
        if not msg.startswith(f"<@{self.bot.user.id}> execute order"):
            return
    
        _msg = msg.split(" ", maxsplit=4)
        execute = _msg[3]
        
        try:
            await message.delete(delay=10)
        except discord.Forbidden:
            pass
        
        match (execute):
            case ("666"): # Clears the current message in cache
                self.last_message[message.guild.id] = {}
                self.last_sent_from_bot[message.guild.id] = {}
                self.last_sent[message.guild.id] = {}
                
            case ("1337"): # Cleans the attachmentsfolder
                for server_dir in os.listdir("./attachments"):
                    if len(os.listdir(f"./attachments/{server_dir}")) == 0:
                        os.rmdir(f"./attachments/{server_dir}")
                        continue
                        
                    for channel_dir in os.listdir(f"./attachments/{server_dir}"):
                        if len(os.listdir(f"./attachments/{server_dir}/{channel_dir}")) == 0:
                            os.rmdir(f"./attachments/{server_dir}/{channel_dir}")
                            continue
                            
                        for image_file in os.listdir(f"./attachments/{server_dir}/{channel_dir}"):
                            os.remove(f"./attachments/{server_dir}/{channel_dir}/{image_file}")
                            
                        if len(os.listdir(f"./attachments/{server_dir}/{channel_dir}")) == 0:
                            os.rmdir(f"./attachments/{server_dir}/{channel_dir}")
                            continue
                    
                    if len(os.listdir(f"./attachments/{server_dir}")) == 0:
                        os.rmdir(f"./attachments/{server_dir}")
                        continue
                    
            case ("populate"):
                if not self.message_cache.get(message.channel.id):
                    self.message_cache[message.channel.id] = []
                self.message_cache[message.channel.id] = [message async for message in message.channel.history(limit=100)]
                    
            case (_):
                await message.reply(f"Ich konnte `{execute}` nicht zuordnen.", delete_after=5)
                return
                
        await message.reply(f"`{execute}` ausgeführt.", delete_after=10)
        
    @commands.Cog.listener(name="on_message")
    async def snipe(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.guild is None:
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
        desc = f"> {self.last_message[message.guild.id][message.channel.id].content}" if len(self.last_message[message.guild.id][message.channel.id].content) != 0 else ""
        footer = f"🔗 #{self.last_message[message.guild.id][message.channel.id].channel.name} — 🕒 {timestamp}"
        
        embed = discord.Embed(title="", description=desc, color=discord.Color.blue(), timestamp=datetime.datetime.now())
        embed.set_author(name=author, icon_url=self.last_message[message.guild.id][message.channel.id].author.avatar if self.last_message[message.guild.id][message.channel.id].author.avatar is not None else self.last_message[message.guild.id][message.channel.id].author.default_avatar)
        embed.set_footer(text=footer)
        
        embeds = [embed]
        files = []
        i = 0
        
        if not reuse:
            for f in os.listdir(f"./attachments/{message.guild.id}/{message.channel.id}"):
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
                files.append(discord.File(f"./attachments/{message.guild.id}/{message.channel.id}/{f}"))
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
        
        if message.guild is None:
            return
        
        if len(message.embeds) != 0:
            return
                
        if not os.path.exists("./attachments"):
            os.mkdir("./attachments")
            
        if not os.path.exists("./attachments/{}".format(str(message.guild.id))):
            os.mkdir("./attachments/{}".format(str(message.guild.id)))
            
        if not os.path.exists("./attachments/{}/{}".format(str(message.guild.id), str(message.channel.id))):
            os.mkdir("./attachments/{}/{}".format(str(message.guild.id), str(message.channel.id)))
        
        for f in os.listdir(f"./attachments/{str(message.guild.id)}/{str(message.channel.id)}"):
            os.remove(f"./attachments/{str(message.guild.id)}/{str(message.channel.id)}/{f}")
        
        if message.attachments:
            i = 1
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(image_exts)):
                    _, extension = os.path.splitext(attachment.filename)
                    await attachment.save(fp="./attachments/{}/{}/{}{}".format(str(message.guild.id), str(message.channel.id), i, extension))
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
            print("Cached Message found, aborting...")
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
                
        if not os.path.exists("./attachments"):
            os.mkdir("./attachments")
            
        if not os.path.exists("./attachments/{}".format(str(message.guild.id))):
            os.mkdir("./attachments/{}".format(str(message.guild.id)))
            
        if not os.path.exists("./attachments/{}/{}".format(str(message.guild.id), str(message.channel.id))):
            os.mkdir("./attachments/{}/{}".format(str(message.guild.id), str(message.channel.id)))
        
        for f in os.listdir(f"./attachments/{str(message.guild.id)}/{str(message.channel.id)}"):
            os.remove(f"./attachments/{str(message.guild.id)}/{str(message.channel.id)}/{f}")
        
        if message.attachments:
            i = 1
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(image_exts)):
                    _, extension = os.path.splitext(attachment.filename)
                    await attachment.save(fp="./attachments/{}/{}/{}{}".format(str(message.guild.id), str(message.channel.id), i, extension))
                i += 1
        
        if not self.last_message.get(message.guild.id):
            self.last_message[message.guild.id] = {}
            
        if not self.last_message[message.guild.id].get(message.channel.id):
            self.last_message[message.guild.id][message.channel.id] = None

        self.last_message[message.guild.id][message.channel.id] = message
    
async def setup(bot):
    await bot.add_cog(Events(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")