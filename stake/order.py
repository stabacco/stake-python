from datetime import datetime
from enum import IntEnum
from typing import List

from pydantic import BaseModel, Field
from pydantic.types import UUID

from stake.common import BaseClient, SideEnum, camelcase
from stake.constant import Url

__all__ = ["OrderTypeEnum"]


class OrderTypeEnum(IntEnum):
    MARKET = 1
    LIMIT = 2
    STOP = 3


class Order(BaseModel):
    order_no: str
    order_id: str = Field(alias="orderID")
    order_cash_amt: int
    symbol: str
    price: int
    stop_price: int
    side: SideEnum
    order_type: OrderTypeEnum
    cum_qty: str
    limit_price: int
    created_when: datetime
    order_status: int
    order_qty: float
    description: str
    instrument_id: UUID = Field(alias="instrumentID")
    image_url: str
    instrument_symbol: str
    instrument_name: str
    encoded_name: str

    class Config:
        alias_generator = camelcase


class OrderSearchRequest(BaseModel):
    symbol: str
    orderType: OrderTypeEnum
    side: SideEnum


class OrdersClient(BaseClient):
    async def list(self) -> List[Order]:
        data = await self._client.get(Url.orders)
        return [Order(**d) for d in data]

    async def cancel(self, order: Order) -> bool:
        """Cancels a pending order."""
        return await self._client.delete(
            Url.cancel_order.format(orderId=order.order_id)
        )

    # async def search(self, request: OrderSearchRequest) -> List[Order]:
    #     for field in iter(request):
    #         print(field)
