import pytest
from stake.constant import ASX, NYSE

from stake.funding import FundingRequest


@pytest.mark.parametrize("exchange_arg", [ASX])
@pytest.mark.asyncio
async def test_list_fundings(tracing_client):
    fundings = await tracing_client.fundings.list(FundingRequest())
    print(fundings[0].json(indent=2))
    assert len(fundings) == 11


@pytest.mark.asyncio
async def test_cash_available(tracing_client):
    cash_available = await tracing_client.fundings.cash_available()
    assert cash_available.cash_available_for_withdrawal == 551.14
    assert cash_available.cash_settlement[0].utc_time.month == 9


@pytest.mark.asyncio
async def test_funds_in_flight(tracing_client):
    funds_in_flight = await tracing_client.fundings.in_flight()
    assert len(funds_in_flight) == 1
    assert funds_in_flight[0].transaction_type == "Poli"
