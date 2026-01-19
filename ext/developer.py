import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional

from util.checks import is_dev
from util.errorhandling import handle_error
from util.logger import log

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]
ATTACHMENTS_SRC = "./attachments"

blocklist = []

class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    execute = app_commands.Group(name="sudo", description="Developer Commands", 
                                allowed_contexts=(app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True)),
                                allowed_installs=app_commands.AppInstallationType(guild=False, user=True))
    
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

    @is_dev()
    @execute.command(name="say", description="Say something as Spongiper")
    async def say(self, interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel]):
        chn = interaction.channel
        if channel:
            chn = channel
        
        await chn.send(message)
        await interaction.response.send_message(">_<", ephemeral=True)
    
    @is_dev()
    @execute.command(name="leave", description="Let the bot leave a specific server")
    async def leave(self, interaction: discord.Interaction, id: str):
        guild = await self.bot.get_guild(id)
        
        if guild is None:
            await interaction.response.send_message("Falsche ID UwU >_<", ephemeral=True)
            return
        
        await interaction.response.send_message("Bye Bye >_<", ephemeral=True)
        await guild.system_channel.send("Bye Bye ¯\\_(ツ)_/¯")
        await guild.leave()
        
    @is_dev()
    @execute.command(name="scuttle", description="Leave the current server immediately")
    async def scuttle(self, interaction: discord.Interaction):
        await interaction.response.send_message("Evacuating <:critical:1226665487988031508>", ephemeral=True)
        await interaction.channel.send("Evacuating this server <:critical:1226665487988031508>")
        await interaction.guild.leave()

    @say.error
    async def say_error(self, interaction: discord.Interaction, error: Exception):
        await handle_error(interaction, error)
        
    @leave.error
    async def leave_error(self, interaction: discord.Interaction, error: Exception):
        await handle_error(interaction, error)
        
    @scuttle.error
    async def scuttle_error(self, interaction: discord.Interaction, error: Exception):
        await handle_error(interaction, error)
    
    @block.error
    async def block_error(self, interaction: discord.Interaction, error: Exception):
        await handle_error(interaction, error)
        
    @unblock.error
    async def unblock_error(self, interaction: discord.Interaction, error: Exception):
        await handle_error(interaction, error)

async def setup(bot):
    await bot.add_cog(Developer(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Developer(bot))
    log.debug(f"{__name__} unloaded")