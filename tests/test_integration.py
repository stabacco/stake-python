# this module contains tests that run real stake api calls


import pytest

import stake


@pytest.mark.asyncio
async def test_integration():
    async with stake.StakeClient() as session:
        await session.watchlist.list()
        await session.equities.list()
        await session.orders.list()
        await session.market.get()
        request = stake.FxConversionRequest(
            from_currency="USD", to_currency="AUD", from_amount=1000.0
        )
        conversion_result = await session.fx.convert(request)
        assert conversion_result.rate
        request = stake.TransactionRecordRequest(limit=10)
        transactions = await session.transactions.list(request)
        assert len(transactions) == 10
        await session.fundings.cash_available()
        await session.fundings.in_flight()
