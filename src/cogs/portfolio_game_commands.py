import discord
from discord.ext import commands

from .functions.portfolio_game import (check_user_exists, create_user_profile, profile_summary,
                                       buy_stock, sell_stock, get_price, get_available_funds)

# constants
from .functions.constants import STARTING_FUNDS


class PortfolioGame(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._last_member = None

    @commands.command(name='rule',
                      help='- Rules of the game!')
    async def sim_rule(self, ctx):
        rules = (f"""Create an investment portfolio and watch it grow!
        Type command: '***$pcreate***' to initialize your profile.
        Start with ***${STARTING_FUNDS}*** and buy/sell your way to victory!
        Show your financial dominance by out-performing your friends' portfolios!
        > No comissions or fees when buying/selling
        > Cannot buy partial shares
        > If buying/selling after market close, closing price will be used.""")
        
        message = discord.Embed(color=0xa3a3ff,
                                title=':chart_with_upwards_trend: Investing Game Rules :chart_with_upwards_trend:',
                                description=rules)

        await ctx.send(embed=message)

    @commands.command(name='create',
                      help='- creates a portfolio for the simulation :)')
    async def create_port(self, ctx):
        try:
            if check_user_exists(ctx.message.author.name):    
                await ctx.send('User profile already exists!')
            else:
                create_user_profile(ctx.message.author.name)
                await ctx.send('Profile created!')

        except Exception as e:
            print(e)
            await ctx.send(e)

    # TODO customize summary message
    # TODO add real time portfolio value, plot portfolio performance
    @commands.command(name='summary',
                      help='- summarizes a users portfolio')
    async def port_sum(self, ctx, *, 
                       username: str=commands.parameter(description='- discord username')):
        try:
            if check_user_exists(username):
                profile = profile_summary(username)
                summary = f"***{username}'s*** portfolio summary:\n"

                for key,value in profile.items():
                    summary += f'> {key}: {value}\n'

                await ctx.send(summary)

            else:
                await ctx.send(f'{username} does not have a profile!')

        except Exception as e:
            print(e)
            await ctx.send(e)
    
    @commands.command(name='buy',
                      help='- buy some shares!')
    async def buy(self, ctx, 
                  ticker: str=commands.parameter(description='- stock ticker')):
        try:
            price = get_price(ticker)
            funds = get_available_funds(ctx.message.author.name)
            await ctx.send(f"""> The current price of {ticker} is ${price}.
            > You have ${funds} available to be invested.
            > With this money, you can buy a maximum of {int(funds/price)} shares.
            > How many shares would you like to buy? (N to cancel transaction)""")

        except Exception as e:
            await ctx.send(e)
        
async def setup(bot):
    await bot.add_cog(PortfolioGame(bot))