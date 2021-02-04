"""Automated order book

This script allows the user to create a trading bot.


This file can also be imported as a module and contains the following
analyzer/optimization functions:

    * rsi_analyzer
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Callable, List, NamedTuple

import math
import logging
import talib
import numpy as np


class OrderType(Enum):
    """The direction of the order (buy/sell)"""
    BUY = 1
    SELL = 2


class Order(NamedTuple):
    """The buy/sell prediction"""
    dirs: OrderType
    amount: float
    price: float
    timestamp: datetime


class Prediction(NamedTuple):
    """The buy/sell prediction"""
    sell: float
    buy: float


class Purchased(NamedTuple):
    """The purchase amount * price"""
    amount: float
    price: float


Trend = List[float]
Handler = Callable[[OrderType, datetime, Purchased], None]
Analyzer = Callable[[Trend, Purchased], Prediction]


class OrderBook:
    """
    A class used to represent an order book

    ...

    Attributes
    ----------
    credit : float
        the amount of money to trade with
    analyzer : Analyzer
        the analyzer calculates the probability to sell or buy

    Methods
    -------
    buyer(prediction: float, price: float)
        executes a buyer action and send the result to the handler

    seller(prediction: float, price: float)
        executes a seller action and send the result to the handler
    """

    def __init__(self, credit: float, analyzer: Analyzer):
        """
        Parameters
        ----------
        credit : str
            the amount of money to trade with
        analyzer : Analyzer
            the analyzer calculates the probability to sell or buy
        """

        self.credit = credit
        self.analyzer = analyzer
        self.purchased: Purchased = Purchased(0, 0)

    def buyer(self, prediction: float, price: float) -> Order:
        """Executes the buyer action

        Parameters
        ----------
        prediction: float
            The predicted buy probability
        price: float
            The actual traded price

        """
        self.credit = self.credit * prediction
        amount = self.credit / price
        self.credit -= price * amount
        self.purchased = Purchased(amount, price)
        return Order(OrderType.BUY, amount, price, datetime.now(
            timezone.utc))


    def seller(self, _prediction: float, price: float):
        """Executes the sell action

        Parameters
        ----------
        prediction: float
            The predicted buy probability
        price: float
            The actual traded price

        """

        amount = self.purchased.amount
        self.credit += price * self.purchased.amount
        self.purchased = Purchased(0, 0)
        return Order(OrderType.SELL, amount, price, datetime.now(
            timezone.utc))
            

    def __call__(self, trend: Trend):
        """ Call the order book object with the actual price time series

        Parameters
        ------------
        trend: Trend
            The current price time series
        """

        price = trend[-1]
        (sell, buy) = self.analyzer(trend, self.purchased)
        if sell > buy and self.purchased.amount > 0:
            self.seller(sell, price)
        elif sell < buy and self.credit > 1.0:
            self.buyer(buy, price)
        return self.purchased


def moving_average(lst, window):
    """Return the moving average array of the input array 'x' """

    return np.convolve(lst, np.ones(window), 'valid') / window


def rsi_analyzer(buy_limit: float, sell_limit: float, moving_average_windows: int, rsi_window: int):
    """Returns a function to predict the buy/sell probability"""

    def avg_rsi(trend: Trend, purchased: Purchased,
                ) -> Prediction:
        """Returns a simple and static price trend course prediction"""
        # pylint: disable=unused-argument
        moving_avg = moving_average(trend, moving_average_windows)[-1]
        rsi = talib.RSI(trend, timeperiod=rsi_window)[-1]
        price = trend[-1]
        logging.debug("price: %f, moving avg: %f, rsi: %f",
                      price, moving_avg, rsi)
        if math.isnan(moving_avg) is False and math.isnan(rsi) is False:
            # check buy condition
            if price < (moving_avg - (moving_avg * buy_limit)) and (rsi <= 39.5):
                return Prediction(0.1, 0.9)
            # check sell conditions
            if price > (purchased.price + (purchased.price * sell_limit)):
                return Prediction(0.9, 0.1)

        return Prediction(0, 0)
    return avg_rsi
