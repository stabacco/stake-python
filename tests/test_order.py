import pytest


@pytest.mark.asyncio
async def test_list_orders(tracing_client):
    orders = await tracing_client.orders.list()
    import itertools

    assert len(orders) == 3
    assert orders[0].symbol == "NIO"
