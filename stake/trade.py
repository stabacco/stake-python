import weakref
from typing import Union

from pydantic import BaseModel


class BuyRequest(BaseModel):
    """This is the request that needs to be passed to the trade client in order to
    buy some equity.
    """

    userId: str
    itemId: str
    itemType: str = "instrument"
    orderType: str = "limit"
    price: float
    limitPrice: float
    comments: str


class LimitBuyRequest(BaseModel):
    limitPrice: float
    quantity: float
    comments: str
    orderType: str = "limit"
    itemType: str = "instrument"


class TradesClient:
    """This client is used to buy/sell equities."""

    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def buy(self, symbol: str, request: Union[BuyRequest, LimitBuyRequest]):
        """

        Args:
            symbol: one of the symbols available in Stake for trading.
            request:

        Returns:

        """
        request = request.dict()
        request["userId"] = self._client.user.userID
        product = self._client.products.get(symbol)
        assert product
        request["itemId"] = product.encodedName
        return await self._client.post(
            self._client.url("purchaseorders/v2/quickBuy"), request
        )
