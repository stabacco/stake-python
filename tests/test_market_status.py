import pytest


@pytest.mark.asyncio
async def test_check_market_status(tracing_client, fixtures_response):
    market_status = await tracing_client.market.get()
    assert market_status.status.current == "pre"
