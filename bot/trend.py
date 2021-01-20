"""Handle the price trend of a product. """
from __future__ import annotations
from datetime import datetime, timezone
from typing import NamedTuple, List


class Price(NamedTuple):
    """A class to represent a price"""
    value: float  # We ignore the rounding issues with float based currencies
    timestamp: datetime

    @classmethod
    def from_value(cls, value: float):
        """Return a new Price object with an initializer time stamp"""
        return cls(value, datetime.now(timezone.utc))


PriceTrend = List[Price]


def update(trend: PriceTrend, value: float) -> Price:
    """Adds new Price object to the price trend list"""
    new_price = Price.from_value(value)
    trend.append(new_price)
    return new_price
