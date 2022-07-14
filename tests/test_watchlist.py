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


"""
```python
import stake
import asyncio
from stake.watchlist import Watchlist

async def create_watchlist(name: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.CreateWatchlistRequest(name = name)
        new_watchlist = await stake_session.watchlist.create_watchlist(request=request)
        return new_watchlist

asyncio.run(create_watchlist(name='Stef 3'))


import stake
import asyncio
from stake.watchlist import Watchlist

async def update_watchlist(id: str, tickers: "List[str]") -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.UpdateWatchlistRequest(id=id, tickers=tickers)
        watchlist = await stake_session.watchlist.add_to_watchlist(request=request)
        return watchlist

asyncio.run(update_watchlist(id='146c733c-518d-4123-8ca8-a33d0ed65328', tickers=["TSLA", "MSFT", "GOOG"] ))

import stake
import asyncio
from stake.watchlist import Watchlist

async def get_watchlist(id: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.GetWatchlistRequest(id=id)
        watchlist = await stake_session.watchlist.watchlist(request=request)
        return watchlist

asyncio.run(get_watchlist(id='20accd2e-4955-42f8-b9d2-15d0a196608c'))



import stake
import asyncio
from stake.watchlist import Watchlist

async def remove_from_watchlist(id: str, tickers: "List[str]") -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.UpdateWatchlistRequest(id=id, tickers=tickers)
        watchlist = await stake_session.watchlist.remove_from_watchlist(request=request)
        return watchlist

asyncio.run(remove_from_watchlist(id='20accd2e-4955-42f8-b9d2-15d0a196608c', tickers=["TSLA", "MSFT", "GOOG"] ))


import stake
import asyncio
from stake.watchlist import Watchlist

async def delete_watchlist(id: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.DeleteWatchlistRequest(id=id)
        watchlist = await stake_session.watchlist.delete_watchlist(request=request)
        return watchlist

asyncio.run(delete_watchlist(id='0e431e05-b60d-4432-9bdb-6d09c7d90108'))

import stake
import asyncio
from stake.watchlist import Watchlist

async def delete_watchlist(id: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.DeleteWatchlistRequest(id=id)
        watchlist = await stake_session.watchlist.list()
        return watchlist

asyncio.run(delete_watchlist(id='0e431e05-b60d-4432-9bdb-6d09c7d90108'))


import stake
import asyncio
from stake.watchlist import Watchlist

async def cancel_order(id: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.CancelOrderRequest(order_id=id)
        watchlist = await stake_session.orders.cancel(order=request)
        return watchlist

asyncio.run(cancel_order(id='0e431e05-b60d-4432-9bdb-6d09c7d90108'))



```

"""
