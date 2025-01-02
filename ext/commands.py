import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        
    @app_commands.command(name="about", description="About me")
    async def about(self, interaction: discord.Interaction):
        DEV = self.bot.get_user(579111799794958377)
        
        embed = discord.Embed(
            title=f"About {self.bot.user.name}",
            color=discord.Color.blue(),
            description="",
            timestamp=datetime.now(),
        )
        
        embed.add_field(
            name="<:info:1226139199351296051> General Information",
            value=f"> - `Bot Name:` *{self.bot.user.name}#{self.bot.user.discriminator}*" + 
                f"\n> - `Bot ID:` *{self.bot.user.id}*" +
                f"\n> - `Developer:` *{DEV.name}*" + 
                f"\n> - `Developer ID:` *{DEV.id}*",
            inline=False
        )
        
        embed.add_field(
            name="<:info:1226139199351296051> Links",
            value="> - [GitHub](https://github.com/SimplexDE/SniperBot)" + 
                "\n> - [Invite me](https://discord.com/oauth2/authorize?client_id=862859543700176896&permissions=274878024704&integration_type=0&scope=bot+applications.commands)",
            inline=False
        )
        
        embed.set_author(name="🧑‍💻 Simplex", url=f"https://discord.com/users/{DEV.id}", icon_url=DEV.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Licsensed under MIT", icon_url=self.bot.user.avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")