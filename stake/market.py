"""Checks the market status."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from stake.common import BaseClient, camelcase

__all__ = ["MarketStatus"]


class Status(BaseModel):
    change_at: Optional[str] = Field(None, alias="change_at")
    next: Optional[str] = None
    current: str
    model_config = ConfigDict(alias_generator=camelcase)


class MarketStatus(BaseModel):
    status: Status
    model_config = ConfigDict(alias_generator=camelcase)


class MarketClient(BaseClient):
    async def get(self) -> MarketStatus:
        data = await self._client.get(self._client.exchange.market_status)
        return MarketStatus(**data["response"])

    async def is_open(self) -> bool:
        status = await self.get()
        return status.status.current == "open"
