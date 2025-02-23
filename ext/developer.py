import discord
from discord import app_commands
from discord.ext import commands

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
        if interaction.user.id != 579111799794958377:
            await interaction.response.send_message("> Du hast keinen Zugriff auf diesen Befehl.", ephemeral=True)
            return
        
        if blocklist.count(member.id) != 0:
            await interaction.response.send_message(f"> {member.name} ist nun geblockt.", allowed_mentions=None, ephemeral=True)
            return
        
        blocklist.append(member.id)
        await interaction.response.send_message(f"> {member.name} ist nun geblockt.", allowed_mentions=None, ephemeral=True)

    @execute.command(name="unblock", description="Unblock a User")
    async def unblock(self, interaction: discord.Interaction, member: discord.Member):
        blocklist.pop(blocklist.index(member.id))
        
        await interaction.response.send_message(f"{member.name} ist nun entblockt.", allowed_mentions=None, ephemeral=True)

    
    # @app_commands.command(name="execute", description="Dev-Terminal")
    # async def execute(self, interaction: discord.Interaction, input: str):
    #     if interaction.user.id != 579111799794958377:
    #         await interaction.response.send_message("Du hast keinen Zugriff auf diesen Befehl.", ephemeral=True)
    #         return
        
    #     arguments = input.split(" ", maxsplit=3)
    #     if len(arguments) >= 3:
    #         arguments.pop(2)
    #     print(arguments)
        
    #     match (arguments[0]):
    #         case ("clear" | "666"): # Clears the current message in cache
    #             self.last_message[interaction.guild.id] = {}
    #             self.last_sent_from_bot[interaction.guild.id] = {}
    #             self.last_sent[interaction.guild.id] = {}
    #             await interaction.response.send_message(f"Ich habe `{arguments[0]}` ausgeführt.", delete_after=10)
            
    #         case ("block"):
    #             if len(arguments) < 2:
    #                 await interaction.response.send_message(f"Zu wenig Argumente um {arguments[0]} auszuführen.", delete_after=10)
    #                 return
                
    #             user = self.bot.get_user(int(arguments[1]))
                
    #             if self.blocklist.count(user.id) != 0:
    #                 await interaction.response.send_message(f"Ich habe `{arguments[0]}` ausgeführt. {user.name} ist nun geblockt.", allowed_mentions=None, delete_after=10)
    #                 return
                
    #             self.blocklist.append(user.id)
    #             await interaction.response.send_message(f"Ich habe `{arguments[0]}` ausgeführt. {user.name} ist nun geblockt.", allowed_mentions=None, delete_after=10)
                
    #         case ("unblock"):
    #             if len(arguments) < 2:
    #                 await interaction.response.send_message(f"Zu wenig Argumente um {arguments[0]} auszuführen.", delete_after=10)
    #                 return
                
    #             user = self.bot.get_user(int(arguments[1]))
    #             self.blocklist.pop(self.blocklist.index(user.id))
                
    #             await interaction.response.send_message(f"Ich habe `{arguments[0]}` ausgeführt. {user.name} ist nun entblockt.", allowed_mentions=None, delete_after=10)
                
    #         case ("1337"): # Cleans the attachmentsfolder
    #             for server_dir in os.listdir(f"{ATTACHMENTS_SRC}/"):
    #                 if len(os.listdir(f"{ATTACHMENTS_SRC}/{server_dir}")) == 0:
    #                     os.rmdir(f"{ATTACHMENTS_SRC}/{server_dir}")
    #                     continue
                        
    #                 for channel_dir in os.listdir(f"{ATTACHMENTS_SRC}{server_dir}"):
    #                     if len(os.listdir(f"{ATTACHMENTS_SRC}/{server_dir}/{channel_dir}")) == 0:
    #                         os.rmdir(f"{ATTACHMENTS_SRC}/{server_dir}/{channel_dir}")
    #                         continue
                            
    #                     for image_file in os.listdir(f"{ATTACHMENTS_SRC}/{server_dir}/{channel_dir}"):
    #                         os.remove(f"{ATTACHMENTS_SRC}/{server_dir}/{channel_dir}/{image_file}")
                            
    #                     if len(os.listdir(f"{ATTACHMENTS_SRC}/{server_dir}/{channel_dir}")) == 0:
    #                         os.rmdir(f"{ATTACHMENTS_SRC}/{server_dir}/{channel_dir}")
    #                         continue
                    
    #                 if len(os.listdir(f"{ATTACHMENTS_SRC}/{server_dir}")) == 0:
    #                     os.rmdir(f"{ATTACHMENTS_SRC}/{server_dir}")
    #                     continue
    #             await interaction.response.send_message(f"Ich habe `{arguments[0]}` ausgeführt.", delete_after=10)
                    
    #         case ("populate"):
    #             if not self.message_cache.get(interaction.channel.id):
    #                 self.message_cache[interaction.channel.id] = []
    #             self.message_cache[interaction.channel.id] = [message async for message in interaction.channel.history(limit=100)]
    #             await interaction.response.send_message(f"Ich habe `{arguments[0]}` ausgeführt.", delete_after=10)
                    
    #         case (_):
    #             await interaction.response.send_message(f"Ich konnte `{arguments[0]}` nicht zuordnen.", delete_after=10)
    #             return
        
async def setup(bot):
    await bot.add_cog(Developer(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Developer(bot))
    print(f"> {__name__} unloaded")