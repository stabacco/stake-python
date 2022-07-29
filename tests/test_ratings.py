import pytest

import stake
from stake import RatingsRequest


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_ratings(tracing_client: stake.StakeClient):
    request = RatingsRequest(symbols=["AAPL", "MSFT"], limit=4)
    ratings = await tracing_client.ratings.list(request)
    assert len(ratings) == 4
    assert ratings[0].symbol in ("AAPL", "MSFT")


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_ratings_unknown(tracing_client: stake.StakeClient):
    request = RatingsRequest(symbols=["NOTEXIST"], limit=4)
    ratings = await tracing_client.ratings.list(request)
    assert len(ratings) == 0
