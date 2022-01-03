from datetime import datetime
from typing import List, Union

from pydantic import BaseModel, Field

from stake.common import BaseClient, camelcase
from stake.constant import Url
from stake.product import Product

__all__ = ["AddToWatchlistRequest", "RemoveFromWatchlistRequest"]


class AddToWatchlistRequest(BaseModel):
    symbol: str


class RemoveFromWatchlistRequest(BaseModel):
    symbol: str


class WatchlistResponse(BaseModel):
    symbol: str
    watching: bool


class WatchlistProduct(BaseModel):
    id: str = Field(alias="productWatchlistID")
    watched_date: datetime
    product: Product

    class Config:
        alias_generator = camelcase


class WatchlistClient(BaseClient):
    async def _modify_watchlist(
        self, request: Union[AddToWatchlistRequest, RemoveFromWatchlistRequest]
    ) -> WatchlistResponse:
        """Adds/remove to the watchlist.

        Args:
            request (Union[AddToWatchlistRequest, RemoveFromWatchlistRequest]):
                Either an add orremove request.

        Returns:
            WatchlistResponse: The result of the watchlist modification
        """
        product = await self._client.products.get(request.symbol)

        assert product
        payload = {
            "instrumentID": str(product.id),
            "userID": str(self._client.user.id),
        }
        data = await self._client.post(Url.watchlist_modify, payload=payload)

        return WatchlistResponse(symbol=request.symbol, watching=data["watching"])

    async def add(self, request: AddToWatchlistRequest) -> WatchlistResponse:
        """Adds a symbol to the watchlist.

        Args:
            request (AddToWatchlistRequest): The request containing the symbol.

        Returns:
            WatchlistResponse: The result of the watchlist modification.
        """
        return await self._modify_watchlist(request)

    async def remove(self, request: RemoveFromWatchlistRequest) -> WatchlistResponse:
        """Removes a symbol from the watchlist.

        Args:
            request (RemoveFromWatchlistRequest): The request containing the symbol

        Returns:
            WatchlistResponse: The result of the watchlist modification.
        """
        return await self._modify_watchlist(request)

    async def list(self) -> List[WatchlistProduct]:
        """Lists all the contents of your watchlist.

        Returns:
            List[WatchlistProduct]: The list of items in your watchlist.
        """
        watchlist = await self._client.get(
            Url.watchlist.format(userId=self._client.user.id)  # type: ignore
        )
        return [
            WatchlistProduct(**watched) for watched in watchlist["instrumentsWatchList"]
        ]
