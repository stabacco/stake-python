import weakref
from typing import Dict
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
    equityPositions: List[EquityPosition]
    equityValue: float


class EquitiesClient:
    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def list(self) -> Dict[EquityPosition]:
        data = await self._client._get(Url.equity_positions)
        return {d["symbol"]: EquityPosition(**d) for d in data["equityPositions"]}
