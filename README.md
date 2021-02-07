# The Geisten Trading Bot

A simple project blueprint for python packages.

## Quick Start

To setup this template for your project run

```sh

sh ./configure_project.sh [PROJECT NAME]
```

### Backtesting Framework

Backtesting allows a trader to simulate and analyze the risk and profitability of trading a particular strategy over a period of time. A backtest environment usually consists of four major components:

* A data handler that interfaces with a data set, 
* A strategy that generates a signal to go long or short based on the data, 
* A portfolio that generates orders and manages profit & loss (also known as "PnL"), and
* An Execution Handler that sends the order to the broker and receives the signals that the stock has been bought or sold.

If you want to backtest a trading strategy using Python, you can 1) run your backtests using existing libraries, 2) build your own backtester, or 3) use a cloud trading platform. There are 2 popular libraries for backtesting: [Backtrader](https://www.backtrader.com/) and [Zipline](https://www.zipline.io/). However, I decided to implement my own small framework for testing my strategies. Normally I would advise against reinventing the wheel every time. Nevertheless, the effort is limited and it is possible to implement a solution with low dependencies.

For testing strategies the geisten bot can be started from the command line.

### Geisten Trading Bot Database Design

A plain CSV data file format is chosen as Database for the geisten trading bot.

There are several reasons for choosing CSV which are briefly discussed as follows:

Time series data will not be overridden and will rarely be inserted within existing data series. The data is always added to the end of the existing file and not modified. The big advantage of CSV is that the data is human readable and can be displayed and analyzed even with basic Linux/Unix on-board tools. Practically every relevant mathematical analysis program can process CSV files. And even if the processing of simple files becomes too complex over time, you can transfer the CSV files to any database system using simple utilities.  
However, a main argument for CSV files in our application is the reduction of dependencies while respecting the KISS principle.

## Developing

Use `make lint` to validate the code changes.

Before changes are added and pushed, the code must be validated via `make lint` . A zero tolerance policy applies when committing changes to the 'main' branch. Only bug-free code is allowed to be checked in.
