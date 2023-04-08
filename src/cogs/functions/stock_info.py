import random
from datetime import date

import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt

# constants
from .constants import VALID_PERIODS, PRICE_PLOT_PATH, GROWTH_PLOT_PATH, INCLUDE_FIELDS


def get_history(ticker: str, period: str) -> pd.DataFrame:
    """Gets the history of a stocks data and computes the daily returns

    Args:
        ticker (str): The ticker of a stock
        period (str): The period for which the data is collected

    Returns:
        Pandas.df: Pandas dataframe of stock data
    """

    if period not in VALID_PERIODS:
        raise Exception('Period not defined')

    try:
        data = yf.Ticker(ticker)
        history = data.history(period=period).dropna()
        returns = [(history.Close[x] / history.Close[x-1] - 1) for x in range(1,len(history.Close))]
        returns.insert(0,0)
        history['Returns'] = returns

        if returns == [] or returns == [0]:
            raise Exception('Ticker not found')
        
        return history
    
    except Exception as e:
        raise e


def plot_ticker(ticker: str, period='ytd') -> None:
    """Saves a plot of a stock's close and daily returns for a given period
        plot is saved as PRICE_PLOT

    Args:
        ticker (str): The ticker of a stock
        period (str): The period for which stock data is plotted
            valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            (default is year to date)
    """

    try:
        history = get_history(ticker, period)
        annual_returns = 100*round((1+np.mean(history.Returns))**252 - 1, 4)

        # plotting the data
        fig, (ax1, ax2) = plt.subplots(2,1, figsize=(12,5))
        fig.subplots_adjust(hspace=0.5)
        ax1.set_title(f'Adjusted close of {ticker}')
        ax1.plot(history.Close)
        ax1.set_ylabel('Price')
        ax1.grid(True)
        ax2.set_title(f'Returns of {ticker}')
        ax2.plot(history.Returns)
        ax2.plot(history.Returns*0, '--')
        ax2.set_ylabel('Returns')
        ax2.grid(True)
        fig.text(.5, 0.02, f'Average annual returns for given period: {annual_returns}%', ha='center')
        fig.savefig(PRICE_PLOT_PATH)

    except Exception as e:
        raise e
    

def get_price(ticker: str) -> float:
    """Checks the current price of a stock
        
        Args:
            ticker (str): the stocks ticker
        
        Return:
            int: price of stock
    """

    try:
        data = yf.Ticker(ticker)

        return data.fast_info.last_price
    
    except Exception as e:
        raise e


def get_info(ticker: str) -> dict:
    """Summarizes info about a stock
    
    Args:
        ticker (str): The ticker of a stock

    Returns:
        dict: dictionary of all stock summaries
    """

    try:
        ticker = yf.Ticker(ticker)
        return {x: y for x, y in ticker.fast_info.items() if x in INCLUDE_FIELDS}

    except Exception as e:
        raise e


def get_news(ticker: str) -> tuple:
    """Sends a link to a news article related to the stock

    Args:
        ticker (str): Ticker of a stock

    Returns:
        tuple: tuple of news link and title
    """

    try:
        data = yf.Ticker(ticker)
        i = random.randint(0, len(data.news)-1)

        return (data.news[i]['link'], data.news[i]['title'])
    
    except Exception as e:
        raise e


# TODO add dividends math...
# TODO make more efficient (define a function to do calculations)
def stock_worth(ticker: str, amount: int, start_date: date) -> dict:
    """Calculates the current value of a hypothetical investment in the past
        Compares investment value to performance of s&p 500 index
        Also saves a plot of % change in value
    
    Args:
        ticker (str): Ticker of a stock
        amount (int): Amount of initial investment
        start_date (date): Date of initial investment
    
    Return:
        dict: dictionary of current investment value info

    """

    try:
        ticker = yf.Ticker(ticker)
        history = ticker.history(start=start_date, end=date.today())
        buy_price = history.head(1).Close[0]
        current_price = history.tail(1).Close[0]
        returns = [(history.Close[x] / history.Close[x-1] - 1) for x in range(1, len(history.Close))]
        returns.insert(0,0)
        history['Returns'] = returns
        history['PercentIncrease'] = [100*(history.Close[x]-buy_price)/buy_price for x in range(len(history.Close))]

        # calculating values
        summary = {}
        summary['annual_returns'] = 100 * ((1 + np.mean(returns))**252 - 1)
        summary['percent_increase'] = 100 * (current_price-buy_price) / buy_price
        summary['current_value'] = (1 + summary['percent_increase']/100) * amount
        summary['total_profit'] = summary['current_value'] - amount

        # s&p500
        snp = yf.Ticker('^GSPC')
        snp_history = snp.history(start=start_date, end=date.today())
        snp_start_price = snp_history.head(1).Close[0]
        snp_end_price = snp_history.tail(1).Close[0]
        snp_returns = [(snp_history.Close[x] / snp_history.Close[x-1] - 1) for x in range(1,len(snp_history.Close))]
        snp_returns.insert(0,0)
        snp_history['Returns'] = snp_returns
        snp_history['PercentIncrease'] = [100*(snp_history.Close[x]-snp_start_price)/snp_start_price for x in range(len(snp_history.Close))]
        
        summary['snp_annual_returns'] = 100 * ((1 + np.mean(snp_returns))**252 - 1)
        summary['snp_percent_increase'] = 100*(snp_end_price/snp_start_price-1)
        summary['snp_current_value'] = (1 + summary['snp_percent_increase']/100) * amount
        summary['snp_total_profit'] = summary['snp_current_value'] - amount

        if summary['snp_current_value'] > summary['current_value']:
            summary['recommendation'] = f"SMH... Should have just bought a market index fund. You would have had **${round(summary['snp_current_value'], 2)}** instead."
        else:
            summary['recommendation'] = f"{ticker.ticker} FTW!"
        
        #plotting
        plt.figure(figsize=(10,5))
        plt.plot(history.PercentIncrease, label=ticker.ticker)
        plt.plot(snp_history.PercentIncrease, label='S&P 500')
        plt.ylabel('Percentage increase')
        plt.title(f'Percent price increase of {ticker.ticker} from {start_date}')
        plt.legend()
        plt.savefig(GROWTH_PLOT_PATH)

        return summary

    except Exception as e:
        print(e)
        raise e


# def calculate_values(data: pd.DataFrame) -> pd.DataFrame:
#     """Calculates some summary values of a stock
#         values calculated: """
        

# if __name__ == "__main__":
#     stock_worth('T', 1000, '2012-03-15')