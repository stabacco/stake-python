from datetime import datetime
from enum import IntEnum
from typing import List, Union

from pydantic import BaseModel, Field
from pydantic.types import UUID

from stake.common import BaseClient, SideEnum, camelcase
from stake.constant import Url

__all__ = ["OrderTypeEnum", "CancelOrderRequest"]


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


class CancelOrderRequest(BaseModel):
    order_id: str


class OrdersClient(BaseClient):
    """This client is in charge of dealing with your pending orders.

    These are the orders limit/stop etc.. that have not been traded yet.
    """

    async def list(self) -> List[Order]:
        """Lists all your pending orders.

        Returns:
            List[Order]: The list of pending orders.
        """
        data = await self._client.get(Url.orders)
        return [Order(**d) for d in data]

    async def cancel(self, order: Union[Order, CancelOrderRequest]) -> bool:
        """Cancels a pending order.

        Args:
            order (Union[Order, CancelOrderRequest])): an order or an order_id

        Returns:
            bool: True if the deletion was succesful.
        """
        return await self._client.delete(
            Url.cancel_order.format(orderId=order.order_id)
        )
