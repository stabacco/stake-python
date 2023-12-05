# this module contains tests that run real stake api calls


import pytest

import stake
from stake import constant
from stake.transaction import TransactionRecordRequest


@pytest.mark.parametrize("exchange", (constant.NYSE,))
@pytest.mark.asyncio
async def test_integration_NYSE(exchange):
    async with stake.StakeClient(exchange=exchange) as session:
        await session.watchlist.list_watchlists()
        await session.equities.list()
        await session.orders.list()
        await session.market.get()
        await session.market.is_open()
        await session.fundings.cash_available()

        request = stake.TransactionRecordRequest(limit=10)
        transactions = await session.transactions.list(request)
        assert len(transactions) == 10
        await session.fundings.list(TransactionRecordRequest(limit=100))


@pytest.mark.parametrize("exchange", (constant.ASX,))
@pytest.mark.asyncio
async def test_integration_ASX(exchange):
    async with stake.StakeClient(exchange=exchange) as session:
        await session.watchlist.list_watchlists()
        await session.equities.list()
        await session.orders.list()
        await session.market.get()
        await session.market.is_open()
        await session.fundings.cash_available()

        from stake.asx.funding import FundingRequest as ASXFundingRequest
        from stake.asx.funding import Sort
        from stake.asx.transaction import (
            TransactionRecordRequest as ASXTransactionRecordRequest,
        )

        request = ASXFundingRequest(
            limit=10, sort=[Sort(direction="asc", attribute="insertedAt")]
        )
        result = await session.fundings.list(request=request)
        assert len(result.fundings) == 10

        request = ASXTransactionRecordRequest(
            limit=10, sort=[Sort(direction="desc", attribute="insertedAt")]
        )
        result = await session.transactions.list(request=request)
        assert len(result.transactions) == 10
