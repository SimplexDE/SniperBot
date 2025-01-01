import discord
import os
import random
from typing import Optional
from discord.ext import commands
import datetime
from discord import app_commands

image_exts = [".jpg", ".png", ".jpeg"]

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.last_message: discord.Message | None = None
        self.last_sent_from_bot: discord.Message | None = None
        self.last_sent: discord.Message | None = None
        
    @commands.Cog.listener(name="on_message")
    @commands.guild_only()
    async def snipe(self, message: discord.Message):
        if message.author.bot:
            return
        
        if self.last_message is None:
            return
        
        if len(message.content) != 1:
            return
            
        content = message.content.lower()
        
        if content[0] != "s":
            return
        
        reuse = False
        
        if self.last_message == self.last_sent:
            reuse = True
        self.last_sent = self.last_message
        
        timestamp = f"{self.last_message.created_at.day}.{self.last_message.created_at.month}.{self.last_message.created_at.year} {self.last_message.created_at.hour}:{self.last_message.created_at.minute}"
        author = f"📸 {self.last_message.author.global_name}"
        desc = f"> {self.last_message.content}" if len(self.last_message.content) != 0 else ""
        footer = f"🔗 #{self.last_message.channel.name} — 🕒 {timestamp}"
        
        embed = discord.Embed(title="", description=desc, color=discord.Color.blue(), timestamp=datetime.datetime.now())
        embed.set_author(name=author, icon_url=self.last_message.author.avatar if self.last_message.author.avatar is not None else self.last_message.author.default_avatar)
        embed.set_footer(text=footer)
        
        embeds = [embed]
        files = []
        i = 0
        
        if not reuse:
            for f in os.listdir("./attachments"):
                if i == 0:
                    embeds.pop(0)
                    embed.set_image(url=f"attachment://{f}")
                    embeds.append(embed)
                
                embed_n = discord.Embed(title="", description="", color=discord.Color.blue(), timestamp=datetime.datetime.now())
                embed_n.set_image(url=f"attachment://{f}")
                embed_n.set_author(name=author, icon_url=self.last_message.author.avatar if self.last_message.author.avatar is not None else self.last_message.author.default_avatar)
                embed_n.set_footer(text=footer)
                
                if i != 0:
                    embeds.append(embed_n)
                files.append(discord.File(f"./attachments/{f}"))
                i += 1
                
        if reuse:
            embed_urls = [embed.image.url for embed in self.last_sent_from_bot.embeds]
            for url in embed_urls:
                if i == 0:
                    embeds.pop(0)
                    embed.set_image(url=url)
                    embeds.append(embed)
                
                embed_n = discord.Embed(title="", description="", color=discord.Color.blue(), timestamp=datetime.datetime.now())
                embed_n.set_image(url=url)
                embed_n.set_author(name=author, icon_url=self.last_message.author.avatar if self.last_message.author.avatar is not None else self.last_message.author.default_avatar)
                embed_n.set_footer(text=footer)
                
                if i != 0:
                    embeds.append(embed_n)
                i += 1
    
        self.last_sent_from_bot = await message.channel.send(embeds=embeds, files=files if reuse is False else None)
        
    @commands.Cog.listener(name="on_message_delete")
    @commands.guild_only()
    async def save(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not os.path.exists("./attachments"):
            os.mkdir("./attachments")
        
        for f in os.listdir("./attachments"):
            os.remove(f"./attachments/{f}")
        
        if message.attachments:
            i = 1
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(image_exts)):
                    _, extension = os.path.splitext(attachment.filename)
                    await attachment.save(fp="./attachments/{}{}".format(i, extension))
                i += 1
        
        self.last_message = message
    
async def setup(bot):
    await bot.add_cog(Events(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")