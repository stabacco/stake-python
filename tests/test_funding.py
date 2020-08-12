import pytest

from stake.funding import FundingRequest
@pytest.mark.asyncio
async def test_fundings(test_client_fixture_generator):
    fundings = await test_client_fixture_generator.fundings.list(FundingRequest())
    print(fundings[0].dict(by_alias=True))