import pytest


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_orders(tracing_client):
    orders = await tracing_client.orders.list()
    assert len(orders) == 1
    assert orders[0].symbol == "TQQQ"
