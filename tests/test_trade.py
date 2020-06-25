import pytest
from trade import LimitBuyRequest
from trade import StopBuyRequest


@pytest.mark.asyncio
async def test_stop_buy(test_client):
    # amountCash too low.
    with pytest.raises(ValueError):
        await test_client.trades.buy(
            StopBuyRequest(symbol="AAPL", price=400, amountCash=5)
        )

    # price too low.
    with pytest.raises(RuntimeError):
        await test_client.trades.buy(
            StopBuyRequest(symbol="AAPL", price=10, amountCash=10)
        )


@pytest.mark.asyncio
async def test_limit_buy(test_client):
    with pytest.raises(RuntimeError):
        await test_client.trades.buy(
            LimitBuyRequest(symbol="AAPL", limitPrice=400, quantity=100)
        )
