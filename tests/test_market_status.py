import pytest


@pytest.mark.asyncio
async def test_check_market_status(test_client):
    market_status = await test_client.market.get()
    assert market_status.status.current == "close"

    is_open = await test_client.market.is_open()
    assert not is_open
