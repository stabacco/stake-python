import pytest


@pytest.mark.asyncio
async def test_show_portfolio(tracing_client):
    return await tracing_client.equities.list()


@pytest.mark.asyncio
async def test_find_products_by_name(tracing_client):
    from stake.product import ProductSearchByName

    request = ProductSearchByName(keyword="techno")
    products = await tracing_client.products.search(request)
    assert len(products) == 10
