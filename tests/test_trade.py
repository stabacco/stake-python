import pytest

import stake
from stake import constant
from stake.asx import trade as asx_trade
from stake.trade import LimitBuyRequest, MarketBuyRequest, StopBuyRequest


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_stop_buy(tracing_client: stake.StakeClient):
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


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_limit_buy(tracing_client: stake.StakeClient):
    with pytest.raises(RuntimeError):
        await tracing_client.trades.buy(
            LimitBuyRequest(symbol="AAPL", limitPrice=460, quantity=1000)
        )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_limit_sell(tracing_client: stake.StakeClient):
    with pytest.raises(RuntimeError):
        await tracing_client.trades.sell(
            LimitBuyRequest(symbol="AAPL", limitPrice=400, quantity=100)
        )


@pytest.mark.parametrize(
    "exchange, request_",
    (
        (
            constant.NYSE,
            MarketBuyRequest(symbol="TSLA", amount_cash=20, comment="from cloud"),
        ),
        (constant.ASX, asx_trade.MarketBuyRequest(symbol="COL", units=20)),
        (
            constant.NYSE,
            LimitBuyRequest(
                symbol="TSLA", limit_price=120, quantity=1, comment="from cloud"
            ),
        ),
        (constant.ASX, asx_trade.LimitBuyRequest(symbol="COL", units=20, price=12.0)),
    ),
)
@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_successful_trade(tracing_client: stake.StakeClient, exchange, request_):
    tracing_client.set_exchange(exchange)

    trade = await tracing_client.trades.buy(request_)
    assert trade

    orders = await tracing_client.orders.list()

    # cancel the order
    await tracing_client.orders.cancel(orders[0])


@pytest.mark.parametrize(
    "exchange, request_",
    (
        (constant.ASX, asx_trade.MarketSellRequest(symbol="COL", units=20)),
        (constant.ASX, asx_trade.LimitSellRequest(symbol="COL", units=20, price=15.0)),
    ),
)
@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_sell(tracing_client: stake.StakeClient, exchange, request_):
    tracing_client.set_exchange(exchange)

    trade = await tracing_client.trades.sell(request_)
    assert trade

    orders = await tracing_client.orders.list()
    assert orders
    # cancel the order
    await tracing_client.orders.cancel(orders[0])
