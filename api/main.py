from getters.poe_trade import get_poetrade_data
from getters.rmt_site import get_rmt_data
from transforms.currency_purchase import currency_purchase
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RMTBase(BaseModel):
    pay_currency: str
    recv_currency: str


class POETradeBase(BaseModel):
    pay_currency: str
    recv_currency: str


class DetailedCurrencyPurchase(BaseModel):
    pay_currency: str
    pay_price_poe: float
    recv_currency: str
    recv_price_poe: float
    pay_price_rmt: float
    recv_price_rmt: float
    rmt_recommendation: str
    rmt_recommendation_weight: str
    pay_price_rmt_diff: float
    pay_price_rmt_diff_percent: float
    timestamp: str


class SimpleCurrencyPurchase(BaseModel):
    pay_currency: str
    recv_currency: str
    rmt_recommendation: str
    rmt_recommendation_weight: str
    timestamp: str


@app.get(
    "/trade-values/rmt",
    tags=["trade-values"],
    responses={200: {"description": "OK"}},
    response_model=RMTBase,
)
async def rmt(pay_currency: int, recv_currency: int):
    return get_rmt_data(str(pay_currency), str(recv_currency))


@app.get(
    "/trade-values/poetrade",
    tags=["trade-values"],
    responses={200: {"description": "OK"}},
    response_model=POETradeBase,
)
async def poetrade(pay_currency: int, recv_currency: int):
    return get_poetrade_data(str(pay_currency), str(recv_currency))


@app.get(
    "/currency-purchase/detailed",
    tags=["currency-purchase"],
    responses={200: {"description": "OK"}},
    response_model=DetailedCurrencyPurchase,
)
async def currency_purchase_detailed(pay_currency: int, recv_currency: int):
    output = currency_purchase(pay_currency, recv_currency, method="detailed")
    return output


@app.get(
    "/currency-purchase/simple",
    tags=["currency-purchase"],
    responses={200: {"description": "OK"}},
    response_model=SimpleCurrencyPurchase,
)
async def currency_purchase_simple(pay_currency: int, recv_currency: int):
    output = currency_purchase(pay_currency, recv_currency, method="simple")
    return output
