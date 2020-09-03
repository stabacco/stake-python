import pytest

from stake.watchlist import AddToWatchlistRequest, RemoveFromWatchlistRequest
from tests.conftest import fixtures_response

# flake8: noqa


@pytest.mark.asyncio
async def test_add_to_watchlist(tracing_client, fixtures_response):
    added = await tracing_client.watchlist.add(AddToWatchlistRequest(symbol="SPOT"))
    assert added.watching


@pytest.mark.asyncio
async def test_remove_from_watchlist(tracing_client, fixtures_response):

    removed = await tracing_client.watchlist.remove(
        RemoveFromWatchlistRequest(symbol="SPOT")
    )
    assert not removed.watching


@pytest.mark.asyncio
async def test_list_watchlist(tracing_client, fixtures_response):
    watched = await tracing_client.watchlist.list()
    assert len(watched) == 7
