import pytest

from stake.order import CancelOrderRequest
from stake.trade import LimitBuyRequest, MarketBuyRequest, StopBuyRequest


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
            StopBuyRequest(symbol="AMD", price=10, amountCash=10)
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


@pytest.mark.skip(reason="This will actually perform a trade")
async def test_successful_trade(tracing_client):
    request_to_buy = MarketBuyRequest(
        symbol="TSLA", amount_cash=20, comment="from cloud"
    )
    trade = await tracing_client.trades.buy(request_to_buy)
    assert trade

    # cancel the order
    await tracing_client.orders.cancel(CancelOrderRequest(order_id=trade.dw_order_id))
