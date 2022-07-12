import asyncio

import aiohttp
import pytest

from stake.client import HttpClient
from stake.constant import NYSE
from stake.product import Product


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_show_portfolio(tracing_client):
    return await tracing_client.equities.list()


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_find_products_by_name(tracing_client):
    from stake.product import ProductSearchByName

    request = ProductSearchByName(keyword="techno")
    products = await tracing_client.products.search(request)
    assert len(products) == 10


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
