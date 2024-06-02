
#?  __  __       _             _           _
#? |  \/  | __ _(_)_ __       | |__   ___ | |_
#? | |\/| |/ _` | | '_ \ _____| '_ \ / _ \| __|
#? | |  | | (_| | | | | |_____| |_) | (_) | |_
#? |_|  |_|\__,_|_|_| |_|     |_.__/ \___/ \__|
#!    version: v1.0
#!    author: annotfound
#!    github: null


title:str= r"""
   __  __       _             _           _
  |  \/  | __ _(_)_ __       | |__   ___ | |_
  | |\/| |/ _` | | '_ \ _____| '_ \ / _ \| __|
  | |  | | (_| | | | | |_____| |_) | (_) | |_
  |_|  |_|\__,_|_|_| |_|     |_.__/ \___/ \__|
"""
version:float = 1.0
author:str = "annguyen2k8"
github:str = "null"

from discord.ext import commands    
from discord import app_commands
import discord
import asyncio
from config import *
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

#*  Clean terminal

os.system('cls' if os.name == 'nt' else 'clear')

#* Print banner

print(f"""\33[94m\33[1m{title}\33[0m
    \33[90mverson:\33[0m\33[1m v{version}\33[0m 
    \33[90mauthor:\33[0m\33[1m {author}\33[0m 
    \33[90mgithub:\33[0m\33[1m {github}\33[0m 
""")

#* Setup logging

logger = logging.getLogger('discord') 
logger.setLevel(logging.INFO) 

handler = logging.StreamHandler()
format_handler = '\33[90m%(asctime)s \33[0m\33[94m%(levelname)s\33[0m \33[95m%(name)s\33[0m %(message)s'
handler.setFormatter(logging.Formatter(format_handler, datefmt='%Y-%m-%d %H:%M:%S'))

logger.addHandler(handler)

#* Nah its bad to save your disk (maybe)

# current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# log_file = f"logs\\log_{current_time}.log"
# file_handler = RotatingFileHandler(log_file, encoding='utf-8', mode='a', backupCount= 2, maxBytes= 5*5*1024)
# file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

# logger.addHandler(file_handler)


#* Setup bot

bot = commands.Bot(command_prefix= prefix,
                   intents= discord.Intents.all(), 
                   help_command= None)


@bot.event
async def on_connect():
    
    #* Loop print ping about 5min/time (you can option)
    
    logger_ = logging.getLogger('discord.ping') 
    while True:
        logger_.info(f'Ping {round(bot.latency * 1000)}ms')
        await asyncio.sleep(300)

@bot.event
async def on_ready():
    global handler
    logger_ = logging.getLogger('discord.on_ready') 
    logger_.info(f"Logged bot's {bot.user} (ID: {bot.application.id})")
    
    try:
        sync = await bot.tree.sync()
        logger_c = logging.getLogger('discord.commands') 
        logger_c.info(f"{len(sync)} commands")
    except Exception as e:
        logger_.error(e)
    
    #* Loop change status
    
    bot_status = ["type in \"!help\" for help.", 
              "{:1.0f} guilds | with {:1.0f} users".format(len(bot.guilds),
                        sum([guild.member_count for guild in bot.guilds]))]
    
    
    while True:
        for name in bot_status:
            await bot.change_presence(
                status=discord.Status.online, 
                activity= discord.CustomActivity(name= name))
            await asyncio.sleep(30)
        
        

#* Process error (cooldown, error appcommands)

@bot.tree.error
async def on_app_command_error(interacrion:discord.Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        await interacrion.response.send_message('you must wait for ``{:0.1f}s`` to use it!'.format(error.retry_after), ephemeral= True)
    if isinstance(error, app_commands.errors.CheckFailure):
        await interacrion.response.send_message('you have no **PERMISSION** to use it.', ephemeral= True)
    else:
        raise error

#* Manage cogs system

def is_owner_bot(interaction: discord.Interaction):
    return interaction.user.id == bot.application.owner.id

@bot.tree.command(name='reload_extension', description= 'just owner use.')
@app_commands.check(is_owner_bot)
async def reload_cogs(interaction:discord.Interaction):
    global handler
    logger_ = logging.getLogger('discord.cogs') 
    for folder in os.listdir('.\\cogs'):
        await bot.reload_extension(f'cogs.{folder}.main')
        logger_.info(f'{folder} is reloaded!')
    await interaction.response.send_message('all extensions war reloaded!', ephemeral= True)

async def load_cogs():
    global handler
    logger_ = logging.getLogger('discord.cogs') 
    
    for folder in os.listdir('.\\cogs'):
        await bot.load_extension(f'cogs.{folder}.main')
        logger_.info(f'{folder} is loaded!')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main()) 