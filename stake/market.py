import weakref

from pydantic import BaseModel

from stake.constant import Url


class MarketStatus(BaseModel):
    current: str
    change_at: str


class MarketClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def get(self) -> MarketStatus:
        data = await self._client.get(Url.market_status)
        return MarketStatus(**data["response"]["status"])

    async def is_open(self) -> bool:
        status = await self.get()
        return status.current == "open"
