import discord
from discord import app_commands
from discord.ext import commands

from util.checks import is_dev
from util.constants import Emote

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]
ATTACHMENTS_SRC = "./attachments"

blocklist = []

class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    execute = app_commands.Group(name="execute", description="Developer Commands", 
                                allowed_contexts=(app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True)),
                                allowed_installs=app_commands.AppInstallationType(guild=True, user=True))
    
    @is_dev()
    @execute.command(name="block", description="Block a User")
    async def block(self, interaction: discord.Interaction, member: discord.Member):
        if blocklist.count(member.id) != 0:
            await interaction.response.send_message(f"> {member.name} is now blocked.", allowed_mentions=None, ephemeral=True)
            return
        
        blocklist.append(member.id)
        await interaction.response.send_message(f"> {member.name} is now blocked.", allowed_mentions=None, ephemeral=True)

    @is_dev()
    @execute.command(name="unblock", description="Unblock a User")
    async def unblock(self, interaction: discord.Interaction, member: discord.Member):        
        if blocklist.count(member.id) == 0:
            await interaction.response.send_message(f"> {member.name} is unblocked.", allowed_mentions=None, ephemeral=True)
            return
        
        blocklist.pop(blocklist.index(member.id))
        
        await interaction.response.send_message(f"{member.name} is unblocked.", allowed_mentions=None, ephemeral=True)
        
    @block.error
    async def block_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message("I am missing permissions to execute this command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.CommandInvokeError):
            await interaction.response.send_message("Something went wrong, check your arguments.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message("You are currently on cooldown.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.AppCommandError):
            await interaction.response.send_message("Something went wrong, try again.", ephemeral=True)
            raise error
            return
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message("I am missing permissions to execute this command.", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Unknown error, please contact the developer about this.", ephemeral=True)
            raise error
            return
        
    @unblock.error
    async def unblock_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message("I am missing permissions to execute this command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.CommandInvokeError):
            await interaction.response.send_message("Something went wrong, check your arguments.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message("You are currently on cooldown.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.AppCommandError):
            await interaction.response.send_message("Something went wrong, try again.", ephemeral=True)
            raise error
            return
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message("I am missing permissions to execute this command.", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Unknown error, please contact the developer about this.", ephemeral=True)
            raise error
            return

async def setup(bot):
    await bot.add_cog(Developer(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Developer(bot))
    print(f"> {__name__} unloaded")