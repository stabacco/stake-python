import weakref
from datetime import datetime
from typing import List

from pydantic import BaseModel

from stake.constant import Url


class Order(BaseModel):
    orderNo: str
    orderID: str
    orderCashAmt: float
    price: float
    stopPrice: float
    side: str
    orderType: int
    cumQty: float
    limitPrice: float
    createdWhen: datetime
    orderStatus: int
    orderQty: float
    instrumentID: str
    imageUrl: str
    instrumentSymbol: str
    instrumentName: str
    description: str
    encodedName: str


class OrdersClient:
    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def list(self) -> List[Order]:
        data = await self._client.get(Url.orders)
        return [Order(**d) for d in data]