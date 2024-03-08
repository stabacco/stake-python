from datetime import date
from typing import Optional

import pydantic
from pydantic import ConfigDict

from stake.common import BaseClient, camelcase

__all__ = ["MarketStatus"]


class Status(pydantic.BaseModel):
    current: Optional[str] = None


class MarketStatus(pydantic.BaseModel):
    last_trading_date: Optional[date] = None
    status: Status
    model_config = ConfigDict(alias_generator=camelcase)


class MarketClient(BaseClient):
    """Retrieves informations about the current status of the market."""

    async def get(self) -> MarketStatus:
        data = await self._client.get(self._client.exchange.market_status)
        return MarketStatus(**data)

    async def is_open(self) -> bool:
        status = await self.get()
        return status.status.current == "open"
