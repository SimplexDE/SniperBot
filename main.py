import discord
import os
import sys
import asyncio
import signal
import random
from dotenv import get_key
from discord.ext import commands, tasks

from util.logger import log
from util.embed import Embed
from util.constants import ONLINE_PRESENCES, STARTUP_PRESENCES

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

class Sniper(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="s.",
            help_command=None,
            intents=intents
        )
        self.message_cache = {}
    
    @staticmethod
    def _get_extenstions() -> list:
        extensions = []
        
        for path in paths:
            for file in os.listdir(path):
                if file.startswith("-"):
                    continue
                if file.endswith(".py"):
                    extensions.append(f"{path.replace("/", ".")}{file[:-3]}")
                    
        return extensions

    @tasks.loop(minutes=30)
    async def cleanup(self):
        log.info("Running Cleanup Task...")
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

    @tasks.loop(minutes=15)
    async def presence_tick(self):
        log.info("Running Presence Tick...")
        await self.change_presence(
            activity=random.choice(ONLINE_PRESENCES), status=discord.Status.online
        )

    async def setup_hook(self):
        log.debug("Starting Cleanup Task...")
        self.cleanup.start()
    
    async def on_connect(self):
        log.debug("Setting Presence to Startup Presence...")
        await self.change_presence(
            activity=random.choice(STARTUP_PRESENCES), status=discord.Status.dnd
        )

    async def on_ready(self):
        
        log.trace("Loading Extensions...")
        for extension in self._get_extenstions():
            await self.load_extension(extension)
        
        # TODO: Make this its own function / separate out into a file ----------------------------------------
        log.debug("Grabbing Channel Text Histories...")
        log_channel = self.get_channel(int(1325196683776229410))
        _guilds = self.guilds
        text_channels_count = 0
        for guild in _guilds:
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    text_channels_count += 1
        text_channels_retrieved = 0
        guilds_count = len(_guilds)
        guilds_retrieved = 0
        msgs = 0
        
        for guild in _guilds:
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    if not self.message_cache.get(channel.id):
                        self.message_cache[channel.id] = []
                    try:
                        self.message_cache[channel.id] = [message async for message in channel.history(limit=100)]
                    except Exception:
                        continue
                    msgs += len(self.message_cache[channel.id])
                    text_channels_retrieved += 1
            guilds_retrieved += 1
            
        log.debug("Grabbed all Text Histories...")
        # --------------------------------------------------------------------------------------------------------------------------
            
        embed = Embed(
            title="History-Grabber",
            description= \
                f"Guilds retrieved: `{guilds_retrieved}/{guilds_count} -|- {round(guilds_retrieved / guilds_count * 100)}%`" +
                f"\nChannels retrieved: `{text_channels_retrieved}/{text_channels_count} -|- {round(text_channels_retrieved / text_channels_count * 100)}%`" + 
                f"\nMessages collected: **`{msgs}`**"
        )
                
        await log_channel.send(embed=embed.StandardEmbed())
    
        sync = await self.tree.sync()
        log.info(f"Synced {len(sync)} commands")
    
        self.presence_tick.start()
    
        log.success(
            f"{self.user.name} Ready"
            )

# Shutdown Handler
def shutdown_handler(signum, frame):
    loop = asyncio.get_event_loop()

    # Cancel all tasks lingering
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    loop.close()

    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

bot = Sniper()

bot.run(os.environ.get("TOKEN", get_key("./.env", "TOKEN")))
