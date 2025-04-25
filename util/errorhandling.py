import discord
from discord import app_commands
from util.logger import log

async def handle_error(interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message("I am missing permissions to execute this command.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You are missing permissions to execute this command", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message("You are currently on cooldown.", ephemeral=True)
            return
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message("I am not allowed to do that.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.AppCommandError):
            await interaction.response.send_message("Something went wrong, try again.", ephemeral=True)
            log.exception(error)
            return
        elif isinstance(error, app_commands.errors.CommandInvokeError):
            await interaction.response.send_message("Something went wrong, check your arguments.", ephemeral=True)
            return
        elif isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Unknown error, please contact the developer about this.", ephemeral=True)
            log.exception(error)
            return