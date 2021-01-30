""" Test the order book module """
from datetime import datetime, timezone

from bot.book import place_sell_order, place_buy_order, place_order_builder


def test_place_sell_order():
    """Test the place_order functionality"""

    def simple_amount_strategy(prediction: float) -> int:
        return int(prediction * 100)

    order_setup = place_sell_order(0.5)
    timestamp = datetime.now(timezone.utc)
    place_order = order_setup(simple_amount_strategy)
    assert place_order.type == "sell"  # nosec
    assert place_order.amount == 50  # nosec
    assert place_order.timestamp > timestamp  # nosec


def test_place_buy_order():
    """Test the place_order functionality"""

    def simple_amount_strategy(prediction: float) -> int:
        return int(prediction * 100)

    order_setup = place_buy_order(0.5)
    timestamp = datetime.now(timezone.utc)
    place_order = order_setup(simple_amount_strategy)
    assert place_order.type == "buy"  # nosec
    assert place_order.amount == 50  # nosec
    assert place_order.timestamp > timestamp  # nosec


def test_place_order_builder():
    """Test the creation of an place order builder function"""

    def simple_amount_strategy(prediction: float) -> int:
        return int(prediction * 100)

    order_builder = place_order_builder(simple_amount_strategy)
    place_order = order_builder(0.81, 0.2)
    assert place_order is not None  # nosec
    assert place_order.type == "sell"  # nosec
    assert place_order.amount == 81  # nosec

    place_order = order_builder(0.30, 0.2)
    assert place_order is not None  # nosec
    assert place_order.type == "sell"  # nosec
    assert place_order.amount == 30  # nosec

    place_order = order_builder(0.30, 0.89)
    assert place_order is not None  # nosec
    assert place_order.type == "buy"  # nosec
    assert place_order.amount == 89  # nosec
