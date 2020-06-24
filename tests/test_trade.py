import pytest
from trade import LimitBuyRequest
from trade import MarketBuyRequest
from trade import StopBuyRequest

from stake import client


@pytest.mark.asyncio
async def test_stop_buy():
    c = await client.StakeClient()

    # amountCash too low.
    with pytest.raises(ValueError):
        await c.trades.buy(StopBuyRequest(symbol="AAPL", price=400, amountCash=5))

    # price too low.
    with pytest.raises(RuntimeError):
        await c.trades.buy(StopBuyRequest(symbol="AAPL", price=10, amountCash=10))

    # all good.
    # await c.trades.buy(StopBuyRequest(symbol="AAPL", price=400, amountCash=10))
