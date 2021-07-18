import pytest

from stake import RatingsRequest


@pytest.mark.asyncio
async def test_list_ratings(tracing_client):
    request = RatingsRequest(symbols=["AAPL", "MSFT"], limit=4)
    ratings = await tracing_client.ratings.list(request)
    assert len(ratings) == 4
    assert ratings[0].symbol in ("AAPL", "MSFT")


@pytest.mark.asyncio
async def test_list_ratings_unknown(tracing_client):
    request = RatingsRequest(symbols=["NOTEXIST"], limit=4)
    ratings = await tracing_client.ratings.list(request)
    assert len(ratings) == 0
