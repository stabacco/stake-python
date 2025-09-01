import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from stake.common import BaseClient, camelcase
from stake.product import Instrument, Product

__all__ = [
    "AddToWatchlistRequest",
    "RemoveFromWatchlistRequest",
    "CreateWatchlistRequest",
    "UpdateWatchlistRequest",
    "GetWatchlistRequest",
    "DeleteWatchlistRequest",
]


class AddToWatchlistRequest(BaseModel):
    symbol: str


class RemoveFromWatchlistRequest(BaseModel):
    symbol: str


class GetWatchlistRequest(BaseModel):
    """Retrieves a watchlist by id."""

    id: uuid.UUID


class DeleteWatchlistRequest(BaseModel):
    """Deletes a watchlist by id."""

    id: uuid.UUID


class CreateWatchlistRequest(BaseModel):
    """This is used to create a new watchlist."""

    name: str
    tickers: List[str] | None = None


class UpdateWatchlistRequest(BaseModel):
    """The request used to update a watchlist."""

    id: uuid.UUID
    tickers: List[str]


class WatchlistResponse(BaseModel):
    symbol: str
    watching: bool


class Watchlist(BaseModel):
    watchlist_id: uuid.UUID
    name: Optional[str] = None
    count: Optional[int] = None
    time_created: Optional[datetime] = None
    instruments: Optional[List[Instrument]] = None
    model_config = ConfigDict(alias_generator=camelcase)


class WatchlistProduct(BaseModel):
    id: str = Field(alias="productWatchlistID")
    watched_date: datetime
    product: Product
    model_config = ConfigDict(alias_generator=camelcase)


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
        data = await self._client.post(
            self._client.exchange.watchlist_modify, payload=payload
        )

        return WatchlistResponse(symbol=request.symbol, watching=data["watching"])

    async def watchlist(self, request: GetWatchlistRequest) -> Watchlist:
        """Retrieves a watchlist by id.

        Will throw an aiohttp.client_exceptions.ClientResponseError if
        the id is not found.
        """
        response = await self._client.get(
            self._client.exchange.read_watchlist.format(watchlist_id=request.id)
        )
        return Watchlist(**response)

    async def list_watchlists(self) -> List[Watchlist]:
        """Lists all your available watchlists.

        Returns:
            List[Watchlist]: The list of your available watchlists
        """

        response = await self._client.get(self._client.exchange.watchlists)
        return [Watchlist(**watchlist) for watchlist in response["watchlists"]]

    async def create_watchlist(
        self, request: CreateWatchlistRequest
    ) -> Optional[Watchlist]:

        name = request.name

        existing_watchlists = await self.list_watchlists()
        if name in [watchlist.name for watchlist in existing_watchlists]:
            raise ValueError(f"A watchlist named {name} already exists.")

        response = await self._client.post(
            self._client.exchange.create_watchlist, payload=request.model_dump()
        )
        watchlist_id = response.get("newWatchlistId", None)
        assert watchlist_id, "Could not get a new watchlist"

        if request.tickers:
            return await self.add_to_watchlist(
                request=UpdateWatchlistRequest(id=watchlist_id, tickers=request.tickers)
            )
        return await self.watchlist(request=GetWatchlistRequest(id=watchlist_id))

    async def add_to_watchlist(self, request: UpdateWatchlistRequest) -> Watchlist:
        """Updates a watchlist by adding symbols to it."""

        existing_watchlist = await self.watchlist(request=request)
        existing_tickers = [
            instrument.symbol for instrument in existing_watchlist.instruments or []
        ]
        # filter out the ones that are already there, otherwise an exception will happen.
        request.tickers = [
            ticker for ticker in request.tickers if ticker not in existing_tickers
        ]

        if not request.tickers:
            return existing_watchlist

        response = await self._client.post(
            self._client.exchange.update_watchlist.format(watchlist_id=request.id),
            payload=request.model_dump(exclude={"id"}),
        )
        return Watchlist(**response)

    async def remove_from_watchlist(self, request: UpdateWatchlistRequest) -> Watchlist:
        existing_watchlist = await self.watchlist(request=request)
        existing_tickers = [
            instrument.symbol for instrument in existing_watchlist.instruments or []
        ]

        # just consider the ones that are in the watchlist already.
        request.tickers = [
            ticker for ticker in request.tickers if ticker in existing_tickers
        ]

        if not request.tickers:
            return existing_watchlist

        response = await self._client.delete(
            self._client.exchange.update_watchlist.format(watchlist_id=request.id),
            payload=request.model_dump(exclude={"id"}),
        )

        return Watchlist(**response)

    async def delete_watchlist(
        self, request: Union[Watchlist, DeleteWatchlistRequest]
    ) -> bool:
        response = await self._client.delete(
            self._client.exchange.read_watchlist.format(watchlist_id=request.id)
        )
        # the response will contains all the remaining watchlists
        return request.id not in [w["watchlistId"] for w in response]
