import pytest

from stake import constant
from stake.client import StakeClient


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_orders(tracing_client: StakeClient, exchange):
    tracing_client.set_exchange(exchange)
    orders = await tracing_client.orders.list()
    assert len(orders)
    assert orders[0].order_id


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_cancel_order(tracing_client: StakeClient, exchange):
    """Warning, will cancel the first pending order."""
    tracing_client.set_exchange(exchange)
    orders = await tracing_client.orders.list()
    how_many_orders = len(orders)
    cancel_order = await tracing_client.orders.cancel(orders[0])
    assert cancel_order
    orders = await tracing_client.orders.list()
    assert len(orders) == how_many_orders - 1

@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_brokerage(tracing_client: StakeClient, exchange):
    tracing_client.set_exchange(exchange)
    brokerage = await tracing_client.orders.brokerage(order_amount=1.0)
    assert brokerage

