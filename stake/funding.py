import weakref
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import List

from pydantic import BaseModel
from pydantic import Field

from stake.constant import Url

__all__ = ["FundingRequest", "Funding"]


class FundingRequest(BaseModel):
    """Request to be issued to the fundings endpoint."""

    endDate: date = Field(default_factory=date.today)
    startDate: date = Field(
        default_factory=lambda *_: date.today() - timedelta(days=365)
    )


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


class FundingsClient:
    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def list(self, request: FundingRequest) -> List[Funding]:
        payload = {
            "endDate": request.endDate.strftime("%d/%m/%Y"),
            "startDate": request.startDate.strftime("%d/%m/%Y"),
        }
        data = await self._client._post(Url.fundings, payload=payload)

        return [Funding(**d) for d in data]

    async def in_flight(self) -> dict:
        """Returns the funds currently in flight."""
        return await self._client._get(Url.fund_details)["fundsInFlight"]
