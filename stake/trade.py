import re
import weakref
from datetime import datetime
from enum import Enum
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import validator

from stake.constant import Url

failed_transaction_regex = re.compile(r"^[0-9]{4}")

__all__ = [
    "LimitBuyRequest",
    "LimitSellRequest",
    "MarketBuyRequest",
    "MarketSellRequest",
    "StopBuyRequest",
    "StopSellRequest",
]


class TradeType(str, Enum):
    """The type of trade the user is requesting."""

    MARKET: str = "market"
    LIMIT: str = "limit"
    STOP: str = "stop"


class MarketBuyRequest(BaseModel):
    """This is the request that needs to be passed to the trade client in order
    to buy some equity."""

    # AAPL, MSFT, TSLA etc...
    symbol: str
    amountCash: float
    comments: Optional[str]

    itemType: str = "instrument"
    orderType: TradeType = TradeType.MARKET


class LimitBuyRequest(BaseModel):
    symbol: str
    limitPrice: float
    quantity: int
    comments: Optional[str]

    itemType: str = "instrument"
    orderType: TradeType = TradeType.LIMIT


class StopBuyRequest(BaseModel):
    symbol: str
    amountCash: float
    price: float  # must be higher than the current one
    comments: Optional[str]

    itemType: str = "instrument"
    orderType: TradeType = TradeType.STOP

    @validator("amountCash")
    def at_least_10(cls, v: float) -> float:  # noqa

        if v < 10.0:
            raise ValueError("'amountCash' must be at least '10$'.")

        return v


class LimitSellRequest(BaseModel):
    symbol: str
    limitPrice: float
    quantity: int
    comments: Optional[str]

    itemType: str = "instrument"
    orderType: TradeType = TradeType.LIMIT


class StopSellRequest(BaseModel):
    symbol: str
    quantity: float
    stopPrice: Optional[float]
    limitPrice: Optional[float]
    comments: Optional[str]

    itemType: str = "instrument"
    orderType: TradeType


class MarketSellRequest(BaseModel):
    """Sell at marked price."""

    symbol: str
    quantity: float
    comments: Optional[str]

    itemType: str = "instrument"
    orderType: TradeType = TradeType.MARKET


class TradeResponse(BaseModel):
    """The response from a request to buy/sell."""

    id: str
    itemId: str
    name: str
    category: str
    quantity: Optional[float]
    amountCash: Optional[float]
    limitPrice: Optional[float]
    stopPrice: Optional[float]
    effectivePrice: Optional[float]
    commission: Optional[float]
    description: Optional[str]
    insertedDate: datetime
    updatedDate: datetime
    side: str
    status: Optional[int]
    orderRejectReason: Optional[str]
    encodedName: str
    imageURL: str
    symbol: str
    dwOrderId: str


class TradesClient:
    """This client is used to buy/sell equities."""

    def __init__(self, client):
        """
        Args:
            client: an instance of a _StakeClient
        """
        self._client = weakref.proxy(client)

    async def _trade(
        self,
        url: str,
        request: Union[
            MarketBuyRequest,
            LimitBuyRequest,
            StopBuyRequest,
            LimitSellRequest,
            StopSellRequest,
            MarketSellRequest,
        ],
        check_success: bool = True,
    ) -> TradeResponse:
        """A generic function used to submit a trade, either buy or sell.

        Args:
            url: the url for buy/sell
            request:
            check_success: if true, an extra check will be performed to see if
            the transaction really occurred. This should not be needed, since it should
            be possible to inspect the TradeResponse for errors, but it does not look
            like they are recorded anywhere.

        Returns:
            the TradeResponse

        Raises:
            RuntimeError
        """
        product = await self._client.products.get(request.symbol)
        assert product
        request_dict = request.dict()
        request_dict["userId"] = self._client.user.userId
        request_dict["itemId"] = product.id
        data = await self._client.post(self._client.httpClient.url(url), request_dict)
        trade = TradeResponse(**data[0])

        if not check_success:
            return trade

        await self._check_trade_against_transactions(trade)

        return trade

    async def _check_trade_against_transactions(self, trade: TradeResponse) -> None:
        """We check the status of the trade by trying to find the matching
        transaction and inspecting its properties. This should not be needed
        but there is nothing i can see in the trading response that would help
        figuring out if the trade request was successful or not.

        Args:
            trade: the responded trade

        Returns:
            Nothing

        Raises:
            RuntimeError if the trade was not successful.
        """

        transactions = await self._client.get("users/accounts/transactions")

        if not transactions:
            raise RuntimeError(
                "The trade did not succeed (Reason: no transaction found)."
            )

        # wait for the transaction to be available
        for transaction in transactions:
            if transaction["orderId"] == trade.dwOrderId and re.search(
                failed_transaction_regex, transaction["updatedReason"]
            ):
                raise RuntimeError(
                    f"The trade did not succeed (Reason: {transaction['updatedReason']}"
                )

    async def buy(
        self, request: Union[MarketBuyRequest, LimitBuyRequest, StopBuyRequest]
    ) -> TradeResponse:
        """

        Args:
            request: the buy request

        Returns:
            the TradeResponse object
        """
        url = self._client.httpClient.url(Url.quick_buy)
        return await self._trade(url, request)

    async def sell(self, request: MarketSellRequest) -> TradeResponse:
        url = self._client.httpClient.url(Url.sell_orders)
        return await self._trade(url, request)
