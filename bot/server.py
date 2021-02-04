"""The geisten bot service"""
import logging
from datetime import datetime
from fastapi import FastAPI

from pydantic import BaseModel
from bot.bot import OrderBook, Order, rsi_analyzer


class Offer(BaseModel):
    """The single price offer class"""
    timestamp: datetime
    price: float


class PlaceOrder(BaseModel):
    """The created order by the bot"""
    timestamp: datetime
    amount: float
    price: float


data: list[Offer] = []
prices: list(float) = []

app = FastAPI()

def handler(type, timestamp, amount, price):
    print("order: {}, at: {}, amount: {}, price: {}, sum: {}".format(type,timestamp, amount, price, amount * price))
    
logging.basicConfig(filename='order_book.log', encoding='utf-8', level=logging.DEBUG)
order_book = OrderBook(1000, rsi_analyzer(0.003, .008, 24,48),handler)


@app.get("/")
async def root():
    """Return the index page"""
    return {"message": "Hello World"}


@app.get("/offers", response_model=list[Offer])
async def offers() -> list[Offer]:
    """Return a list of the last trade offers"""
    return data


@app.post("/offers/", response_model=Order)
async def post_offer(offer: Offer):
    """Create a new offer"""
    data.append(offer)
    prices.append(offer.price)
    order: Order = order_book(prices)
    return PlaceOrder(order.timestamp, order.amount, order.price)
