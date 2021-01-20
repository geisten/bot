"""Test the price trend module"""
from datetime import datetime, timezone
from bot.trend import update as trend_update


def test_trend_update():
    """Test the price trend update functionality"""
    lst = []
    current = datetime.now(timezone.utc)
    trend_update(lst, 30.0)
    assert len(lst) == 1  # nosec
    assert current < lst[0].timestamp  # nosec
