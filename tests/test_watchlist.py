import pytest
from pydantic import BaseModel

import stake
from stake import constant
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
async def test_add_to_watchlist(tracing_client: stake.StakeClient):
    added = await tracing_client.watchlist.add(AddToWatchlistRequest(symbol="SPOT"))
    assert added.watching


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_remove_from_watchlist(tracing_client: stake.StakeClient):

    removed = await tracing_client.watchlist.remove(
        RemoveFromWatchlistRequest(symbol="SPOT")
    )
    assert not removed.watching


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_watchlist(tracing_client: stake.StakeClient):
    watched = await tracing_client.watchlist.list()
    assert len(watched) == 10


@pytest.mark.parametrize(
    "exchange, symbols",
    (
        (constant.NYSE, ["TSLA", "GOOG", "MSFT", "NOK"]),
        (constant.ASX, ["COL", "WDS", "BHP", "OOO"]),
    ),
)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_create_watchlist(
    tracing_client: stake.StakeClient, exchange: BaseModel, symbols: str
):
    name = f"test_watchlist__{exchange.__class__.__name__}"
    tracing_client.set_exchange(exchange)
    watched = await tracing_client.watchlist.create_watchlist(
        CreateWatchlistRequest(name=name)
    )
    if not watched:
        return
    assert len(symbols[:3]) == 3
    update_request = UpdateWatchlistRequest(
        id=watched.watchlist_id, tickers=symbols[:3]
    )

    watched = await tracing_client.watchlist.add_to_watchlist(request=update_request)
    assert watched.count == 3
    # update again, with the same symbols, nothing should change.
    watched = await tracing_client.watchlist.add_to_watchlist(request=update_request)
    assert watched.count == 3

    update_request = UpdateWatchlistRequest(
        id=watched.watchlist_id,
        tickers=symbols,
    )
    watched = await tracing_client.watchlist.remove_from_watchlist(
        request=update_request
    )

    assert watched.count == 0

    result = await tracing_client.watchlist.delete_watchlist(
        request=DeleteWatchlistRequest(id=update_request.id)
    )
    assert result
