import discord
import os
import sys
import asyncio
import signal
import random
from dotenv import get_key
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

class Sniper(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=">>",
            help_command=None,
            intents=intents
        )

    @tasks.loop(minutes=30)
    async def cleanup(self):
        print("> Cleanup - Started")
        for server_dir in os.listdir("./attachments"):
            if len(os.listdir(f"./attachments/{server_dir}")) == 0:
                os.rmdir(f"./attachments/{server_dir}")
                
            for channel_dir in os.listdir(f"./attachments/{server_dir}"):
                if len(os.listdir(f"./attachments/{server_dir}/{channel_dir}")) == 0:
                    os.rmdir(f"./attachments/{server_dir}/{channel_dir}")
                    
                for image_file in os.listdir(f"./attachments/{server_dir}/{channel_dir}"):
                    os.remove(f"./attachments/{server_dir}/{channel_dir}/{image_file}")
                    
                if len(os.listdir(f"./attachments/{server_dir}/{channel_dir}")) == 0:
                    os.rmdir(f"./attachments/{server_dir}/{channel_dir}")
            
            if len(os.listdir(f"./attachments/{server_dir}")) == 0:
                os.rmdir(f"./attachments/{server_dir}")
        print("> Cleanup - Complete")

    @tasks.loop(minutes=60)
    async def presence_tick(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="Sniping"),
            discord.CustomActivity(name="Sniper"),
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.online
        )

    async def setup_hook(self):
        pass
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\\_(ツ)_/¯")
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.dnd
        )
    
    async def on_ready(self):
        
        self.presence_tick.start()
        self.cleanup.start()
        
        for path in paths:
            for file in os.listdir(path):
                if file.startswith("-"):
                    continue
                if file.endswith(".py"):
                    await self.load_extension(f"{path.replace("/", ".")}{file[:-3]}")
    
        sync = await self.tree.sync()
        print(f"> Synced {len(sync)} commands")
    
        print(
            f"[✓] >> {self.user.name} Ready"
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
