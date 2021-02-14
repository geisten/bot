"""Connect to the binance cybercoin trader
 see https://dev.binance.vision for further information
"""

import hashlib
import hmac
import json
import time
from datetime import datetime
from decimal import Decimal
from typing import Callable
from urllib.parse import urlencode

import asyncio
import httpx
import websockets
from websockets import WebSocketClientProtocol

from .trader import TradingBook, Order


async def consumer_handler(websocket: WebSocketClientProtocol, trading_book: TradingBook) -> None:
    """Read the price ticker data from the binance websocket server"""
    async for message in websocket:
        print(message)
        trade = json.loads(message)
        price = Decimal(trade['p'])
        timestamp = datetime.utcfromtimestamp(trade['T'] / 1000.0)
        trading_book(timestamp, price)


async def consume_websocket(websocket_resource_url: str, trading_book: TradingBook) -> None:
    """ Connect and handle the received data from the websocket"""
    print(f"connect to: '{websocket_resource_url}'")
    async with websockets.connect(websocket_resource_url) as websocket:
        print("wait on websocket")
        await consumer_handler(websocket, trading_book)


async def order_status_consumer(order_id: str, symbol: str, order_address: str, api_key: bytes, secret_key: bytes,
                                trading_book: TradingBook):
    """Check the order status of the placed order"""
    async with httpx.AsyncClient() as client:
        print("check order status of order: " + order_id)
        params = {'symbol': symbol, 'origClientOrderId': order_id, 'recvWindow': 5000,
                  'timestamp': int(time.time() * 1e3)}
        response = await client.get(order_address, params=params, headers={'X-MBX-APIKEY': api_key})
        status = response['status']
        if status == 'NEW':
            print("Order still with status new")
        elif status == 'FILLED':
            print("Order filled")
            trading_book.complete(order_id)


async def order_producer(symbol: str, order_address: str, api_key: bytes, secret_key: bytes,
                         order: Order, trading_book: TradingBook):
    """Place a new buy or sell order to the binance order book"""
    async with httpx.AsyncClient() as client:
        print("place order: " + str(order))
        payload = {'symbol': symbol, 'side': 'SELL', 'type': 'LIMIT', 'timeInForce': 'GTC', 'quantity': order.amount,
                   'price': order.price, 'recvWindow': 5000, 'timestamp': int(order.timestamp.timestamp() * 1e3)}
        signature = hmac.new(secret_key, urlencode(payload).encode('ASCII'), hashlib.sha256).hexdigest()
        payload['signature'] = signature
        headers = {'X-MBX-APIKEY': api_key}
        response = await client.post(order_address, headers=headers,
                                     data=urlencode(payload).encode('ASCII'))
        status = response['status']
        order_id = response['orderId']
        if status == 'NEW':
            trading_book.place(order_id, order)


async def order_producers(trading_book: TradingBook, symbol: str, order_address: str, api_key: bytes,
                          secret_key: bytes):
    """Create a list with all orders to be placed"""
    task_list = []
    for order_id, order in trading_book.created():
        task_list.append(
            order_producer(symbol, order_address, api_key, secret_key, order, trading_book))
    if task_list:
        trading_book.created_reset()
        return asyncio.gather(*task_list)


def order_producers_create(symbol: str, order_address: str, api_key: bytes,
                           secret_key: bytes):
    """Return a function to place the orders from the trading book"""
    def producers(trading_book: TradingBook):
        return order_producers(trading_book, symbol, order_address, api_key, secret_key)

    return producers


def order_status_consumer_list_create(symbol: str, order_address: str,
                                      api_key: bytes, secret_key: bytes):
    """Return a function to check the state of the placed order"""
    def func(order_book: TradingBook):
        return order_status_consumer_list(order_book, symbol, order_address,
                                          api_key, secret_key)

    return func


async def order_status_consumer_list(order_book: TradingBook, symbol: str, order_address: str,
                                     api_key: bytes, secret_key: bytes):
    """Return a list with all coroutines to check the status of the placed order"""
    task_list = []
    for order_id, order in order_book.placed():
        task_list.append(order_status_consumer(order_id, symbol, order_address, api_key, secret_key, order_book))
    if task_list:
        return asyncio.gather(*task_list)


def run_trader(trading_book: TradingBook, status_consumer: Callable[[TradingBook], any],
               producers: Callable[[TradingBook], any],
               websocket_consumer):
    """Run the event loop to handle the REST producers, consumers and websocket consumers"""
    loop = asyncio.get_event_loop()
    print("run binance client")
    all_groups = asyncio.gather(websocket_consumer, status_consumer(trading_book), producers(trading_book))
    try:
        loop.run_until_complete(all_groups)
    except KeyboardInterrupt:
        print("...Received exit, exiting")
        loop.stop()
    loop.run_forever()
    return loop


def binance_runner(trading_book: TradingBook, order_resource: str, websocket_stream_resource: str, symbol: str,
                   symbol_format: str,
                   api_key: bytes, secret_key: bytes):
    """Run the 'run_trader' function with the created consumers/producers"""
    status_consumer = order_status_consumer_list_create(symbol, order_resource,
                                                        api_key, secret_key)
    producers = order_producers_create(symbol, order_resource, api_key,
                                       secret_key)
    websocket_consumer = consume_websocket(f"{websocket_stream_resource}/{symbol.lower()}@{symbol_format}",
                                           trading_book)
    run_trader(trading_book, status_consumer, producers, websocket_consumer)


def authenticate_to_broker(api_key: bytes, secret_key: bytes):
    """Returns the runner including the authentication keys"""
    def runner(trading_book: TradingBook, order_resource: str, websocket_stream_resource: str, symbol: str,
               symbol_format: str):
        binance_runner(trading_book, order_resource, websocket_stream_resource, symbol, symbol_format, api_key,
                       secret_key)

    return runner


def test_runner(trading_book: TradingBook, symbol: str, symbol_format: str, runner):
    """Start the binance test runner"""
    # "wss://testnet.binance.vision/ws"
    runner(trading_book, "https://testnet.binance.vision/api/v3/order", "wss://stream.binance.com:9443/ws", symbol,
           symbol_format)
