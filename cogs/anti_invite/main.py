import os
import typing
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
import re

def is_invite(link):
    pattern = r'(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)[a-zA-Z0-9]+'
    return re.search(pattern, link)

def is_owner(interaction: discord.Interaction):
    return interaction.user.id == interaction.guild.owner_id

class AntiInvite(commands.Cog):
    bot:commands.Bot
    
    if not os.path.exists("cogs\\anti_invite\\database"):
        os.makedirs("cogs\\anti_invite\\database")
    
    path_database:str = "cogs\\anti_invite\\database\\database.db"
    con:sqlite3.Connection = sqlite3.connect(path_database)
    cur:sqlite3.Cursor = con.cursor()
    
    def __init__(self, bot:commands.Bot) -> None:
        ...
        self.bot = bot
        
        # create table GUILDS if not exists
        self.cur.execute("""CREATE TABLE IF NOT EXISTS GUILDS(
            GUILD_ID INT PRIMARY KEY,
            TOGGLE_ANTI_INVITE BOOLEAN,
            LOG_CHANNEL INT
            )""")
        self.con.commit()
            
    def is_toggle_antiInvite(self, guild_id:int) -> bool:
        print(guild_id)
        self.cur.execute("SELECT * FROM GUILDS WHERE GUILD_ID = ?", (guild_id,))
        return bool(self.cur.fetchone()[1])
    
    def fetch_log_channel(self, guild_id:int) -> discord.TextChannel:
        self.cur.execute("SELECT * FROM GUILDS WHERE GUILD_ID = ?", (guild_id,))
        id_channel = self.cur.fetchone()[2]
        print(id_channel)
        if not id_channel:
            return None
        return self.bot.get_channel(id_channel)
    
    def set_toggle_anti_invite(self, guild_id:int, mode:bool) -> None:
        self.cur.execute("UPDATE GUILDS SET TOGGLE_ANTI_INVITE = ? WHERE GUILD_ID = ?", (mode, guild_id))
        self.con.commit()
    
    def set_log_channel(self, guild_id:int, channel_id:int) -> None:
        self.cur.execute("UPDATE GUILDS SET LOG_CHANNEL = ? WHERE GUILD_ID = ?", (channel_id, guild_id))
        self.con.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message) -> None:
        if message.author == self.bot.user:
            return
        
        if is_invite(message.content) and not message.author.guild_permissions.administrator:
            guild_id = message.guild.id
            if self.is_toggle_antiInvite(guild_id):
                await message.delete()
                await message.channel.send(f"{message.author.mention} invite link isn\'t allowed!", delete_after= 15)
                
                try:
                    channel = self.fetch_log_channel(guild_id)
                except:
                    return
                
                if not isinstance(channel, discord.TextChannel):
                    return
                
                author:discord.User = message.author
                embed:discord.Embed = discord.Embed(color= discord.Color.red(), title= "Anti Invite")
                embed.add_field(name= "author", value= f"**{author}** (**ID:** ``{author.id}``)", inline= False)
                embed.add_field(name= "content", value= f"``{message.content}``", inline= False)
                await channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.cur.execute("INSERT OR IGNORE INTO GUILDS VALUES(?, ?, ?)", (guild.id, None, None))
        self.con.commit()
    
    async def mode_autocompletion(self, interaction: discord.Interaction,
                                  current:str) -> typing.List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name= "disable", value= 0),
            app_commands.Choice(name= "enable", value= 1)
        ]
    
    @app_commands.command(name= "anti_invite", description= "just owner/moderator/admin or have permission using.")
    @app_commands.check(is_owner)
    @app_commands.autocomplete(mode= mode_autocompletion)
    async def anti_invite(self, interaction: discord.Interaction, mode:int) -> None:
        self.set_toggle_anti_invite(interaction.guild_id, mode)
        await interaction.response.send_message(f"**``{'🟢' if mode else '🔴'}AntiInvite`` **", ephemeral= True)
    
    @app_commands.command(name= "log_channel", description= "just owner/moderator/admin or have permission using.")
    async def log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"✅ {channel.mention} become a logging channel!", ephemeral= True, delete_after= 30)
        self.set_log_channel(interaction.guild_id, channel.id)

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiInvite(bot))  