"""Checks the market status."""
from datetime import datetime

from pydantic import BaseModel, Field

from stake.common import BaseClient, camelcase
from stake.constant import Url

__all__ = ["MarketStatus"]


class Status(BaseModel):
    change_at: str = Field(alias="change_at")
    next: str
    current: str

    class Config:
        alias_generator = camelcase


class MarketStatus(BaseModel):
    message: str
    unixtime: datetime
    error: str
    status: Status
    elapsedtime: int
    date: datetime
    version_number: str

    class Config:
        alias_generator = camelcase


class MarketClient(BaseClient):
    async def get(self) -> MarketStatus:
        data = await self._client.get(Url.market_status)
        return MarketStatus(**data["response"])

    async def is_open(self) -> bool:
        status = await self.get()
        return status.status.current == "open"
