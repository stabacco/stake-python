from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from stake.asx.common import TradeType
from stake.asx.transaction import Side
from stake.common import BaseClient, camelcase

__all__ = ["CancelOrderRequest"]


class Order(BaseModel):
    average_price: Optional[float] = None
    broker: Optional[str] = None
    completed_timestamp: Optional[datetime] = None
    estimated_brokerage: Optional[float] = None
    estimated_exchange_fees: Optional[float] = None
    expires_at: Optional[datetime] = None
    filled_units: Optional[float] = None
    instrument_code: str
    instrument_id: Optional[str] = None
    limit_price: Optional[float] = None
    order_completion_type: Optional[str] = None
    order_id: UUID = Field(alias="id")
    order_status: Optional[str] = None
    placed_timestamp: datetime
    side: Side
    type: TradeType
    units_remaining: Optional[int] = None
    validity_date: Optional[datetime] = None
    validity: Optional[str] = None

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
        data = await self._client.get(self._client.exchange.orders)
        return [Order(**d) for d in data]

    async def cancel(self, order: Union[Order, CancelOrderRequest]) -> bool:
        """Cancels a pending order.

        Args:
            order (Union[Order, CancelOrderRequest])): an existing order or its ID.

        Returns:
            bool: True if the deletion was succesful.
        """
        await self._client.post(
            self._client.exchange.cancel_order.format(orderId=order.order_id),
            payload={},
        )
        return True
