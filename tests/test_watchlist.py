import pytest

from stake.watchlist import (
    AddToWatchlistRequest,
    CreateWatchlistRequest,
    DeleteWatchlistRequest,
    RemoveFromWatchlistRequest,
    UpdateWatchlistRequest,
    Watchlist,
)

# flake8: noqa


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_add_to_watchlist(tracing_client):
    added = await tracing_client.watchlist.add(AddToWatchlistRequest(symbol="SPOT"))
    assert added.watching


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_remove_from_watchlist(tracing_client):

    removed = await tracing_client.watchlist.remove(
        RemoveFromWatchlistRequest(symbol="SPOT")
    )
    assert not removed.watching


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_watchlist(tracing_client):
    watched = await tracing_client.watchlist.list()
    assert len(watched) == 10


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_create_watchlist(tracing_client):
    name = "__test_watchlist__"
    watched = await tracing_client.watchlist.create_watchlist(
        CreateWatchlistRequest(name=name)
    )
    assert isinstance(watched, Watchlist)

    update_request = UpdateWatchlistRequest(
        id=watched.watchlist_id, tickers=["TSLA", "GOOG", "MSFT"]
    )
    watched: Watchlist = await tracing_client.watchlist.add_to_watchlist(
        request=update_request
    )
    assert watched.count == 3
    # update again, with the same symbols, nothing should change.
    watched: Watchlist = await tracing_client.watchlist.add_to_watchlist(
        request=update_request
    )
    assert watched.count == 3

    update_request = UpdateWatchlistRequest(
        id=watched.watchlist_id, tickers=["TSLA", "GOOG", "MSFT", "NOK"]
    )
    watched: Watchlist = await tracing_client.watchlist.remove_from_watchlist(
        request=update_request
    )

    assert watched.count == 0

    result = await tracing_client.watchlist.delete_watchlist(
        request=DeleteWatchlistRequest(id=update_request.id)
    )
    assert result
