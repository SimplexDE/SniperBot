import discord
import os
import sys
import asyncio
import signal
import random
from dotenv import get_key
from discord.ext import commands, tasks

from util.logger import log
from util.constants import ONLINE_PRESENCES, STARTUP_PRESENCES
from database.message_history import MessageHistory

from stats.client import BOT_STATUS, SERVER_COUNT

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

HISTORY_BACKFILL_LIMIT = 10
HISTORY_BACKFILL_CONCURRENCY = 5

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

    @staticmethod
    async def _backfill_channel_history(channel, history: MessageHistory, semaphore: asyncio.Semaphore):
        async with semaphore:
            try:
                async for message in channel.history(limit=HISTORY_BACKFILL_LIMIT):
                    history.remember(message)
            except (discord.Forbidden, discord.HTTPException):
                pass

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
        BOT_STATUS.state("starting")
        self.cleanup.start()
        MessageHistory().ensure_index()
    
    async def on_connect(self):
        log.debug("Setting Presence to Startup Presence...")
        await self.change_presence(
            activity=random.choice(STARTUP_PRESENCES), status=discord.Status.dnd
        )

    async def on_ready(self):
        
        log.trace("Loading Extensions...")
        for extension in self._get_extenstions():
            await self.load_extension(extension)

        SERVER_COUNT.set(len(self.guilds))

        log.debug("Backfilling recent channel history...")
        history = MessageHistory()
        semaphore = asyncio.Semaphore(HISTORY_BACKFILL_CONCURRENCY)
        text_channels = [
            channel
            for guild in self.guilds
            for channel in guild.channels
            if channel.type == discord.ChannelType.text
        ]
        await asyncio.gather(*(
            self._backfill_channel_history(channel, history, semaphore)
            for channel in text_channels
        ))
        log.debug(f"Backfilled history for {len(text_channels)} channels")

        sync = await self.tree.sync()
        log.info(f"Synced {len(sync)} commands")
    
        self.presence_tick.start()
        BOT_STATUS.state("running")
    
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

    BOT_STATUS.state("stopped")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

bot = Sniper()

bot.run(os.environ.get("TOKEN", get_key("./.env", "TOKEN")))
