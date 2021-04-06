import re
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field, validator

from stake.common import BaseClient, camelcase
from stake.constant import Url

failed_transaction_regex = re.compile(r"^[0-9]{4}")

__all__ = [
    "LimitBuyRequest",
    "LimitSellRequest",
    "MarketBuyRequest",
    "MarketSellRequest",
    "StopBuyRequest",
    "StopSellRequest",
    "TradeType",
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
    amount_cash: float
    comments: Optional[str]

    item_type: str = "instrument"
    order_type: TradeType = TradeType.MARKET

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class LimitBuyRequest(BaseModel):
    symbol: str
    limit_price: float
    quantity: int
    comments: Optional[str]

    item_type: str = "instrument"
    order_type: TradeType = TradeType.LIMIT

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class StopBuyRequest(BaseModel):
    symbol: str
    amount_cash: float
    price: float  # must be higher than the current one
    comments: Optional[str]

    item_type: str = "instrument"
    order_type: TradeType = TradeType.STOP

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True

    @validator("amount_cash")
    def at_least_10(cls, v: float) -> float:  # noqa

        if v < 10.0:
            raise ValueError("'amount_cash' must be at least '10$'.")

        return v


class LimitSellRequest(BaseModel):
    symbol: str
    limit_price: float
    quantity: int
    comments: Optional[str]

    item_type: str = "instrument"
    order_type: TradeType = TradeType.LIMIT

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class StopSellRequest(BaseModel):
    symbol: str
    quantity: float
    stop_price: float
    comments: Optional[str]

    item_type: str = "instrument"
    order_type: TradeType = TradeType.STOP

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class MarketSellRequest(BaseModel):
    """Sell at marked price."""

    symbol: str
    quantity: float
    comments: Optional[str]

    item_type: str = "instrument"
    order_type: TradeType = TradeType.MARKET

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class TradeResponse(BaseModel):
    """The response from a request to buy/sell."""

    amount_cash: Optional[float]
    category: str
    commission: Optional[float]
    description: Optional[str]
    dw_order_id: str
    effective_price: Optional[float]
    encoded_name: str
    id: str
    image_url: str = Field(alias="imageURL")
    inserted_date: datetime
    item_id: str
    limit_price: Optional[float]
    name: str
    order_reject_reason: Optional[str]
    quantity: Optional[float]
    side: str
    status: Optional[int]
    stop_price: Optional[float]
    symbol: str
    updated_date: datetime

    class Config:
        alias_generator = camelcase


class TradesClient(BaseClient):
    """This client is used to buy/sell equities."""

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
        request_dict = request.dict(by_alias=True)
        product = await self._client.products.get(request_dict.pop("symbol"))
        assert product

        request_dict["orderType"] = request_dict["orderType"].value
        request_dict["userId"] = str(self._client.user.id)
        request_dict["itemId"] = str(product.id)
        data = await self._client.post(url, request_dict)
        trade = TradeResponse(**data[0])

        if check_success:
            await self._verify_successful_trade(trade)

        return trade

    async def _verify_successful_trade(self, trade: TradeResponse) -> None:
        """We check the status of the trade by trying to find the matching
        transaction and inspecting its properties. This should not be needed
        but there is nothing i can see in the trading response that would help
        figuring out if the trade request was successful or not.

        Args:
            trade: the responded trade

        Raises:
            RuntimeError if the trade was not successful.
        """

        transactions = await self._client.get("users/accounts/transactions")

        if not transactions:
            raise RuntimeError(
                "The trade did not succeed (Reason: no transaction found)."
            )

        # wait for the transaction to be available
        for transaction in transactions["transactions"]:
            if transaction["orderId"] == trade.dw_order_id:
                if re.search(failed_transaction_regex, transaction["updatedReason"]):
                    raise RuntimeError(
                        "The trade did not succeed "
                        f"(Reason: {transaction['updatedReason']}"
                    )
                else:
                    return

        raise RuntimeError("Could not find a matching transaction.")

    async def buy(
        self, request: Union[MarketBuyRequest, LimitBuyRequest, StopBuyRequest]
    ) -> TradeResponse:
        """Creates an order to buy equities.

        Args:
            request: the buy request

        Returns:
            the TradeResponse object
        """
        return await self._trade(Url.quick_buy, request)

    async def sell(self, request: MarketSellRequest) -> TradeResponse:
        """Creates an order to sell equities.

        Args:
            request: the sell request

        Returns:
            the TradeResponse object
        """
        return await self._trade(Url.sell_orders, request)
