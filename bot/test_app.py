"""The Bot App tests"""
from .app import run, process
from .book import Credit, OrderBook, Order, OrderStatus


def test_app(capsys):
    """The bot test"""
    run()
    captured = capsys.readouterr()

    assert "Hello World..." in captured.out


def test_app_process():
    credit = Credit(100)
    book = [Order.from_price("abc", 20.0, 4)]
    new_orders = process(book, credit, 0.5, 0.5)
    assert not new_orders
    assert 0 == len(new_orders)
