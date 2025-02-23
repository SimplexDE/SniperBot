import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

from util.presets import Embed, Emote
from database.mongoclient import SpongiperClient

# TODO: refactor embeds with Embed class from util.presets
# TODO: refactor emotes with Emote class from util.presets
# TODO: redesign embed design

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.client: SpongiperClient = SpongiperClient(bot)
    
    starboard = app_commands.Group(name="starboard", description="Manage the guilds Starboard Settings")
    
    quote = app_commands.Group(name="quote", description="Manage the guilds Quote Settings")
    
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
                f"{Emote.INFO} <:info:1226139199351296051> Links",
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
            timestamp=datetime.now(),
            fields=fields,
        )
        
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
        
        embed = discord.Embed(
            title="Starboard",
            description="",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(
            name=f"{Emote.RIGHT_ARROW} Starboard-Channel",
            value="> - `N/A` <:edit:1210725875625099304>",
            inline=False
        )
        embed.add_field(
            name=f"{Emote.STAR} Stars needed per Message",
            value=f"> - {stars} {Emote.STAR}",
            inline=False
        )
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed)
    
    @starboard.command(name="set", description="Set the Starboard channel (& activate)")
    @app_commands.default_permissions(manage_channels=True)
    async def starboard_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        if "stars" not in settings:
            settings["stars"] = 3
        
        stars = settings["stars"]
        
        embed = discord.Embed(
            title="Starboard",
            description="",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(
            name=f"{Emote.RIGHT_ARROW} Starboard-Channel",
            value=f"> - {channel.mention} <:edit:1210725875625099304>",
            inline=False
        )
        embed.add_field(
            name=f"{Emote.STAR} Stars needed per Message",
            value=f"> - {stars} {Emote.STAR}",
            inline=False
        )
        
        settings["starboard_channel"] = channel.id
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed)
        
    @quote.command(name="set", description="Disable the Quoting")
    @app_commands.default_permissions(manage_channels=True)
    async def quote_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        embed = discord.Embed(
            title="Quote",
            description="",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(
            name="<:helioschevronright:1267515447406887014> Quote-Channel",
            value=f"> - {channel.mention} <:edit:1210725875625099304>",
            inline=False
        )
        
        settings["quote_channel"] = channel.id
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed)
        
    @quote.command(name="unset", description="Set the Quote channel (& activate)")
    @app_commands.default_permissions(manage_channels=True)
    async def quote_unset(self, interaction: discord.Interaction):
        
        db_guild = await self.client.get_guild(interaction.guild.id)
        settings = db_guild.settings
        
        embed = discord.Embed(
            title="Quote",
            description="",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(
            name="<:helioschevronright:1267515447406887014> Quote-Channel",
            value="> - `N/A` <:edit:1210725875625099304>",
            inline=False
        )
        
        settings["quote_channel"] = None
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed)


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
        
        embed = discord.Embed(
            title="Starboard",
            description="",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(
            name="<:helioschevronright:1267515447406887014> Starboard-Channel",
            value=f"> - {starboard_channel.mention if starboard_channel is not None else "Not Set (set with `/starboard`)"}",
            inline=False
        )
        embed.add_field(
            name="<:heliosmedal:1267515459012657245> Stars needed to be starred",
            value=f"> - {stars} :star: <:edit:1210725875625099304>",
            inline=False
        )
        
        settings["stars"] = stars
        
        db_guild.settings = settings
        
        await interaction.response.send_message(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")