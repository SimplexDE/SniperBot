import discord
from discord import app_commands
from discord.ext import commands

from util.constants import Emote

# TODO: refactor all old execute commands to the new execute group

image_exts = [".jpg", ".png", ".jpeg", ".webp", ".gif"]
ATTACHMENTS_SRC = "./attachments"

blocklist = []

class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    execute = app_commands.Group(name="execute", description="Developer Commands", 
                                allowed_contexts=(app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True)),
                                allowed_installs=app_commands.AppInstallationType(guild=False, user=True))
    
    @execute.command(name="block", description="Block a User")
    async def block(self, interaction: discord.Interaction, member: discord.Member):
        
        # TODO: Turn this into a check
        if interaction.user.id != 579111799794958377:
            await interaction.response.send_message(f"> {Emote.WARNING} Du hast keinen Zugriff auf diesen Befehl.", ephemeral=True)
            return
        
        if blocklist.count(member.id) != 0:
            await interaction.response.send_message(f"> {member.name} ist nun geblockt.", allowed_mentions=None, ephemeral=True)
            return
        
        blocklist.append(member.id)
        await interaction.response.send_message(f"> {member.name} ist nun geblockt.", allowed_mentions=None, ephemeral=True)

    @execute.command(name="unblock", description="Unblock a User")
    async def unblock(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id != 579111799794958377:
            await interaction.response.send_message(f"> {Emote.WARNING} Du hast keinen Zugriff auf diesen Befehl.", ephemeral=True)
            return
        
        if blocklist.count(member.id) == 0:
            await interaction.response.send_message(f"> {member.name} ist nun entblockt.", allowed_mentions=None, ephemeral=True)
            return
        
        blocklist.pop(blocklist.index(member.id))
        
        await interaction.response.send_message(f"{member.name} ist nun entblockt.", allowed_mentions=None, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Developer(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Developer(bot))
    print(f"> {__name__} unloaded")