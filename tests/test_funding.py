from typing import Union

import pytest

import stake
from stake import constant
from stake.asx.funding import FundingRequest as ASXFundingRequest
from stake.funding import TransactionRecordRequest as NYSEFundingRequest


@pytest.mark.parametrize(
    "exchange, request_",
    (
        (constant.NYSE, NYSEFundingRequest(limit=1000)),
        (constant.ASX, ASXFundingRequest(limit=3)),
    ),
)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_fundings(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
    request_: Union[ASXFundingRequest, NYSEFundingRequest],
):
    tracing_client.set_exchange(exchange=exchange)
    await tracing_client.fundings.list(request_)


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_cash_available(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
):
    tracing_client.set_exchange(exchange)
    cash_available = await tracing_client.fundings.cash_available()
    assert cash_available.cash_available_for_withdrawal == 1000.0


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_funds_in_flight(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
):
    tracing_client.set_exchange(exchange=exchange)
    await tracing_client.fundings.in_flight()


"""
import asyncio

import stake
from stake.constant import ASX
from stake.watchlist import Watchlist


async def cash_available() -> "Watchlist":
    async with stake.StakeClient(exchange=ASX) as stake_session:
        cash_available = await stake_session.fundings.cash_available()
        return cash_available


asyncio.run(cash_available())


import asyncio

import stake
from stake.constant import ASX
from stake.watchlist import Watchlist


async def market_status() -> "Watchlist":
    async with stake.StakeClient(exchange=ASX) as stake_session:
        is_open = await stake_session.market.get()
        return is_open


asyncio.run(market_status())

import asyncio

import stake
from stake.constant import ASX
from stake.watchlist import UpdateWatchlistRequest, Watchlist


async def update_watchlist() -> "Watchlist":
    request = UpdateWatchlistRequest(
        id="1f179b38-6a47-4f84-bdea-45aaa37879af", symbols=["A3D"]
    )
    async with stake.StakeClient(exchange=ASX) as stake_session:
        is_open = await stake_session.watchlist.add_to_watchlist(request=request)
        return is_open


asyncio.run(update_watchlist())

import asyncio

import stake
from stake.constant import ASX
from stake.watchlist import UpdateWatchlistRequest, Watchlist


async def update_watchlist() -> "Watchlist":
    request = UpdateWatchlistRequest(
        id="1f179b38-6a47-4f84-bdea-45aaa37879af", symbols=["A3D"]
    )
    async with stake.StakeClient(exchange=ASX) as stake_session:
        is_open = await stake_session.watchlist.add_to_watchlist(request=request)
        return is_open


asyncio.run(update_watchlist())


import asyncio

import stake
from stake.asx.trade import MarketBuyRequest
from stake.constant import ASX


async def buy_asx_() -> "Watchlist":
    request = MarketBuyRequest(type="MARKET", symbol="COL", units=30)
    async with stake.StakeClient(exchange=ASX) as stake_session:
        order = await stake_session.trades.buy(request=request)
        return order


asyncio.run(buy_asx_())
"""
