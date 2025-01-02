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
        print("> Cleaning...")
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

    @tasks.loop(minutes=60)
    async def presence_tick(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="Type s to snipe deleted messages"),
            discord.CustomActivity(name="Stalking for deleted messages"),
            discord.CustomActivity(name="Danke Simplex"),
            discord.Activity(type=discord.ActivityType.playing, name="Aale und Rolltreppen"),
            discord.Activity(type=discord.ActivityType.watching, name="Don"),
            discord.Activity(type=discord.ActivityType.watching, name="Juox"),
            discord.Activity(type=discord.ActivityType.watching, name="Simplex"),
            discord.Streaming(name="Technikstube", url="https://www.youtube.com/watch?v=d1YBv2mWll0"),
            discord.Streaming(name="Der Keller", url="https://www.youtube.com/watch?v=xvFZjo5PgG0"),
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.online
        )

    async def setup_hook(self):
        self.cleanup.start()
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\\_(ツ)_/¯"),
            discord.CustomActivity(name="q(≧▽≦q)"),
            discord.CustomActivity(name="(^///^)"),
            discord.CustomActivity(name="\\^o^/"),
            discord.CustomActivity(name="(ಥ _ ಥ)"),
            discord.CustomActivity(name="◑﹏◐"),
            discord.CustomActivity(name="The purpose of our lives is to be happy. — Dalai Lama"),
            discord.CustomActivity(name="The healthiest response to life is joy. — Deepak Chopra")
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.dnd
        )
    
    async def on_ready(self):
        
        self.presence_tick.start()
        
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
