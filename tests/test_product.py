import asyncio
from typing import List

import aiohttp
import pytest
from pydantic import BaseModel

from stake import asx, constant
from stake.client import HttpClient, StakeClient
from stake.constant import NYSE
from stake.product import Product


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
