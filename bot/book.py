"""Module to handle order books"""
from typing import Dict, NamedTuple, Optional
from enum import Enum
from datetime import datetime, timezone
from bot.trend import Price


class OrderStatus(Enum):
    """Class to represent the status of an order"""
    CREATED = 1
    PENDING = 2
    DONE = 3
    CANCELLED = 4


class Order(NamedTuple):
    """The Order class"""
    idx: str
    status: OrderStatus
    price: Price
    amount: int
    timestamp: datetime

    @classmethod
    def from_price(cls, idx: str, price: float, amount: int):
        """Return a new Order object with an initializer time stamp"""
        return cls(idx, OrderStatus.CREATED, Price.from_value(price), amount, datetime.now(timezone.utc))


OrderBook = Dict[str, Order]


class Credit:
    """The credit class"""

    def __init__(self, value):
        """Initialize the Credit object with the credit value"""
        self.value = value


def update(book: OrderBook, idx: str, status: OrderStatus) -> Optional[Order]:
    """Updates orders taken by the bot.

       It must not create new Orders

       Returns None if key not found
    """
    if idx in book:
        old_order = book[idx]
        book[idx] = Order(idx, status, old_order.price,
                          old_order.amount, datetime.now(timezone.utc))
        return book[idx]
    return None
