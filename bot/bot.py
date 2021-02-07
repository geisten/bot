"""Automated order book

This script allows the user to create a trading bot.


This file can also be imported as a module and contains the following
analyzer/optimization functions:

    * rsi_analyzer
"""

import logging
import math
from decimal import Decimal
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Callable, NamedTuple

import numpy as np  # type: ignore
import talib  # type: ignore


class Order(NamedTuple):  # pylint: disable=inherit-non-class
    """The buy/sell prediction"""
    # pylint: disable=too-few-public-methods
    amount: float
    price: float
    timestamp: datetime

    def __repr__(self):
        return 'time={}, price={}, amount={}'.format(self.timestamp, self.price, self.amount)


class Purchased(NamedTuple):  # pylint: disable=inherit-non-class
    """The purchase amount * price"""
    # pylint: disable=too-few-public-methods
    amount: Decimal
    price: Decimal


Trend = Iterable[float]
Handler = Callable[[Order], None]
Bot = Callable[[Trend, Purchased], float]


class TradingBot:
    """
    An autonomous trading bot.

    The order book is used with a bot (or algorithm) to autotrade with buy or sell offers.
    The bot returns a probability to buy or sell depending on the price trend.

    ...

    Attributes
    ----------
    credit : Decimal
        the initial amount of capital (money) to trade with
    bot : Bot
        the bot calculates the probability to sell or buy
    buyer_handler: Handler
        the handler to execute the buy order
    seller_handler: Handler
        the handler to execute the sell order

    Methods
    -------
    buyer(prediction: float, price: float)
        executes a buyer action and send the result to the handler

    seller(prediction: float, price: float)
        executes a seller action and send the result to the handler
    """

    def __init__(self, cash: Decimal, bot: Bot, buyer_handler: Handler, seller_handler: Handler):
        """
        Parameters
        ----------
        cash : Decimal
            the amount of money to trade with
        bot : Bot
            the analyzer calculates the probability to sell or buy
        buyer_handler : Handler
            An Execution Handler that sends the order to the broker and receives the signals that the stock has been
            bought.
        seller_handler : Handler
            An Execution Handler that sends the order to the broker and receives the signals that the stock has been
            sold.
        """

        self.cash = cash
        self.bot = bot
        self.purchased: Purchased = Purchased(Decimal(0), Decimal(0))
        self.seller_handler = seller_handler
        self.buyer_handler = buyer_handler

    def buyer(self, _prediction: float, price: float) -> None:
        """Executes the buyer action

        Parameters
        ----------
        _prediction: float
            The predicted buy probability
        price: float
            The actual traded price

        """

        decimal_price = Decimal(price)
        amount: Decimal = self.cash / decimal_price
        self.cash -= decimal_price * amount
        self.purchased = Purchased(amount, decimal_price)
        self.buyer_handler(Order(float(amount), price, datetime.now(
            timezone.utc)))

    def seller(self, _prediction: float, price: float) -> None:
        """Executes the sell action

        Parameters
        ----------
        _prediction: float
            The predicted sell probability
        price: float
            The actual traded price

        """

        amount = self.purchased.amount
        self.cash += Decimal(price) * self.purchased.amount
        self.purchased = Purchased(Decimal(0), Decimal(0))
        self.seller_handler(Order(float(amount), price, datetime.now(
            timezone.utc)))

    def __call__(self, trend: Trend) -> None:  # pylint: disable=unsubscriptable-object
        """ Call the order book object with the actual price time series

        Parameters
        ------------
        trend: Trend
            The current price time series
        """

        price = list(trend)[-1]
        impulse = self.bot(trend, self.purchased)
        if impulse > 0.2 and self.purchased.amount > 0:
            self.seller(impulse, price)
        if impulse < -0.2 and self.cash > 1.0:
            self.buyer(abs(impulse), price)


def moving_average(lst, window):
    """Return the moving average array of the input array 'x' """

    return np.convolve(lst, np.ones(window), 'valid') / window


def rsi_analyzer(buy_limit: float, sell_limit: float, moving_average_windows: int, rsi_window: int):
    """Returns a function to predict the buy/sell probability
        The code computes a [moving_average_windows] moving average (MA).
        RSI is computed over [rsi_window] hours.
        If the price dips below a certain percentage below the MA, and
        if the RSI is below a threshold, it will try to buy.

        Once the price rises to a fixed percentage above the buy price, it will sell.

        It never, ever sells below the buy price, which means it has no stop-loss.

        The algorithm is intended to capture a small amount of profit as the price of the coin
        oscillates up and down. If the prices are overall flat or slowly climbing, it works well.
        If prices are climbing sharply over time, as it has for much of 2020, it will not perform
        as well as buy/hold. If the prices are declining over time, it will buy, and then get stuck
         — since it never sells below buy price, it will hold as the price drops.
        This is the primary risk that I can identify.

        The algorithm is thus best suited for periods where you are seeing regular swings up and down,
        but the prices are not sharply climbing or descending.

        Parameters
        ------------
        buy_limit: float
            The general buy limit
        sell_limit: float
            The buy limit factor
        moving_average_windows: int
            The moving average processing window
        rsi_window: int
            The rsi processing window

    """

    def avg_rsi(trend: Trend, purchased: Purchased) -> float:
        """Returns a simple and static price trend course prediction.
        To buy the prediction is > 0 and to sell the prediction is < 0
        """
        # pylint: disable=unused-argument
        moving_avg = moving_average(trend, moving_average_windows)[-1]
        rsi = talib.RSI(trend, timeperiod=rsi_window)[-1]
        price = list(trend)[-1]
        logging.debug("price: %f, moving avg: %f, rsi: %f",
                      price, moving_avg, rsi)
        if math.isnan(moving_avg) is False and math.isnan(rsi) is False:
            # check buy condition
            if price < (moving_avg - (moving_avg * buy_limit)) and (rsi <= 39.5):
                return 0.9
            # check sell conditions
            if price > (purchased.price + (purchased.price * Decimal(sell_limit))):
                return -0.9

        return 0

    return avg_rsi


def rsi_bot_from_json(data):
    """Create and returns a rsi bot based on the json config data"""
    return rsi_analyzer(data['buy_limit'], data['sell_limit'], data['moving_average_windows'],
                        data['rsi_window'])
