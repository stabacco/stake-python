import weakref
from datetime import datetime
from typing import List
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from stake.common import camelcase
from stake.constant import Url
from stake.product import Product

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


class WatchlistProduct(BaseModel):
    id: str = Field(alias="productWatchlistID")
    watched_date: datetime
    product: Product

    class Config:
        alias_generator = camelcase


class WatchlistClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def _modify_watchlist(
        self, request: Union[AddToWatchlistRequest, RemoveFromWatchlistRequest]
    ) -> WatchlistResponse:
        product = await self._client.products.get(request.symbol)
        assert product
        data = {
            "instrumentID": product.id,
            "userID": self._client.user.id,
            "watching": request.watching,
        }
        result_data = await self._client.post(Url.watchlist_modify, payload=data)
        return WatchlistResponse(
            symbol=request.symbol, watching=result_data["watching"]
        )

    async def add(self, request: AddToWatchlistRequest) -> WatchlistResponse:
        return await self._modify_watchlist(request)

    async def remove(self, request: RemoveFromWatchlistRequest) -> WatchlistResponse:
        return await self._modify_watchlist(request)

    async def list(self) -> List[WatchlistProduct]:
        watchlist = await self._client.get(
            Url.watchlist.format(userId=self._client.user.id)
        )
        return [
            WatchlistProduct(**watched) for watched in watchlist["instrumentsWatchList"]
        ]
