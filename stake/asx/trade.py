from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator, validate_call

from stake.asx.common import TradeType
from stake.asx.order import Order
from stake.common import BaseClient, camelcase

__all__ = [
    "LimitBuyRequest",
    "LimitSellRequest",
    "MarketBuyRequest",
    "MarketSellRequest",
]


class ExpiryDate(str, Enum):
    """The expiry date for the trade."""

    IN_ONE_DAY = "GFD"
    IN_THIRTY_DAYS = "GTC"


class GenericTradeRequest(BaseModel):
    """Issues a limit buy request."""

    symbol: Optional[str] = Field(
        None,
        alias="instrumentCode",
        description="The symbol for the ",
    )
    instrument_code: Optional[str] = None

    units: int
    validity: ExpiryDate = ExpiryDate.IN_THIRTY_DAYS
    validity_date: Optional[datetime] = None
    model_config = ConfigDict(alias_generator=camelcase, populate_by_name=True)

    @model_validator(mode="after")
    @classmethod
    def symbol_or_instrument_type(
        cls, value: "GenericTradeRequest"
    ) -> "GenericTradeRequest":
        if value.symbol is None and value.instrument_code is None:
            raise ValueError("Either specify symbol or instrument_code")
        return value


class LimitBuyRequest(GenericTradeRequest):
    side: str = "BUY"
    type: TradeType = TradeType.LIMIT
    price: float


class LimitSellRequest(GenericTradeRequest):
    side: str = "SELL"
    type: TradeType = TradeType.LIMIT
    price: float


class MarketBuyRequest(GenericTradeRequest):
    side: str = "BUY"
    type: TradeType = TradeType.MARKET
    price: Optional[float] = None


class MarketSellRequest(GenericTradeRequest):
    side: str = "SELL"
    type: TradeType = TradeType.MARKET
    price: Optional[float] = None


class TradesClient(BaseClient):
    """This client is used to buy/sell equities."""

    @validate_call
    async def _trade(
        self,
        url: str,
        request: Union[
            MarketBuyRequest,
            LimitBuyRequest,
            LimitSellRequest,
            MarketSellRequest,
        ],
    ) -> Order:
        """A generic function used to submit a trade, either buy or sell.

        Args:
            url: the url for buy/sell
            request:the trade request
        Returns:
            the Order
        """
        if not request.instrument_code and request.symbol:
            # in this case we need to get the instrument name from the symbol
            instrument_id = await self._instrument_id_from_symbol(request.symbol)
            request.instrument_code = instrument_id

        data = await self._client.post(
            url, payload=request.model_dump(by_alias=True, exclude={"symbol"})
        )

        return Order(**data["order"])

    async def _instrument_id_from_symbol(self, symbol: str) -> str:
        """Returns the instrument_id from an associated product."""
        url = self._client.exchange.instrument_from_symbol.format(symbol=symbol)
        data = await self._client.post(url, payload={})
        return data["instrumentId"]

    async def buy(self, request: Union[MarketBuyRequest, LimitBuyRequest]) -> Order:
        """Creates an order to buy equities.

        Args:
            request: the buy request

        Returns:
            the Order object
        """
        # if the price has not been set(in the case of a market order),
        # we get the current ask price for that symbol. This seems to
        # be what the app is doing, the price value cannot be left null.
        if request.price is None:
            product = await self._client.products.get(request.symbol)
            assert product
            assert product.ask
            request.price = product.ask

        return await self._trade(self._client.exchange.orders, request)

    async def sell(self, request: Union[MarketSellRequest, LimitSellRequest]) -> Order:
        """Creates an order to sell equities.

        Args:
            request: the sell request

        Returns:
            the Order object
        """
        # if the price has not been set, we get the current bid price for that symbol.
        if request.price is None:
            product = await self._client.products.get(request.symbol)
            assert product
            assert product.bid
            request.price = product.bid

        return await self._trade(self._client.exchange.orders, request)
