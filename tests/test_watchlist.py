import json

import pytest

from stake.constant import Url
from stake.watchlist import AddToWatchlistRequest
from stake.watchlist import RemoveFromWatchlistRequest


@pytest.mark.asyncio
async def test_add_to_watchlist(test_client_fixture_generator):
    added = await test_client_fixture_generator.watchlist.add(
        AddToWatchlistRequest(symbol="SPOT")
    )
    assert added.watching


@pytest.mark.asyncio
async def test_remove_from_watchlist(test_client_fixture_generator):
    removed = await test_client_fixture_generator.watchlist.remove(
        RemoveFromWatchlistRequest(symbol="SPOT")
    )
    assert not removed.watching


@pytest.mark.asyncio
async def test_list_watchlist(test_client_fixture_generator):
    watched = await test_client_fixture_generator.watchlist.list()
    assert len(watched) == 6
