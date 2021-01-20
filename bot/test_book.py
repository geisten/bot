""" Test the order book module """

from bot.book import update as book_update, OrderStatus, Order


def test_book_update():
    """Test the order book update functionality"""
    res = book_update({}, "a", OrderStatus.CANCELLED)
    assert res is None  # nosec

    book = {"a": Order("a", None, None, None, None)}
    res = book_update(book, "a", OrderStatus.CANCELLED)
    assert res.idx == "a"  # nosec
