"""The rsi strategy"""

import logging
import math

import numpy as np  # type: ignore
import talib  # type: ignore

from .strategy import Trend


def moving_average(lst, window):
    """Return the moving average array of the input array 'x' """

    return np.convolve(lst, np.ones(window), 'valid') / window


def rsi(buy_limit: float, sell_limit: float, moving_average_windows: int, rsi_window: int):
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

    def processor(trend: Trend) -> float:
        """Returns a simple and static price trend course prediction.
        To buy the prediction is > 0 and to sell the prediction is < 0
        """
        trend = [float(x) for x in trend]
        trend = np.array(trend)
        moving_avg = moving_average(trend, moving_average_windows)[-1]
        rsi_val = talib.RSI(trend, timeperiod=rsi_window)[-1]
        price = list(trend)[-1]
        logging.debug("price: %f, moving avg: %f, rsi: %f",
                      price, moving_avg, rsi)
        if math.isnan(moving_avg) is False and math.isnan(rsi_val) is False:
            # check buy condition
            if price < (moving_avg - (moving_avg * buy_limit)) and (rsi_val <= 39.5):
                return 0.9

        return 0

    return processor


def rsi_from_json(data):
    """Create and returns a rsi strategy based on the json config data"""
    return rsi(data['buy_limit'], data['sell_limit'], data['moving_average_windows'],
               data['rsi_window'])
