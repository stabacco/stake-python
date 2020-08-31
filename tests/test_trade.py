import pytest

from stake.trade import LimitBuyRequest
from stake.trade import StopBuyRequest


@pytest.mark.asyncio
async def test_stop_buy(tracing_client):
    # amountCash too low.
    with pytest.raises(ValueError):
        await tracing_client.trades.buy(
            StopBuyRequest(symbol="AAPL", price=400, amountCash=5)
        )

    # price too low.
    with pytest.raises(RuntimeError):
        await tracing_client.trades.buy(
            StopBuyRequest(symbol="AAPL", price=10, amountCash=10)
        )


@pytest.mark.asyncio
async def test_limit_buy(tracing_client):
    with pytest.raises(RuntimeError):
        await tracing_client.trades.buy(
            LimitBuyRequest(symbol="AAPL", limitPrice=460, quantity=1000)
        )


@pytest.mark.asyncio
async def test_limit_sell(tracing_client):
    with pytest.raises(RuntimeError):
        await tracing_client.trades.sell(
            LimitBuyRequest(symbol="AAPL", limitPrice=400, quantity=100)
        )
