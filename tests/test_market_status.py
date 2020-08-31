import pytest


@pytest.mark.asyncio
async def test_check_market_status(tracing_client):
    market_status = await tracing_client.market.get()
    assert market_status.status.current == "close"

    is_open = await tracing_client.market.is_open()
    assert not is_open
