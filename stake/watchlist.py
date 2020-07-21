import weakref

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

    # async def list(self) -> List[Order]:
    #     data = await self._client.get(Url.orders)
    #     return [Order(**d) for d in data]

    async def add(self, request: AddToWatchlistRequest) -> WatchlistResponse:
        product = await self._client.products.get(request.symbol)
        assert product
        print(product.id)
        data = {"instrumentID": product.id, "userID": self._client.user.userId}
        result_data = await self._client.post(Url.watchlist_modify, payload=data)
        return WatchlistResponse(
            symbol=request.symbol, watching=result_data["watching"]
        )

    async def remove(self, request: RemoveFromWatchlistRequest) -> WatchlistResponse:
        product = await self._client.products.get(request.symbol)
        assert product
        data = {"instrumentID": product.id, "userID": self._client.user.userId}
        result_data = await self._client.post(Url.watchlist_modify, payload=data)
        return WatchlistResponse(
            symbol=request.symbol, watching=result_data["watching"]
        )
