"""Module to handle order books"""
from datetime import datetime, timezone
from enum import Enum
from typing import NamedTuple, Dict, Optional, Callable, List

from bot.trend import Price


class OrderStatus(Enum):
    """Class to represent the status of an order"""
    CREATED = 1
    PENDING = 2
    DONE = 3
    CANCELLED = 4


class Limit(NamedTuple):
    """The buy/sell limit prediction values"""
    upper: float
    lower: float


class Order(NamedTuple):
    """The confirmed Order class"""
    idx: str
    status: OrderStatus
    price: Price
    amount: int
    timestamp: datetime

    @classmethod
    def from_price(cls, idx: str, price: float, amount: int):
        """Return a new Order object with an initializer time stamp"""
        return cls(idx, OrderStatus.CREATED, Price.from_value(price),
                   amount, datetime.now(timezone.utc))


class BuyOrder(Order):
    """The buy order"""


class SellOrder(Order):
    """The sell order"""


class PlaceOrder(NamedTuple):
    """Place order tuple class"""
    type: str
    amount: int
    price: float
    timestamp: datetime


def place_order(order_type: str, prediction: float) -> Callable[[Callable[[float], int]], PlaceOrder]:
    """Function to create a setup to place orders of different types by the prediction value"""

    def place(price, amount_strategy: Callable[[float, float], int]) -> PlaceOrder:
        return PlaceOrder(order_type, amount_strategy(prediction, price), price, datetime.now(timezone.utc))

    return place


def place_sell_order(prediction: float) -> Callable[[Callable[[float], int]], PlaceOrder]:
    """Function to place a 'sell' order"""
    return place_order("sell", prediction)


def place_buy_order(prediction: float) -> Callable[[Callable[[float], int]], PlaceOrder]:
    """Function to place a 'buy' order"""
    return place_order("buy", prediction)


def order_within_limit(first: float, second: float, limits: Limit) -> bool:
    """Helper function to calculate if the sell/buy predictions are reliable"""
    return first > limits.upper and second <= limits.lower


def order_prediction_is_valid(sell: float, buy: float, sell_limits: Limit, buy_limits: Limit) -> bool:
    """Check if the predicted sell and buy value are valid to create order from"""
    if order_within_limit(buy, sell, buy_limits):
        return True
    if order_within_limit(sell, buy, sell_limits):
        return True
    return False


def order_prediction_checker(sell_limits: Limit, buy_limits: Limit) -> Callable[[float, float], bool]:
    """Return the prediction validation function"""
    return lambda s, b: order_prediction_is_valid(s, b, sell_limits, buy_limits)


def place_bet(sell: float, buy: float) -> Callable[[Callable[[float], int]], PlaceOrder]:
    if sell > buy:
        placed_order = place_sell_order(sell)
    elif sell < buy:
        placed_order = place_buy_order(buy)
    else:
        raise ValueError("Invalid predictions")
    return placed_order


def order_price(place_order: PlaceOrder, credit: float):
    if(place_order.type == 'sell'):
        return credit + (place_order.amount * place_order.price)
    if(place_order.type == 'buy'):
        return credit - (place_order.amount * place_order.price)
    raise ValueError("Invalid type name")


def place_order_builder(amount_strategy: Callable[[float], int]) -> Callable[[float, float], PlaceOrder]:
    """Return the place order function, created by the sell and buy prediction"""

    def create(sell: float, buy: float):
        if sell > buy:
            placed_order = place_sell_order(sell)
        elif sell < buy:
            placed_order = place_buy_order(buy)
        else:
            raise ValueError("Invalid predictions")
        return placed_order(amount_strategy)

    return create


OrderBook = Dict[str, Order]


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


def order_processor_setup(sell_limit: Limit, buy_limit: Limit, order_strategy, clb: Callable[[List[PlaceOrder]], None]):
    """Setups the order processor"""
    prediction_is_valid = order_prediction_checker(sell_limit, buy_limit)

    def predictor(credit: float, sell: float, buy: float) -> bool:
        """Returns a new order, based on prediction or None if no new Order is predicted"""
        if prediction_is_valid(sell, buy):
            clb([place_order_builder(order_strategy(credit))(sell, buy)])
            return True
        return False

    return predictor
