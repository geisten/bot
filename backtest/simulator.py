"""Create and save random price data"""
from random import random
import os
from datetime import datetime, timedelta
import pandas as pd  # type: ignore


def random_walker(data_length: int):
    """Create a random walk data list"""
    # seed(1)
    random_walk = list()
    random_walk.append(-1 if random() < 0.5 else 1)  # nosec
    for i in range(0, data_length):
        movement = -1 if random() < 0.5 else 1  # nosec
        value = random_walk[i] + movement
        random_walk.append(value)
    return random_walk


def load_data(filename: str, offset: float, variance: float):
    """Load the created price curve from file"""
    if not os.path.exists(filename):
        # prob = [0.05, 0.95]
        data_length = 1000
        positions = random_walker(data_length)

        date_today = datetime.now()
        minutes = pd.date_range(
            date_today, date_today + timedelta(0, 60 * data_length), freq='min')
        data = pd.DataFrame({'Coin1': positions}, index=minutes)
        data["Coin1"] = offset + data["Coin1"] * variance
        data.to_pickle(filename)
    else:
        data = pd.read_pickle(filename)

    return data


def load_csv_data(filename: str, offset: float, variance: float):
    """Load the created price curve from csv file"""
    if not os.path.exists(filename):
        # prob = [0.05, 0.95]
        data_length = 1000
        positions = random_walker(data_length)

        date_today = datetime.now()
        minutes = pd.date_range(
            date_today, date_today + timedelta(0, 60 * data_length), freq='min')
        data = pd.DataFrame({'Coin1': positions}, index=minutes)
        data["Coin1"] = offset + data["Coin1"] * variance
        data.to_csv(filename)
    else:
        data = pd.read_csv(filename)

    return data
