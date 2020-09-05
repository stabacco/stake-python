import pytest


@pytest.mark.asyncio
async def test_list_orders(tracing_client):
    orders = await tracing_client.orders.list()
    assert len(orders) == 9
    assert orders[0].symbol == "NIO"
