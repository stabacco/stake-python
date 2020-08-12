from stake.common import camelcase
import weakref
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import List

from pydantic import BaseModel
from pydantic import Field

from stake.constant import Url

__all__ = ["FundingRequest"]


class FundingRequest(BaseModel):
    """Request to be issued to the fundings endpoint."""

    end_date: date = Field(default_factory=date.today)
    start_date: date = Field(
        default_factory=lambda *_: date.today() - timedelta(days=365)
    )


class Funding(BaseModel):
    id: str
    timestamp: datetime
    order_type: str
    event_type: str
    status: str
    title: str
    amount: str
    description: str
    currency_from: str
    currency_to: str
    spot_rate: float
    total_fee: float
    amount_from: float
    amount_to: float
    rate: float
    reference_number: str

    class Config:
        alias_generator = camelcase


class FundingsClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def list(self, request: FundingRequest) -> List[Funding]:
        payload = {
            "endDate": request.end_date.strftime("%d/%m/%Y"),
            "startDate": request.start_date.strftime("%d/%m/%Y"),
        }
        data = await self._client.post(Url.fundings, payload=payload)

        return [Funding(**d) for d in data]

    async def in_flight(self) -> dict:
        """Returns the funds currently in flight."""
        return await self._client.get(Url.fund_details)["fundsInFlight"]
