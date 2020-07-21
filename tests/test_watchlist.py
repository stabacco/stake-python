import pytest

from stake.watchlist import AddToWatchlistRequest
from stake.watchlist import RemoveFromWatchlistRequest


@pytest.mark.asyncio
async def test_add_to_watchlist(test_client_fixture_generator):
    added = await test_client_fixture_generator.watchlist.add(
        AddToWatchlistRequest(symbol="SPOT")
    )
    assert added.watching

    removed = await test_client_fixture_generator.watchlist.remove(
        RemoveFromWatchlistRequest(symbol="SPOT")
    )
    assert not removed.watching
