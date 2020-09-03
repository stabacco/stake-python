"""Your current fundings."""
from datetime import date, datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from stake.common import BaseClient, camelcase
from stake.constant import Url

__all__ = ["FundingRequest"]


class FundingRequest(BaseModel):
    """Request to be issued to the fundings endpoint."""

    end_date: date = Field(default_factory=date.today)
    start_date: date = Field(
        default_factory=lambda *_: date.today() - timedelta(days=365)
    )


class Funding(BaseModel):
    id: UUID4
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


class CashSettlement(BaseModel):
    utc_time: datetime
    cash: float

    class Config:
        alias_generator = camelcase


class CashAvailable(BaseModel):
    cash_available_for_withdrawal: float
    cash_available_for_trade: float
    cash_balance: float
    reserved_cash: float
    dw_cash_available_for_withdrawal: float
    pending_orders_amount: float
    pending_withdrawals: float
    card_hold_amount: float
    pending_poli_amount: float
    cash_settlement: List[Optional[CashSettlement]]

    class Config:
        alias_generator = camelcase


class FundingsClient(BaseClient):
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

    async def cash_available(self) -> CashAvailable:
        data = await self._client.get(Url.cash_available)
        return CashAvailable(**data)
