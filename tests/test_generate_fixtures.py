import pytest


@pytest.mark.asyncio
async def test_show_transactions(tracing_client):
    from stake import transaction

    request = transaction.TransactionRecordRequest(limit=6)
    await tracing_client.transactions.list(request)

    request = transaction.TransactionRecordRequest(limit=7)
    return await tracing_client.transactions.list(request)


@pytest.mark.asyncio
async def test_show_portfolio(tracing_client):
    return await tracing_client.equities.list()


@pytest.mark.asyncio
async def test_show_pending_orders(tracing_client):
    return await tracing_client.orders.list()


@pytest.mark.asyncio
async def test_show_fundings(tracing_client):
    from stake.funding import FundingRequest

    request = FundingRequest()
    return await tracing_client.fundings.list(request=request)


@pytest.mark.asyncio
async def test_find_products_by_name(tracing_client):
    from stake.product import ProductSearchByName

    request = ProductSearchByName(keyword="techno")
    products = await tracing_client.products.search(request)
    assert len(products) == 10


# @pytest.mark.asyncio
# async def test_add_stop_sell_for_every_equity_if_loses_5_percent(
#     tracing_client,
# ):
#     owned_equities = await tracing_client.equities.list()
#     for equity in owned_equities.equityPositions:
#         import pprint

# pprint.pprint(equity.dict())
# print(
#     equity.name,
#     equity.unrealizedPL,
#     equity.lastTrade,
#     100 * equity.unrealizedPL / equity.marketValue,
# )
