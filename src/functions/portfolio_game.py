import yfinance as yf
from datetime import date
from pysondb import db
import pandas as pd
from matplotlib import pyplot as plt

# constants
from functions.constants import STARTING_FUNDS, PORTFOLIO_DATA_PATH, TRANSACTIONS_PATH


class UserProfile:
    def __init__(self, username: str) -> None:
        self.username = username
        self.create_date = str(date.today())
        self.funds_available = STARTING_FUNDS
        self.portfolio = {}


class Transaction:
    def __init__(self, username: str, ticker: str, price: float, shares: int, status: str, remaining_funds: float) -> None:
        self.date = str(date.today())
        self.username = username
        self.ticker = ticker
        self.price = price
        self.shares = shares
        self.status = status
        self.remaining_funds = remaining_funds


def check_user_exists(username: str) -> bool:
    """Checks if user has a profile
        
        Args:
            username (str): user's name
            
        Return:
            bool: boolean of whether the user exists in file
    """
    profiles = db.getDb(PORTFOLIO_DATA_PATH)
    return profiles.getByQuery({'username': username}) != []


def create_user_profile(username: str) -> bool:
    """Creates a user profile if one does not already exist
        
        Args:
            username (str): user's name

        Return:
            bool: True if profile was created, False if it already exists
    """
    profiles = db.getDb(PORTFOLIO_DATA_PATH)

    if profiles.getByQuery({'username': username}):
        return False
    else:
        profiles.add(UserProfile(username).__dict__)
        return True


def get_profile(username: str) -> dict:
    """Retrieves the user's profile
        
        Args:
            username (str): user's name
        
        Return:
            dict: dictionary of user's profile, returns None if user does not exist
    """
    profiles = db.getDb(PORTFOLIO_DATA_PATH)
    return profiles.getByQuery({'username': username})[0]


def get_current_prices(tickers: list) -> dict:
    """Retrieves the current price of a list of tickers
        args:
            tickers (list): list of tickers to get prices for
        
        return:
            dict: dictionary of tickers and their current prices
    """
    tickers = [ticker.upper() for ticker in tickers]
    response = yf.Tickers(tickers)

    return {ticker: response.tickers[ticker].info['currentPrice'] for ticker in tickers}


def profile_summary(username: str) -> dict:
    """Sends a brief summary of the user's profile
    
        Args:
            username (str): users name
            
        Return:
            dict: dictionary of user's profile, returns None if user does not exist
    """
    profile = get_profile(username)

    if profile:
        stocks_owned = list(profile['portfolio'].keys())
        profile['current_stock_values'] = get_current_prices(stocks_owned)
        profile['current_value'] = profile['funds_available'] + sum([profile['portfolio'][ticker]['shares']*profile['current_stock_values'][ticker] for ticker in profile['portfolio']])
        return profile
    else:
        return None


def get_available_funds(username: str) -> float:
    """Retrieves the funds available for a given user
        
        Args:
            user (str): users name
        
        Return:
            float: available funds in users account, None if user does not exist
    """
    profile = get_profile(username)
    return profile['funds_available'] if profile else None


def record_transaction(username: str, ticker: str, price: float, shares: int, status: str) -> None:
    """Records a stock transaction

        Args:
            user (str): users name
            ticker (str): the stocks ticker
            price (float): current price of stock
            shares (int): the amount of shares in transaction
            status (str): the status of the transaction (buy/sell)
    """
    profile = get_profile(username)

    # assumes 'buy stock' has already been called so the remaining funds is already updated
    remaining_funds = profile['funds_available']

    transactions = db.getDb(TRANSACTIONS_PATH)
    transactions.add(Transaction(username, ticker.upper(), price, shares, status, remaining_funds).__dict__)


def buy_stock(username: str, ticker: str, amount: int, price: float) -> None:
    """Buys a stock for a given user. Assumed that the user has enough funds for the transaction
    
        Args:
            user (str): users name
            ticker (str): the stocks ticker
            amount (int): the amount of shares to buy
            price (float): current price of stock
    """
    ticker = ticker.upper()

    profile = get_profile(username)
    if profile:
        new_funds = round(profile['funds_available'] - (amount * price), 2)
        portfolio = profile['portfolio']

        # ticker is in portfolio
        if ticker in portfolio:
            portfolio[ticker]['average_price'] = (portfolio[ticker]['average_price']*portfolio[ticker]['shares'] + price*amount)/(amount+portfolio[ticker]['shares'])
            portfolio[ticker]['shares'] += amount
        # ticker is not in portfolio
        else:
            stock = yf.Ticker(ticker.upper())
            portfolio[ticker] = {
                'name': stock.info['longName'],
                'shares': amount,
                'average_price': price,
                'currency': stock.info['financialCurrency']
            }
        
        updated_profile = {
            'funds_available': new_funds,
            'portfolio': portfolio
        }

        # update database
        profiles = db.getDb(PORTFOLIO_DATA_PATH)
        profiles.updateById(pk=profile['id'], new_data=updated_profile)

        # record transaction
        record_transaction(username, ticker, price, amount, 'buy')
    else:
        raise Exception('User does not exist')


def check_user_owns_stock(username: str, ticker: str) -> bool:
    """Checks if user owns a stock
    
        Args:
            user (str): users name
            ticker (str): the stocks ticker
            
        Return:
            bool: boolean of whether the user owns the stock"""
    profile = db.getDb(PORTFOLIO_DATA_PATH).getByQuery({'username': username})
    return ticker.upper() in profile[0]['portfolio']


def get_stock_info(username: str, ticker: str) -> dict:
    """Gets the average price and number of shares of a stock in a users portfolio
    
        Args:
            user (str): users name
            ticker (str): the stocks ticker
        
        Return:
            dict: dictionary of the average price and number of shares"""
    profile = db.getDb(PORTFOLIO_DATA_PATH).getByQuery({'username': username})
    return profile[0]['portfolio'][ticker.upper()]


def sell_stock(username: str, ticker: str, amount: int, price: float) -> None:
    """Sells a stock for a given user. Assumed that the user own enough shares for transaction
    
        Args:
            user (str): users name
            ticker (str): the stocks ticker
            amount (int): the amount of shares to sell
            price (float): current price of stock
    """
    ticker = ticker.upper()
    profile = get_profile(username)
    if profile:
        new_funds = round(profile['funds_available'] + (amount * price), 2)
        portfolio = profile['portfolio']

        # ticker is in portfolio
        if ticker in portfolio:
            portfolio[ticker]['shares'] -= amount
            
            if portfolio[ticker]['shares'] == 0:
                del portfolio[ticker]
        # ticker is not in portfolio
        else:
            raise Exception('User does not own this stock')
        
        updated_profile = {
            'funds_available': new_funds,
            'portfolio': portfolio
        }

        # update database
        profiles = db.getDb(PORTFOLIO_DATA_PATH)
        profiles.updateById(pk=profile['id'], new_data=updated_profile)

        # record transaction
        record_transaction(username, ticker, price, amount, 'sell')
    else:
        raise Exception('User does not exist')


def get_performance_history(username: str) -> pd.DataFrame:
    """Gets the historical performance of a users portfolio
    
        Args:
            user (str): users name
        
        Return:
            pd.DataFrame: dataframe of the portfolio performance history"""
    transactions = db.getDb(TRANSACTIONS_PATH).getByQuery({'username': username})
    
    creation_date = get_profile(username)['create_date']

    # get all unique tickers in transactions
    tickers = list(set([transaction['ticker'] for transaction in transactions]))

    history = yf.download(tickers, start=creation_date, end=date.today())

    print(history)


def plot_history(username: str) -> None:
    pass


def get_leaderboard() -> dict:
    """Generates a leaderboard of all users and their current portfolio values
    
        Return:
            dict: dictionary of all users and their current portfolio values"""
    profiles = db.getDb(PORTFOLIO_DATA_PATH).getAll()
    leaderboard = {}
    for profile in profiles:
        stocks_owned = list(profile['portfolio'].keys())
        prices = get_current_prices(stocks_owned)
        leaderboard[profile['username']] = round(profile['funds_available'] + sum([profile['portfolio'][ticker]['shares']*prices[ticker] for ticker in profile['portfolio']]),2)
    
    return leaderboard


def day_performance() -> dict:
    pass

def plot_comparison() -> None:
    pass

if __name__ == "__main__":
    get_performance_history('billjohn')

    pass
    