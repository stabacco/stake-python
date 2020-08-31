import pytest

"""
{"response":{"message":"Market is open","unixtime":"1598535062.41974","error":"Success","status":{"change_at":"16:00:00","next":"after","current":"open"},"elapsedtime":"0","date":"2020-08-27 09:31:02.4197365-04:00","versionNumber":"2.56.0"}}
"""


@pytest.mark.asyncio
async def test_check_market_status(tracing_client):
    market_status = await tracing_client.market.get()
    assert market_status.status.current == "close"

    is_open = await tracing_client.market.is_open()
    assert not is_open
