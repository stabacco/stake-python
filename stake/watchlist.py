import weakref
from typing import List
from typing import Union

from pydantic import BaseModel

from stake.constant import Url

__all__ = ["AddToWatchlistRequest", "RemoveFromWatchlistRequest"]


class AddToWatchlistRequest(BaseModel):
    symbol: str
    watching: bool = True


class RemoveFromWatchlistRequest(BaseModel):
    symbol: str
    watching: bool = False


class WatchlistResponse(BaseModel):
    symbol: str
    watching: bool


class WatchlistClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def list(self) -> List[WatchlistResponse]:
        raise NotImplementedError("Not able to get the watchlist yet.")

    async def _modify_watchlist(
        self, request: Union[AddToWatchlistRequest, RemoveFromWatchlistRequest]
    ) -> WatchlistResponse:
        product = await self._client.products.get(request.symbol)
        assert product
        data = {
            "instrumentID": product.id,
            "userID": self._client.user.userId,
            "watching": request.watching,
        }
        print("daaa", data)
        result_data = await self._client.post(Url.watchlist_modify, payload=data)
        print(result_data)
        return WatchlistResponse(
            symbol=request.symbol, watching=result_data["watching"]
        )

    async def add(self, request: AddToWatchlistRequest) -> WatchlistResponse:
        return await self._modify_watchlist(request)

    async def remove(self, request: RemoveFromWatchlistRequest) -> WatchlistResponse:
        return await self._modify_watchlist(request)
