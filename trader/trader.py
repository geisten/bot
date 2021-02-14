import sys
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Callable, Union, NamedTuple

from strategy import Trend

TradeConsumer = Callable[[Union[str, bytes]], None]

Strategy = Callable[[Trend], float]


class OrderType(Enum):
    ASK = 1
    BID = 2


def unix_timestamp(dt: datetime):
    return int(dt.timestamp() * 1e3)


class Order(NamedTuple):  # pylint: disable=inherit-non-class
    """The buy/sell prediction"""
    # pylint: disable=too-few-public-methods
    amount: float
    price: float
    timestamp: datetime

    def __repr__(self):
        return 'time={}, price={}, amount={}'.format(self.timestamp, self.price, self.amount)

    def unix_timestamp(self):
        return unix_timestamp(self.timestamp)


def sum_up_order_amount(orders: list[tuple[OrderType, Order]]):
    sum_up: Decimal = Decimal(0.0)
    for order_type, order in orders:
        sum_up += order.amount
    return sum_up


class HookValue:
    def __init__(self, variable):
        self.value = variable

    def __call__(self, value):
        self.value = value


class TradingBook:
    """Order Report class
    The trading book is used with a strategy (or algorithm) to autotrade based on buy or sell offers.
    The bot returns a probability to buy or sell depending on the price trend."""

    def __init__(self, strategy: Strategy, cash_hook: HookValue):
        self.orders_new: list[tuple[OrderType, Order]] = []
        self.orders_placed: dict[Union[str, int], tuple[OrderType, Order]] = {}
        self.orders_completed: dict[Union[str, int], tuple[OrderType, Order]] = {}
        self.cash_handler = cash_hook
        self.timestamp = None
        self.trend = []
        self.strategy = strategy

    def ask(self, price: Decimal, qty: Decimal):
        """Execute buy order"""
        order = Order(float(qty), float(price), datetime.now(
            timezone.utc))
        self.orders_new.append((OrderType.ASK, order))
        print(f"ask: {repr(order)}", file=sys.stdout)

    def bid(self, price: Decimal, qty: Decimal):
        """Execute sell order"""
        order = Order(float(qty), float(price), datetime.now(
            timezone.utc))
        self.orders_new.append((OrderType.BID, order))
        print(f"bid: {repr(order)}", file=sys.stdout)

    def available_cash(self):
        return self.cash_handler()

    def complete(self, order_id: Union[str, int]):
        order = self.orders_placed.pop(order_id)
        if order is not None:
            self.orders_completed[order_id] = order
        else:
            raise ValueError(
                f"order id: '{order_id}' is unknown/invalid")

    def place(self, order_id, order: Order):
        if order is not None:
            self.orders_placed[order_id] = order

    def placed(self):
        return self.orders_placed

    def created(self):
        return self.orders_new

    def created_reset(self):
        self.orders_new = []

    def orders_greater_than(self, price: Decimal, spread: float):
        result = []
        for item in self.orders_completed.values():
            if item[0] == OrderType.ASK and item[1].price + spread > price:
                result.append(item)
        return result

    # return filter(lambda x: x[0] == OrderType.ASK).filter(lambda x: x[1].)

    def __call__(self, timestamp: datetime, price: Decimal):
        self.trend.append(price)
        impulse = self.strategy(self.trend)
        cash = self.cash_handler.value

        if impulse > 0.2:
            amount = sum_up_order_amount(self.orders_greater_than(price, 1.2))
            if amount > 0:
                self.bid(price, amount)
                self.cash_handler(cash - amount * price)
        elif impulse < -0.2:
            amount = cash / price
            self.ask(price, amount) if amount > 0 else None
        elif price > 2000.0:
            amount = cash / price
            self.ask(price, amount) if amount > 0 else None
