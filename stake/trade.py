import asyncio
import weakref
from datetime import datetime
from enum import Enum
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import root_validator
from pydantic import ValidationError
from pydantic import validator


class OrderType(str, Enum):
    MARKET: str = "market"
    LIMIT: str = "limit"
    STOP: str = "stop"


class MarketBuyRequest(BaseModel):
    """This is the request that needs to be passed to the trade client in order to
    buy some equity.
    """

    # AAPL, MSFT, TSLA etc...
    symbol: str
    # needed for "market" & stop buy
    price: float
    # comments to be added to the trade
    comments: Optional[str]

    orderType: OrderType = OrderType.MARKET
    itemType: str = "instrument"


class LimitBuyRequest(BaseModel):
    symbol: str
    limitPrice: float
    quantity: int
    comments: Optional[str]
    orderType: OrderType = OrderType.LIMIT
    itemType: str = "instrument"


class StopBuyRequest(BaseModel):
    symbol: str
    amountCash: float
    price: float  # must be higher than the current one
    comments: Optional[str]
    itemType: str = "instrument"
    orderType: OrderType = OrderType.STOP

    @validator("amountCash")
    def at_least_10(cls, v: float) -> float:

        if v < 10.0:
            raise ValueError("'amountCash' must be at least '10$'.")

        return v


class SellRequest(BaseModel):
    symbol: str
    itemType: str = "instrument"
    orderType: OrderType
    quantity: float
    stopPrice: Optional[float]
    limitPrice: Optional[float]
    comments: Optional[str]


class TradeResponse(BaseModel):
    """ The response from a request to buy/sell."""

    id: str
    itemId: str
    name: str
    category: str
    quantity: float
    amountCash: float
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


class PendingOrder(BaseModel):
    """Orders listed in the pending orders page"""

    orderNo: str
    orderID: str
    orderCashAmt: float
    symbol: Optional[str]
    price: float
    stopPrice: float
    side: str
    orderType: int
    cumQty: float
    limitPrice: float
    createdWhen: datetime
    orderStatus: int
    orderQty: int
    instrumentID: str
    imageUrl: str
    instrumentSymbol: str
    instrumentName: str
    description: str
    encodedName: str


class TradesClient:
    """This client is used to buy/sell equities."""

    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def _trade(
        self,
        url: str,
        request: Union[MarketBuyRequest, LimitBuyRequest, StopBuyRequest, SellRequest],
        check_success: bool = True,
    ) -> TradeResponse:
        """ A generic function used to submit a trade, either buy or sell.

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
        request_dict["userId"] = self._client.user.userID
        request_dict["itemId"] = product.id
        data = await self._client._post(self._client._url(url), request_dict)
        trade = TradeResponse(**data[0])

        if not check_success:
            return trade

        # now check if the trade has really happened
        transactions = await self._client._get("users/accounts/transactions")
        if not transactions:
            raise RuntimeError("The trade did not succeed.")

        # wait for the transaction to be available
        for transaction in transactions:
            if transaction["orderId"] == trade.dwOrderId:
                # TODO: so baddd
                if " Buy Stop price must be >= " in transaction["updatedReason"]:
                    raise RuntimeError("The trade did not succeed.")
                return trade

    async def buy(
        self, request: Union[MarketBuyRequest, LimitBuyRequest, StopBuyRequest]
    ) -> TradeResponse:
        """

        Args:
            request: the buy request

        Returns:
            the TradeResponse object
        """
        url = self._client._url("purchaseorders/v2/quickBuy")
        return await self._trade(url, request)

    async def sell(self, request: SellRequest) -> TradeResponse:
        url = self._client._url("sellorders")
        return await self._trade(url, request)

    async def cancel(self, orderId: str) -> bool:
        """cancels a pending order.
        """
        return await self._client._delete(f"orders/cancelOrder/{orderId}")

    async def list(self) -> List[PendingOrder]:
        """List all the pending orders"""

        orders = await self._client._get("users/accounts/orders")
        return [PendingOrder(**order) for order in orders]
