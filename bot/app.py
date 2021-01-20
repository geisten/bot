"""The trading bot module"""
from typing import List
from .book import Order, OrderBook, Credit
from .trend import Price


def run():
    """Run the bot"""
    print("Hello World...")
    print("Ende...")


def process(book: OrderBook, credit: Credit,
            buy: float,
            sell: float) -> List[Order]:
    """Process the bot with the required parameters"""
    return []
