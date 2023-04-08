import random
import os
import discord
from discord.ext import commands

# constants
VIDEO_PATH = "C:/Users/Yang/Documents/Projects/discord bot/videos/"

class GeneralCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._last_member = None

    @commands.command(name='hello',
                      help='- bot says hello')
    async def hello(self, ctx):
        await ctx.send('hello sexy')

    @commands.command(name='replay',
                      help='- sends a nutty video')
    async def replay(self, ctx):
        try:
            await ctx.send(file=discord.File(f"{VIDEO_PATH}{random.choice([x for x in os.listdir(VIDEO_PATH) if os.path.isfile(os.path.join(VIDEO_PATH, x))])}"))

        except Exception as e:
            print(e)
            await ctx.send(e)


async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
