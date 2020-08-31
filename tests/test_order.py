import pytest


@pytest.mark.asyncio
async def test_list_orders(tracing_client):
    orders = await tracing_client.orders.list()
    import itertools

    order_by_symbol = itertools.groupby(orders, lambda x: x.instrument_symbol)
    print(dict(order_by_symbol).get("ZM"))
    assert len(orders) >= 5
