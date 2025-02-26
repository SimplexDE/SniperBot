import discord
from discord.app_commands import check

from util.constants import VIP

def is_dev():
    async def predicate(interaction: discord.Interaction):
        return str(VIP.DEVELOPER) == str(interaction.user.id)
    return check(predicate)