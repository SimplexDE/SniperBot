import discord
from discord import ui

class NukeConfirmView(ui.View):
    def __init__(self, bot, user: discord.User, channel: discord.TextChannel):
        super().__init__(
            timeout=120
        )
        self.deletebutton = ui.Button(
            style=discord.ButtonStyle.danger,
            row=1,
            label="Nuke!",
        )
        self.cancelbutton = ui.Button(
            style=discord.ButtonStyle.gray,
            row=1,
            label="Cancel",
        )
        
        self.add_item(self.deletebutton)
        self.add_item(self.cancelbutton)
        
        self.bot = bot
        self.user = user.id
        self.channel = channel

        self.deletebutton.callback = self.delete_callback
        self.cancelbutton.callback = self.cancel_callback
        
    async def interaction_check(self, interaction: discord.Interaction):
        if self.user != interaction.user.id:
            await interaction.response.send_message("> :warning: Du hast kein Zugriff auf dieses Menü", ephemeral=True, delete_after=3)
            return False
        return True
        
    async def delete_callback(self, interaction: discord.Interaction):
        self.deletebutton.disabled = True
        self.cancelbutton.disabled = True
        
        await interaction.response.send_message("nuking")
        
        await self.channel.clone(reason="Channel was nuked.")
        await self.channel.delete(reason="Channel was nuked.")
        
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelled...", ephemeral=True,delete_after=5)
        self.stop()
        
    async def on_timeout(self):
        self.stop()
        