import weakref
from typing import Union, Optional

from pydantic import BaseModel
from datetime import datetime


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
    quantity: int
    comments: Optional[str]
    orderType: str = "limit"
    itemType: str = "instrument"

class BuyResponse(BaseModel):
    """ The order resulted from a request to buy."""
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

class PendingOrder:
        {
        "orderNo": "HFBE031975",
        "orderID": "HF.28af4106-88ae-402e-a687-ada4b63d24c3",
        "orderCashAmt": 0,
        "symbol": null,
        "price": 0,
        "stopPrice": 0,
        "side": "B",
        "orderType": 2,
        "cumQty": "0",
        "limitPrice": 450,
        "createdWhen": "2020-06-23 12:42:49",
        "orderStatus": 0,
        "orderQty": 1,
        "instrumentID": "1214d7f3-e709-4e06-8659-b879a543d2e1",
        "imageUrl": "https://d3an3cesqmrf1x.cloudfront.net/images/symbols/nflx.png",
        "instrumentSymbol": "NFLX",
        "instrumentName": "Netflix, Inc.",
        "description": "Limit Order: Buy at a limit of $450.00",
        "encodedName": "netflix-inc-nflx"
    },
    {
    "orderNo": "HFKH027104",
	"orderID": "HF.a34e5494-1938-4998-b708-6c679f9bf969",
	"orderCashAmt": 0.0,
	"symbol": null,
	"price": 0.0,
	"stopPrice": 230.0,
	"side": "S",
	"orderType": 3,
	"cumQty": "0",
	"limitPrice": 0.0,
	"createdWhen": "2020-06-18 12:31:19",
	"orderStatus": 0,
	"orderQty": 0.33168316,
	"instrumentID": "b8882f91-43be-4f8e-acdc-79f8041fa72b",
	"imageUrl": "https://drivewealth.imgix.net/symbols/zm.png?fit=fillmax&w=125&h=125&bg=FFFFFF",
	"instrumentSymbol": "ZM",
	"instrumentName": "Zoom Video Communications Inc",
	"description": "Stop Order: Sell if price reaches ($230.00)",
	"encodedName": "zoom-video-communications-inc-zm"
    }
    
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
        product = await self._client.products.get(symbol)
        assert product
        print(product)
        request = request.dict()
        request["userId"] = self._client.user.userID

        request["itemId"] = product.id
        data = await self._client._post(
            self._client._url("purchaseorders/v2/quickBuy"), request
        )

        return BuyResponse(**data[0])


    async def cancel(self, orderId: str)->bool:
        """cancels a pending order.
        """
        return await self._client._delete(f"orders/cancelOrder/{orderId}")
    
    
    async def list(self) -> dict:
        """List all the pending orders"""

        await self._client._get("users/accounts/orders")