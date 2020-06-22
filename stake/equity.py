from typing import List
from typing import Optional

import attr
from pydantic import BaseModel


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

    @classmethod
    def from_data(cls, **data):
        filtered_data = {
            key: value for key, value in data.items() if key in cls.__annotations__
        }
        return cls(**filtered_data)


class EquityPositions(BaseModel):
    equityPositions: List[EquityPosition]
    equityValue: float
