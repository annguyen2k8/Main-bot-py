import os
import typing
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands

class AntiInvite(commands.Cog):
    bot:commands.Bot
    
    if not os.path.exists("cogs\\anti_invite\\database"):
        os.makedirs("cogs\\anti_invite\\database")
    
    path_database:str = "cogs\\anti_invite\\database\\database.db"
    con:sqlite3.Connection = sqlite3.connect(path_database)
    cur:sqlite3.Cursor = con.cursor()
    
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        
        # create table GUILDS if not exists
        self.cur.execute("""CREATE TABLE IF NOT EXISTS GUILDS(
            GUILD_ID INT PRIMARY KEY,
            TOGGLE_ANTI_INVITE BOOLEAN
            )""")
        self.con.commit()
    
    def is_toggle_antiInvite(self, guild_id:int):
        print(guild_id)
        self.cur.execute("SELECT * FROM GUILDS WHERE GUILD_ID = ?", (guild_id,))
        return self.cur.fetchone()[1]
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author == self.bot.user:
            return
        if 'discord.gg' in message.content and not message.author.guild_permissions.administrator:
            if self.is_toggle_antiInvite(message.guild.id):
                await message.delete()
                await message.channel.send(f"{message.author.mention} invite link is not allowed!", delete_after= 30)
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.cur.execute("INSERT OR IGNORE INTO GUILDS VALUES(?, ?)", (guild.id, None))
        self.con.commit()
        discord.PermissionOverwrite
    
    async def mode_autocompletion(self, interaction: discord.Interaction,
                                  current:str) -> typing.List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name= "disable", value= 0),
            app_commands.Choice(name= "enable", value= 1)
        ]
    
    @app_commands.command(name= "anti_invite", description= "just owner/moderator/admin or have permission using.")
    @app_commands.autocomplete(mode= mode_autocompletion)
    async def anti_invite(self, interaction: discord.Interaction, mode:int):
        mode:bool = bool(mode)
        await interaction.response.send_message(f"**{'enable' if mode else 'disable'}** Anti Invite ``will delete any link invite discord. \nIf you have channel public invite, please set permission``**``  ``**")
        self.cur.execute("UPDATE GUILDS SET TOGGLE_ANTI_INVITE = ? WHERE GUILD_ID = ?", (mode, interaction.guild_id))
        self.con.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiInvite(bot))