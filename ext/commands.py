import discord
from discord.ext import commands
from discord import app_commands

from util.embed import Embed
from util.constants import Emote
from util.logger import log
from database.mongoclient import SpongiperClient

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.client: SpongiperClient = SpongiperClient(bot)
    
    starboard = app_commands.Group(name="starboard", description="Manage the guilds Starboard Settings", 
                                allowed_contexts=(app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True)),
                                allowed_installs=app_commands.AppInstallationType(guild=True, user=False))
    
    quote = app_commands.Group(name="quote", description="Manage the guilds Quote Settings", 
                                allowed_contexts=(app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True)),
                                allowed_installs=app_commands.AppInstallationType(guild=True, user=False))
    
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.command(name="about", description="About me")
    async def about(self, interaction: discord.Interaction):
        DEV = self.bot.get_user(579111799794958377)
    
        fields = [
            (
                f"{Emote.INFO} General Information",
                f"> - `Bot Name:` *{self.bot.user.name}#{self.bot.user.discriminator}*" + 
                f"\n> - `Bot ID:` *{self.bot.user.id}*" +
                f"\n> - `Developer:` *{DEV.name}*" + 
                f"\n> - `Developer ID:` *{DEV.id}*",
                False
            ),
            (
                f"{Emote.INFO} Links",
                "> - [GitHub](https://github.com/SimplexDE/SniperBot)" + 
                "\n> - [Invite me](https://discord.com/oauth2/authorize?client_id=862859543700176896&permissions=274878024704&integration_type=0&scope=bot+applications.commands)",
                False
            )
            ]
    
        embed = Embed(
            title="🧑‍💻 Simplex",
            title_url=f"https://discord.com/users/{DEV.id}",
            title_icon_url=f"{DEV.avatar.url}",
            alt_title=f"About {self.bot.user.name}",
            image_url=self.bot.user.avatar.url,
            footer="Licensed under MIT",
            footer_icon_url=self.bot.user.avatar.url,
            color=discord.Color.blue(),
            fields=fields,
        )
        
        await interaction.response.send_message(embed=embed.StandardEmbed())

    @app_commands.command(name="nsfw", description="Toggle if NSFW Content is allowed")
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.default_permissions(manage_channels=True)
    async def nsfw_toggle(self, interaction: discord.Interaction):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        if "nsfw_allow" not in settings:
            settings["nsfw_allow"] = False
        settings["nsfw_allow"] = False if settings["nsfw_allow"] else True

        nsfw_allowed = Emote.CHECK if settings["nsfw_allow"] else Emote.UNCHECK
        
        fields = [
            (f"{Emote.NSFW} NSFW", f"> {nsfw_allowed} {Emote.EDIT}", False)
            ]
        
        embed = Embed(
            title="Settings | NSFW",
            color=discord.Color.blue(),
            fields=fields
        )
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed.StandardEmbed())

    @starboard.command(name="unset", description="Disable the Starboard")
    @app_commands.default_permissions(manage_channels=True)
    async def starboard_unset(self, interaction: discord.Interaction):
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
    
        settings["starboard_channel"] = None
        
        if "stars" not in settings: 
            settings["stars"] = 3
        stars = settings["stars"]
        
        if "nsfw_allow" not in settings:
            settings["nsfw_allow"] = False
        
        nsfw_allowed = Emote.CHECK if settings["nsfw_allow"] else Emote.UNCHECK
        
        fields = [
            (f"{Emote.RIGHT_ARROW} Channel", f"> `N/A` {Emote.EDIT}", False),
            (f"{Emote.STAR} Minimum Stars", f"> {stars} {Emote.STAR}", False),
            (f"{Emote.NSFW} NSFW", f"> {nsfw_allowed}" , False)
            ]
        
        embed = Embed(
            title="Settings | Starboard",
            color=discord.Color.blue(),
            fields=fields
        )
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed.StandardEmbed())
    
    @starboard.command(name="set", description="Set the Starboard channel (& activate)")
    @app_commands.default_permissions(manage_channels=True)
    async def starboard_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        if "stars" not in settings:
            settings["stars"] = 3
        
        stars = settings["stars"]
        
        if "nsfw_allow" not in settings:
            settings["nsfw_allow"] = False
        
        nsfw_allowed = Emote.CHECK if settings["nsfw_allow"] else Emote.UNCHECK
        
        
        fields = [
            (f"{Emote.RIGHT_ARROW} Channel", f"> {channel.mention} {Emote.EDIT}", False),
            (f"{Emote.STAR} Minimum Stars", f"> {stars} {Emote.STAR}", False),
            (f"{Emote.NSFW} NSFW", f"> {nsfw_allowed}" , False)
            ]
        
        embed = Embed(
            title="Settings | Starboard",
            color=discord.Color.blue(),
            fields=fields
        )
        
        settings["starboard_channel"] = channel.id
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed.StandardEmbed())

    @starboard.command(name="stars", description="Set the needed stars")
    @app_commands.default_permissions(manage_channels=True)
    async def stars(self, interaction: discord.Interaction, stars: int):
        
        starboard_channel = None
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        if "starboard_channel" not in settings:
            settings["starboard_channel"] = None
            
        if settings["starboard_channel"] is not None:
            starboard_channel = self.bot.get_channel(settings["starboard_channel"])
        
        if "nsfw_allow" not in settings:
            settings["nsfw_allow"] = False
        
        nsfw_allowed = Emote.CHECK if settings["nsfw_allow"] else Emote.UNCHECK
        
        fields = [
            (f"{Emote.RIGHT_ARROW} Channel", f"> {starboard_channel.mention if starboard_channel is not None else "`N/A` (set with `/starboard set`)"}", False),
            (f"{Emote.STAR} Minimum Stars", f"> {stars} {Emote.STAR} {Emote.EDIT}", False),
            (f"{Emote.NSFW} NSFW", f"> {nsfw_allowed}" , False)
            ]
        
        embed = Embed(
            title="Settings | Starboard",
            color=discord.Color.blue(),
            fields=fields
        )
        
        settings["stars"] = stars
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed.StandardEmbed())
        
    @quote.command(name="set", description="Enable the Quoting")
    @app_commands.default_permissions(manage_channels=True)
    async def quote_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        fields = [
            (f"{Emote.ARROW_RIGHT} Channel", f"> {channel.mention} {Emote.EDIT}", False),
            ]
        
        embed = Embed(
            title="Settings | Quote",
            color=discord.Color.blue(),
            fields=fields
        )
        
        settings["quote_channel"] = channel.id
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed.StandardEmbed())
        
    @quote.command(name="unset", description="Disable the Quoting")
    @app_commands.default_permissions(manage_channels=True)
    async def quote_unset(self, interaction: discord.Interaction):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        fields = [
            (f"{Emote.ARROW_RIGHT} Channel", f"> `N/A` {Emote.EDIT}", False),
            ]
        
        embed = Embed(
            title="Settings | Quote",
            color=discord.Color.blue(),
            fields=fields
        )
        
        settings["quote_channel"] = None
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed.StandardEmbed())

    @about.error
    async def about_error(self, interaction: discord.Interaction, error: Exception):
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
        
    @starboard_set.error
    async def starboard_set_error(self, interaction: discord.Interaction, error: Exception):
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

    @starboard_unset.error
    async def starboard_unset_error(self, interaction: discord.Interaction, error: Exception):
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
        
    @stars.error
    async def stars_error(self, interaction: discord.Interaction, error: Exception):
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

    @quote_set.error
    async def quote_set_error(self, interaction: discord.Interaction, error: Exception):
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
        
    @quote_unset.error
    async def quote_unset_error(self, interaction: discord.Interaction, error: Exception):
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
    await bot.add_cog(Commands(bot))
    log.debug(f"{__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    log.debug(f"{__name__} unloaded")