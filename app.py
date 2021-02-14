"""The main app"""
import argparse
import json
import logging
import csv
import sys
import os
from decimal import Decimal
from collections.abc import Iterable
from typing import Callable

import numpy as np

import bot
import strategy

# List all available strategies. TOTO replace with parsing of strategy package
BOTS: dict[str, Callable[[dict], Callable[[Iterable[float], bot.Purchased], float]]] = {
    "rsi": strategy.rsi_from_json}


class OrderBook:
    """Order Report class"""

    def __init__(self):
        self.order_buy_list: list[bot.Order] = []
        self.order_sell_list: list[bot.Order] = []
        self.timestamp = None

    def buy_handler(self, order: bot.Order):
        """Execute buy order"""
        self.order_sell_list.append(order)
        self.timestamp = self.timestamp

    def sell(self, order: bot.Order):
        """Execute sell order"""
        self.order_buy_list.append(order)
        self.timestamp = self.timestamp

    def __call__(self, trading_bot: bot.TradingBot):
        return f"""
Order Book
================
Cash: {round(trading_bot.cash)} EURO
"""


def sell_handler(order_book: OrderBook):
    """Sell handler to execute sell order"""
    def func(order: bot.Order):
        order_book.sell(order)
        print(f"sell: {repr(order)}", file=sys.stdout)
    return func


def buy_handler(order_book: OrderBook):
    """Buy handler to execute buy order"""
    def func(order: bot.Order):
        order_book.buy_handler(order)
        print(f"buy: {repr(order)}", file=sys.stdout)
    return func


def run():
    """Run the main app"""

    parser = argparse.ArgumentParser(
        description='Backtest your trading strategy.')
    parser.add_argument('--cash', type=str, nargs=1,
                        help='the available cash to trade (EURO)')
    parser.add_argument('--strategy', type=str, nargs=1,
                        help='the trading strategy config file')
    parser.add_argument('--logfile', type=str, nargs='?', const='geisten_bot.log',
                        help='the name of the log file')

    param: argparse.Namespace = parser.parse_args()
    backtest: str = os.path.basename(param.strategy[0])
    print("run backtesting: '{}'".format(backtest))
    logging.basicConfig(filename=param.logfile,
                        encoding='utf-8', level=logging.INFO)

    cash = Decimal(param.cash[0])
    order_report = OrderBook()

    with open(param.strategy[0]) as json_file:
        data = json.load(json_file)
        bot_runner = BOTS[data['name']]
        if bot_runner is not None:
            algo = bot_runner(data['param'])
            runner = bot.TradingBot(
                cash, algo, buy_handler(order_report), sell_handler(order_report))
        else:
            if data['name'] is None:
                raise ValueError("strategy name not set")
            raise ValueError("Invalid strategy name: '%s'" % data['name'])

    trend: list[float] = []
    reader = csv.reader(sys.stdin)
    next(reader, None)
    for row in reader:
        trend.append(float(row[1]))
        runner(np.array(trend))

    print(order_report(runner), file=sys.stderr)


if __name__ == "__main__":
    # execute only if run as a script
    run()
