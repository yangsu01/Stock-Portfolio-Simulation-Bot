import yfinance as yf
import json
from datetime import date

# constants
from .constants import STARTING_FUNDS, USER_DATA_PATH, PORTFOLIO_DATA_PATH, TRANSACTIONS_PATH


class UserProfile:
    def __init__(self) -> None:
        self.create_date = str(date.today())
        self.funds_available = STARTING_FUNDS
        self.portfolio = {}
        self.portfolio_value = STARTING_FUNDS


class Transaction:
    def __init__(self, ticker: str, price: float, shares: int, description: str) -> None:
        self.date = str(date.today())
        self.ticker = ticker
        self.price = price
        self.shares = shares
        self.description = description


def check_user_exists(username: str) -> bool:
    """Checks if username is defined in user file
        
        Args:
            username (str): user's name
            
        Return:
            bool: boolean of whether the user exists in file
    """
    with open(USER_DATA_PATH, 'r') as read_file:
        data = json.load(read_file)

        return username in data


def create_user_profile(username: str) -> None:
    """Creates a user profile and portfolio
        
        Args:
            username (str): user's name
    """
    # add user to the users list
    with open(USER_DATA_PATH, 'r') as read_users:
        user_data = json.load(read_users)

    with open(USER_DATA_PATH, 'w') as write_users:
        user_data.append(username)
        json.dump(user_data, write_users, indent=4)

    # create a portfolio under the user's name
    with open(PORTFOLIO_DATA_PATH, 'r') as read_portfolios:
        portfolio_data = json.load(read_portfolios)

    with open(PORTFOLIO_DATA_PATH, 'w') as portfolios:
        portfolio_data[username] = UserProfile(username).__dict__
        json.dump(portfolio_data, portfolios, indent=4)


def profile_summary(username: str) -> dict:
    """Sends a brief summary of the user's profile
    
        Args:
            username (str): users name
            
        Return:
            dict: dictionary of profile summary
    """

    with open(PORTFOLIO_DATA_PATH, 'r') as read_portfolios:
        portfolio_data = json.load(read_portfolios)
    
    return portfolio_data[username]


def get_available_funds(user: str) -> float:
    """Retrieves the funds available for a given user
        
        Args:
            user (str): users name
        
        Return:
            float: available funds in users account
    """

    with open(PORTFOLIO_DATA_PATH, 'r') as read_users:
        user_data = json.load(read_users)

        if user not in user_data:
            raise Exception(f'{user} does not have a portfolio!')
        
    return user_data.get(user).get('funds_available')

def record_transaction():
    return

def update_portfolio():
    return

def buy_stock(user: str, ticker: str, amount: int, price: float) -> None:

    return

def sell_stock(user: str, ticker: str, amount: int):
    return


# if __name__ == "__main__":
#     summary = profile_summary('bill john')

#     for key,value in summary.items():
#         print(f'{key}: {value}')
    
