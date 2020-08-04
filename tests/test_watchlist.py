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


from aioresponses import aioresponses


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.mark.asyncio
async def test_aioresponses(mock_aioresponse):
    from client import HttpClient

    url = HttpClient.url(Url.account_balance)
    mock_aioresponse.get(url, payload=dict(foo="bar"))

    data = await HttpClient.get(url)
    assert data == dict(foo="bar")
