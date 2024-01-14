# Stock Portfolio Simulation Bot

This project is a Portfolio Simulation Discord Bot made using Discord.py. It allows users to look up real time ticker info as well as participate in a portfolio simulation game where users are able to create mock stock portfolios and perform trades.

## Installation

This project was not created in a virtual environment, so the following Python libraries need to be installed for usage: 
- discord.py: used to create the framework of the bot
- numpy: used for numerical computations
- pandas: used to clean up and process data
- matplotlib: used for plotting ticker data
- yfinance: used to retrieve real time ticker data
- pysondb: simple json database to store portfolio data

Constants also need to be updated to match new file paths (src/functions/constants.py)

## Usage

You will need to invite the bot to a Discord server and run the main.py file under src/. Typing '$help' in the Discord chat for the complete list of commands.