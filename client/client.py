import argparse
from decimal import Decimal
from typing import Callable, Iterable

import strategy

# List all available strategies. TOTO replace with parsing of strategy package
BOTS: dict[str, Callable[[dict], Callable[[Iterable[float], tuple[Decimal, Decimal]], float]]] = {
    "rsi": strategy.rsi_from_json}


def find_strategy_name(name: str):
    return BOTS[name]


def parse_cmd_line() -> tuple[Decimal, str, str]:
    parser = argparse.ArgumentParser(
        description='Backtest your trading strategy.')
    parser.add_argument('--cash', type=str, nargs=1,
                        help='the available cash to trade (EURO)')
    parser.add_argument('--strategy', type=str, nargs=1,
                        help='the trading strategy config file')
    parser.add_argument('--logfile', type=str, nargs='?', const='geisten_bot.log',
                        help='the name of the log file')

    param: argparse.Namespace = parser.parse_args()
    log_file: str = param.logfile
    config_file: str = param.strategy[0]
    cash: Decimal = Decimal(param.cash[0])
    return cash, config_file, log_file
