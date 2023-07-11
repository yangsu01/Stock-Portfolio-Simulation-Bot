import discord
from discord.ext import commands
import pandas as pd
import numpy as np
import dataframe_image as dfi
import datetime as dt

from functions.portfolio_game import (check_user_exists, create_user_profile, profile_summary,
                                       buy_stock, sell_stock, get_available_funds, check_user_owns_stock, get_stock_info)
from functions.stock_info import get_price

# constants
from functions.constants import STARTING_FUNDS, STOCK_TABLE_PATH


class PortfolioGame(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._last_member = None

    # rules of the game
    @commands.command(name='rule',
                      help='- Rules of the game!')
    async def sim_rule(self, ctx):
        rules = f"""Create an investment portfolio and watch it grow!
        Type command: '***$create***' to initialize your profile.
        Start with ***${STARTING_FUNDS}*** and buy/sell your way to victory!
        Show your financial dominance by out-performing your friends' portfolios!
        > No comissions or fees when buying/selling
        > Cannot buy partial shares
        > If buying/selling after market close, closing price will be used."""
        
        message = discord.Embed(color=0xa3a3ff,
                                title=':chart_with_upwards_trend: Investing Game Rules :chart_with_upwards_trend:',
                                description=rules)

        await ctx.send(embed=message)

    # create user profile
    @commands.command(name='create',
                      help='- creates a portfolio for the simulation :)')
    async def create_port(self, ctx):
        try:
            if create_user_profile(ctx.message.author.name):
                await ctx.send('Profile created!')
            else:
                await ctx.send('User profile already exists!')
        except Exception as e:
            await ctx.send(e)

    # summarizes user portfolio
    @commands.command(name='summary',
                      help='- summarizes a users portfolio')
    async def port_sum(self, ctx, *, 
                       username: str=commands.parameter(description='- discord username')):
        try:
            if check_user_exists(username):
                summary = profile_summary(username)
                response = f"""Portfolio performance on {dt.datetime.now().strftime('%A %b %d %Y, %H:%M:%S')}
                    > ***Date Created***: {summary['create_date']}
                    > ***Funds Available***: ${round(summary['funds_available'],2)}
                    > ***Total Market Value of Portfolio***: ${round(summary['current_value'],2)}
                    
                    Here's the breakdown:"""
                
                current_values = summary['current_stock_values']
                portfolio = summary['portfolio']
                data = []
                for ticker in portfolio:
                    average_price = portfolio[ticker]['average_price']
                    current_price = current_values[ticker]
                    num_shares = portfolio[ticker]['shares']

                    data.append([portfolio[ticker]['name'],
                                ticker,
                                portfolio[ticker]['currency'],
                                round(average_price, 2),
                                round(current_price, 2),
                                round((current_price-average_price)/average_price, 2),
                                round((current_price-average_price)*num_shares, 2),
                                round(current_price*num_shares, 2)
                    ])

                columns = ['Name', 'Currency', 'Ticker', 'Average Price', 'Market Price', 'Change (%)', 'Total Change', 'Market Value']
                df = pd.DataFrame(data, columns=columns).set_index('Name')
                dfi.export(df, STOCK_TABLE_PATH)
                
                message = discord.Embed(color=0xa3a3ff,
                                        title=f":money_mouth: {username}'s Portfolio Summary :money_mouth:",
                                        description=response)
                file = discord.File(STOCK_TABLE_PATH, filename="stock_summary_table.jpg")
                message.set_image(url=f'attachment://stock_summary_table.jpg')
                await ctx.send(file=file, embed=message)
            else:
                await ctx.send(f'{username} does not have a profile! Please create one with ***$create*** first.')

        except Exception as e:
            await ctx.send(e)
    
    # buy a stock
    @commands.command(name='buy',
                      help='- buy some shares!')
    async def buy(self, ctx, 
                  ticker: str=commands.parameter(description='- stock ticker')):
        try:
            if check_user_exists(ctx.message.author.name):
                price = get_price(ticker)
                funds = round(get_available_funds(ctx.message.author.name),2)
                
                await ctx.send(f"""> The current price of ***{ticker.upper()}*** is ***${round(get_price(ticker), 2)}***
                               > You have ***${funds}*** available to be invested.
                               > With this money, you can buy a maximum of ***{int(funds/price)} shares***.
                               > **How many shares would you like to buy?** (enter a whole number... 'no' to cancel transaction)""")

                response = await self.bot.wait_for('message',
                                                check=lambda message:message.author == ctx.author and message.channel.id == ctx.channel.id,
                                                timeout=20.0)
                
                if response.content in ['n', 'N', 'No', 'NO', 'no']:
                    await ctx.send('Transaction Cancelled')
                elif int(response.content) > int(funds/price):
                    await ctx.send(f'You cant afford {int(response.content)} shares right now')
                else:
                    buy_stock(ctx.message.author.name, ticker, int(response.content), price)
                    await ctx.send(f'Congrats, you just bought {int(response.content)} shares of {ticker} at {price}!')
            else:
                await ctx.send('You do not have a profile! Create one with ***$create***')

        except Exception as e:
            await ctx.send(e)

    # sell a stock
    @commands.command(name='sell',
                      help='- sell some shares!')
    async def sell(self, ctx,
                   ticker: str=commands.parameter(description='- stock ticker')):
        try:
            if check_user_owns_stock(ctx.message.author.name, ticker):
                price = get_price(ticker)
                funds = round(get_available_funds(ctx.message.author.name),2)
                info = get_stock_info(ctx.message.author.name, ticker)


                
                await ctx.send(f"""> The current price of ***{ticker}*** is ***${round(price, 2)}***
                               > You own a total of ***{info['shares']}*** shares 
                               > The average price of the shares you own is ***{info['average_price']}***
                               > If you were to sell now, you would make ***${price-info['average_price']}*** per share.
                               > **How many shares would you like to sell?** (enter a whole number... 'no' to cancel transaction)""")

                response = await self.bot.wait_for('message',
                                                check=lambda message:message.author == ctx.author and message.channel.id == ctx.channel.id,
                                                timeout=20.0)
                
                if response.content in ['n', 'N', 'No', 'NO', 'no']:
                    await ctx.send('Transaction Cancelled')
                elif int(response.content) > info['shares']:
                    await ctx.send(f'You dont own that many shares!')
                else:
                    sell_stock(ctx.message.author.name, ticker, int(response.content), price)
                    await ctx.send(f"""Congrats, **you just sold {int(response.content)} shares of {ticker.upper()} at ${price}**!
                                   you now have ***${funds+int(response.content)*price}*** available to invest""")
            else:
                await ctx.send(f'You do not own any shares of {ticker}!')

        except Exception as e:
            await ctx.send(e)


async def setup(bot):
    await bot.add_cog(PortfolioGame(bot))