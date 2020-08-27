"""Checks the market status"""

import weakref
from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from stake.common import camelcase
from stake.constant import Url
import logging

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


class MarketClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def get(self) -> MarketStatus:
        data = await self._client.get(Url.market_status)
        return MarketStatus(**data["response"])

    async def is_open(self) -> bool:
        status = await self.get()
        return status.status.current == "open"
