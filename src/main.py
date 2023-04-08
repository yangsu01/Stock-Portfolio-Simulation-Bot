import os
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands

# # importing cogs
# from cogs.general_commands import GeneralCommands
# from cogs.stock_data_commands import StockData
# from cogs.portfolio_game_commands import PortfolioGame

# tokens
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#bot command prefix
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print('connection established!')

    # print server info
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id}) \n'
    )


@bot.event
async def on_member_join(member):
    print(f'New member {member.name} has joined the server \n')

    await member.create_dm()
    await member.dm_channel.send(f"""-This is a Work in Progress- 
    Hello there {member.name}, welcome to {GUILD}! This is a server for all things investing... and other random stuff
    If you have any feedback or suggestions, please let Bill John know! 
    To get started, type "$help" in the server for list of available commands!"""
    )


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    await load()
    await bot.start(TOKEN)


asyncio.run(main())