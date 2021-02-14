import json
import logging

from trader import authenticate_to_broker, test_runner, TradingBook, HookValue
from .client import parse_cmd_line, find_strategy_name


def run():
    print("run binance client")
    cash, config_file_name, log_file = parse_cmd_line()
    logging.basicConfig(filename=log_file,
                        encoding='utf-8', level=logging.INFO)
    with open(config_file_name) as json_file:
        data = json.load(json_file)
        bot_runner = find_strategy_name(data['name'])
        if bot_runner is not None:
            trade_strategy = bot_runner(data['param'])
            trading_book = TradingBook(trade_strategy, HookValue(cash))
            runner = authenticate_to_broker(b'm3hrAISGBgx16k3v8LCgVqvDDBhdLnLoehbMXKwgkOCPX1srfSPvfHttItnNvDxC',
                                            b"y2b6L5NaWDkAwIVpgnbkWBOsOswsFdwOyWFGsxRCuo6fyTy54IPHSQVnEP9XWjh6")
            test_runner(trading_book, "BTCUSDT", "aggTrade", runner)
        else:
            if data['name'] is None:
                raise ValueError("strategy name not set")
            raise ValueError("Invalid strategy name: '%s'" % data['name'])

    print("Auf Wiedersehen!")
