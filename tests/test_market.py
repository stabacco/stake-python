import pytest

import stake
from stake import constant


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_check_market_status(tracing_client: stake.StakeClient, exchange):
    tracing_client.set_exchange(exchange)
    market_status = await tracing_client.market.get()
    assert market_status.status.current == "close"
