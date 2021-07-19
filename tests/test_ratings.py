import datetime

import pytest

from stake import RatingsRequest


@pytest.mark.asyncio
async def test_list_ratings(tracing_client):
    request = RatingsRequest(symbols=["AAPL", "MSFT"], limit=4)
    ratings = await tracing_client.ratings.list(request)
    assert len(ratings) == 4
    assert ratings[0].symbol in ("AAPL", "MSFT")
    assert ratings[0].rating_current == "Buy"
    assert ratings[0].updated == datetime.datetime(
        2021, 7, 16, 11, 40, 23, tzinfo=datetime.timezone.utc
    )


@pytest.mark.asyncio
async def test_list_ratings_unknown(tracing_client):
    request = RatingsRequest(symbols=["NOTEXIST"], limit=4)
    ratings = await tracing_client.ratings.list(request)
    assert len(ratings) == 0
