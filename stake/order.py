from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from stake.common import BaseClient, SideEnum, camelcase

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
    stop_price: float
    side: SideEnum
    order_type: OrderTypeEnum
    cum_qty: str
    limit_price: float
    created_when: datetime
    order_status: int
    order_qty: float
    description: str
    instrument_id: str = Field(alias="instrumentID")
    image_url: str
    instrument_symbol: str
    instrument_name: str
    encoded_name: str
    model_config = ConfigDict(alias_generator=camelcase)


class Brokerage(BaseModel):
    brokerage_fee: Optional[float] = None
    fixed_fee: Optional[float] = None
    variable_fee_percentage: Optional[float] = None
    variable_limit: Optional[int] = None
    model_config = ConfigDict(alias_generator=camelcase)


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
        data = await self._client.get(self._client.exchange.orders)
        return [Order(**d) for d in data]

    async def cancel(self, order: Union[Order, CancelOrderRequest]) -> bool:
        """Cancels a pending order.

        Args:
            order (Union[Order, CancelOrderRequest])): an existing order or its ID.

        Returns:
            bool: True if the deletion was succesful.
        """
        await self._client.delete(
            self._client.exchange.cancel_order.format(orderId=order.order_id)
        )
        return True

    async def brokerage(self, order_amount: float) -> Brokerage:
        """Retrieve the brokerage for an order.

        Args:
            order_amount (float): the per unit purchase price
        Returns:
            Brokerage: the brokerage information
        """

        data = await self._client.get(
            self._client.exchange.brokerage.format(orderAmount=order_amount)
        )
        return Brokerage(**data)
