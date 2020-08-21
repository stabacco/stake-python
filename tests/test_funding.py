import pytest

from stake.funding import FundingRequest
@pytest.mark.asyncio
async def test_fx_conversion(test_client_fixture_generator):
    fundings = await test_client_fixture_generator.fx.list(FundingRequest())
    print(fundings[0].dict(by_alias=True))

@pytest.mark.asyncio
async def test_cash_available(test_client_fixture_generator):
    cash_available = await test_client_fixture_generator.fundings.cash_available()
    import pprint; pprint.pprint(cash_available.dict(by_alias=True))
