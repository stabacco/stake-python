from datetime import datetime
from typing import Optional

import pydantic
from pydantic import ConfigDict

from stake.common import BaseClient, camelcase

__all__ = ["MarketStatus"]


class Status(pydantic.BaseModel):
    current: str


class MarketStatus(pydantic.BaseModel):
    last_trading_date: Optional[datetime] = None
    status: Status
    model_config = ConfigDict(alias_generator=camelcase)


class MarketClient(BaseClient):
    """Retrieves informations about the current status of the market."""

    async def get(self) -> MarketStatus:
        data = await self._client.get(self._client.exchange.market_status)
        return MarketStatus(
            last_trading_date=data[0]["lastTradedTimestamp"],
            status=Status(current=data[0]["marketStatus"]),
        )

    async def is_open(self) -> bool:
        status = await self.get()
        return status.status.current == "open"
