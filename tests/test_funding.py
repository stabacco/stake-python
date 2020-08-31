import pytest

from stake.funding import FundingRequest


@pytest.mark.asyncio
async def test_fx_conversion(tracing_client):
    fundings = await tracing_client.fundings.list(FundingRequest())
    print(fundings[0].dict(by_alias=True))


@pytest.mark.asyncio
async def test_cash_available(tracing_client):
    cash_available = await tracing_client.fundings.cash_available()
    import pprint

    pprint.pprint(cash_available.dict(by_alias=True))
