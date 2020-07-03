import pytest

from stake.trade import LimitBuyRequest
from stake.trade import StopBuyRequest


@pytest.mark.asyncio
async def test_stop_buy(test_client_fixture_generator):
    # amountCash too low.
    with pytest.raises(ValueError):
        await test_client_fixture_generator.trades.buy(
            StopBuyRequest(symbol="AAPL", price=400, amountCash=5)
        )

    # price too low.
    with pytest.raises(RuntimeError):
        await test_client_fixture_generator.trades.buy(
            StopBuyRequest(symbol="AAPL", price=10, amountCash=10)
        )


@pytest.mark.asyncio
async def test_limit_buy(test_client_fixture_generator):
    with pytest.raises(RuntimeError):
        await test_client_fixture_generator.trades.buy(
            LimitBuyRequest(symbol="AAPL", limitPrice=400, quantity=100)
        )


@pytest.mark.asyncio
async def test_limit_sell(test_client_fixture_generator):
    with pytest.raises(RuntimeError):
        await test_client_fixture_generator.trades.sell(
            LimitBuyRequest(symbol="AAPL", limitPrice=400, quantity=100)
        )
