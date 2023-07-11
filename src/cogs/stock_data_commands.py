from datetime import date
import discord
from discord.ext import commands

from functions.stock_info import (plot_ticker, get_info, stock_worth, get_news, get_price)

#constants
from functions.constants import PRICE_PLOT_PATH, GROWTH_PLOT_PATH, VALID_PERIODS

class StockData(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._last_member = None
    
    @commands.command(name='stonk', 
                      help='- Shows stock price for the given period')
    async def stonk(self, ctx, 
                    ticker: str=commands.parameter(description='- Stock ticker'), 
                    period: str=commands.parameter(description=f'- Time period {VALID_PERIODS}')):
        try:
            plot_ticker(ticker, period)
            await ctx.send(file=discord.File(PRICE_PLOT_PATH))

        except Exception as e:
            await ctx.send(e)

    @commands.command(name='price',
                        help='- current price of a stock')
    async def price(self, ctx,
                    ticker: str=commands.parameter(description='- Stock ticker')):
        try:
            await ctx.send(f'Current price of **{ticker}: ${round(get_price(ticker), 2)}**')

        except Exception as e:
            await ctx.send(e)

    @commands.command(name='stonknews',
                      help='- Sends a related news article for a given ticker')
    async def news(self, ctx, 
                   ticker: str=commands.parameter(description='- Stock ticker')):
        try:
            news = get_news(ticker)
            await ctx.send(f'> **{ticker} in the news:** {news[1]}\n'
                        f'> {news[0]}')
            
        except Exception as e:
            print(e)
            await ctx.send('No news available for ticker')

    # @commands.command(name='stonksum',
    #                   help='- summary of a ticker')
    # async def summary(self, ctx, 
    #                   ticker: str=commands.parameter(description='- Stock ticker')):
    #     try:
    #         summary = get_info(ticker)
    #         await ctx.send(f"""```{date.today()} summary of {ticker} (prices in {summary['currency']})
    #         Current price: {round(summary['lastPrice'],2)}
    #         Todays high: {round(summary['dayHigh'],2)}
    #         Todays Low: {round(summary['dayLow'])}
    #         Fifty day average: {round(summary['fiftyDayAverage'],2)}
    #         Market cap: {round(summary['marketCap']/(10**9),2)} Billion
    #         Yearly High: {round(summary['yearHigh'],2)}
    #         Yearly Low: {round(summary['yearLow'],2)}
    #         Yearly Change: {100*round(summary['yearChange'],2)}%```""")

    #     except Exception as e:
    #         print(e)
    #         await ctx.send('Summary not available')

    @commands.command(name='stonkworth',
                      help='- What an investment in the past would be worth today...')
    async def worth(self, ctx,
                    ticker: str=commands.parameter(description="- stock ticker"),
                    amount: int=commands.parameter(description="- amount of initial investment"),
                    start_date: str=commands.parameter(description="- initial investment date (YYYY-MM-DD)")):
        try:
            y,m,d = [int(x) for x in start_date.split('-')]
            start_date = date(y,m,d)
            summary = stock_worth(ticker, amount, start_date)

            await ctx.send(f"""> If you invested ${amount} in {ticker} stock on {start_date}...
            > Today, this investment would be worth: **${round(summary['current_value'], 2)}**
            > Average annual returns: {round(summary['annual_returns'], 2)}%
            > Total percent increase in price: {round(summary['percent_increase'], 2)}%
            > Total profit: ${round(summary['total_profit'], 2)}
            > During the same time period, the **S&P500 index** grew {round(summary['snp_percent_increase'], 2)}%. With annual returns of {round(summary['snp_annual_returns'], 2)}%
            > Meaning the same investment would be worth ${round(summary['snp_current_value'], 2)}
            > {summary['recommendation']}""")

            await ctx.send(file=discord.File(GROWTH_PLOT_PATH))

        except Exception as e:
            await ctx.send(e)


async def setup(bot):
    await bot.add_cog(StockData(bot))