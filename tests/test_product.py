import asyncio
from typing import List

import aiohttp
import pytest
from pydantic import BaseModel

from stake import asx, constant
from stake.client import HttpClient, StakeClient
from stake.constant import NYSE
from stake.product import Product, ProductsClient


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_find_products_by_name(tracing_client: StakeClient, exchange):
    from stake.product import ProductSearchByName

    tracing_client.set_exchange(exchange)
    request = ProductSearchByName(keyword="techno")
    products = await tracing_client.products.search(request)
    assert len(products) == 10
    assert products[0].__class__.__name__ == "Instrument"


@pytest.mark.asyncio
async def test_product_serializer():

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        await session.get(HttpClient.url(NYSE.symbol.format(symbol="MSFT")))

        async def _get_symbol(symbol):
            response = await session.get(
                HttpClient.url(NYSE.symbol.format(symbol=symbol))
            )
            return await response.json()

        coros = [_get_symbol(symbol) for symbol in {"MSFT", "TSLA", "GOOG"}]

        results = await asyncio.gather(*coros)
        assert [
            Product(**serialized_product["products"][0])
            for serialized_product in results
        ]


@pytest.mark.asyncio
async def test_get_us_product_adds_quote_bid_and_ask():
    class Client:
        exchange = constant.NYSE

        async def get(self, url):
            return {
                "products": [
                    {
                        "id": "16bf66e3-94f5-4357-88d0-48e2a44f44bf",
                        "symbol": "SE",
                        "description": "Sea Limited",
                        "urlImage": "https://example.com/se.png",
                        "name": "Sea Limited",
                        "dailyReturn": 1.75,
                        "dailyReturnPercentage": 2.01,
                        "lastTraded": 89.02,
                        "monthlyReturn": 0,
                        "popularity": 1,
                        "watched": 1,
                        "news": 0,
                        "bought": 1,
                        "viewed": 1,
                        "productType": "Instrument",
                        "encodedName": "sea-limited-se",
                        "period": "YEAR RETURN",
                        "instrumentTags": [],
                        "childInstruments": [],
                    }
                ]
            }

        async def post(self, url, payload):
            assert url == constant.NYSE.quotes
            assert payload == {"symbols": ["SE"]}
            return [
                {
                    "symbol": "SE",
                    "bid": 88.5,
                    "ask": 90,
                    "lastTrade": 89.02,
                    "marketStatus": "POSTMARKET",
                }
            ]

    client = Client()
    product = await ProductsClient(client).get("SE")
    assert product
    assert product.bid == 88.5
    assert product.ask == 90
    assert product.last_trade == 89.02
    assert product.market_status == "POSTMARKET"


@pytest.mark.parametrize(
    "exchange, symbols",
    ((constant.NYSE, ["TSLA", "MSFT", "GOOG"]), (constant.ASX, ["ANZ", "WDS", "COL"])),
)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_get_product(
    tracing_client: StakeClient, exchange: BaseModel, symbols: List[str]
):
    tracing_client.set_exchange(exchange)
    for symbol in symbols:
        product = await tracing_client.products.get(symbol)
    assert product.__class__.__name__ == "Product"


@pytest.mark.parametrize(
    "exchange, keyword", ((constant.ASX, "CBA"), (constant.NYSE, "MSFT"))
)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_search_products(
    tracing_client: StakeClient, exchange: BaseModel, keyword: str
):
    tracing_client.set_exchange(exchange)
    search_results = await tracing_client.products.search(
        asx.ProductSearchByName(keyword=keyword)
    )
    assert search_results

    product = await tracing_client.products.product_from_instrument(search_results[0])
    assert product


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_asx_product_depth(tracing_client: StakeClient):
    tracing_client.set_exchange(constant.ASX)
    assert isinstance(tracing_client.products, asx.product.ProductsClient)

    depth = await tracing_client.products.depth("ORG")

    assert depth.ticker == "ORG"
    assert isinstance(depth.total_buy_count, int)
    assert isinstance(depth.total_sell_count, int)
    assert isinstance(depth.total_buy_volume, int)
    assert isinstance(depth.total_sell_volume, int)
    assert depth.buy_orders
    assert depth.sell_orders

    buy_order = depth.buy_orders[0]
    assert isinstance(buy_order.price, float)
    assert isinstance(buy_order.volume, int)
    assert isinstance(buy_order.number_of_orders, int)
    assert buy_order.orders
    assert isinstance(buy_order.orders[0].exchange, str)
    assert isinstance(buy_order.orders[0].undisclosed, bool)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_asx_product_course_of_sales(tracing_client: StakeClient):
    tracing_client.set_exchange(constant.ASX)
    assert isinstance(tracing_client.products, asx.product.ProductsClient)

    sales = await tracing_client.products.course_of_sales("ORG")

    assert sales.ticker == "ORG"
    assert isinstance(sales.total_volume, int)
    assert isinstance(sales.total_trades, int)
    assert isinstance(sales.total_value, float)
    assert sales.course_of_sales

    sale = sales.course_of_sales[0]
    assert isinstance(sale.id, str)
    assert isinstance(sale.instrument_code_id, str)
    assert isinstance(sale.exchange_market, str)
    assert isinstance(sale.price, float)
    assert isinstance(sale.volume, int)
    assert isinstance(sale.value, float)
    assert isinstance(sale.trade_time_millis, int)
