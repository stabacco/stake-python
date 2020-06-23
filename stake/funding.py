from datetime import datetime

from pydantic import BaseModel


class Funding(BaseModel):
    id: str
    timestamp: datetime
    orderType: str
    eventType: str
    status: str
    title: str
    amount: str
    description: str
    currencyFrom: str
    currencyTo: str
    spotRate: float
    totalFee: float
    amountFrom: float
    amountTo: float
    rate: float
    referenceNumber: str
