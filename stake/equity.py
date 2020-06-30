import weakref
from typing import List
from typing import Optional

from pydantic import BaseModel

from stake.constant import Url


class EquityPosition(BaseModel):
    availableForTradingQty: float
    avgPrice: float
    category: str
    costBasis: float
    dailyReturnValue: float
    encodedName: str
    instrumentID: str
    lastTrade: float
    marketValue: float
    mktPrice: float
    name: str
    openQty: float
    period: str
    priorClose: float
    side: str
    symbol: str
    unrealizedDayPL: float
    unrealizedDayPLPercent: float
    unrealizedPL: float
    urlImage: str
    yearlyReturnPercentage: float
    yearlyReturnValue: float
    askPrice: Optional[float] = None
    bidPrice: Optional[float] = None
    returnOnStock: Optional[float] = None


class EquityPositions(BaseModel):
    """Represents the user's portforlio, with the list of the currently
    available equities."""

    equityPositions: List[EquityPosition]
    equityValue: float


class EquitiesClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def list(self) -> EquityPositions:
        data = await self._client.get(Url.equity_positions)
        return EquityPositions(**data)
