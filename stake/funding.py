"""Your current fundings."""
import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from stake.common import BaseClient, camelcase
from stake.constant import Url
from stake.transaction import (
    TransactionHistoryElement,
    TransactionHistoryType,
    TransactionRecordRequest,
)


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


class FundsInFlight(BaseModel):
    type: str
    insert_date_time: str
    estimated_arrival_time: str
    estimated_arrival_time_us: str = Field(alias="estimatedArrivalTimeUS")
    transaction_type: str
    to_amount: float
    from_amount: float

    class Config:
        alias_generator = camelcase


class FundingsClient(BaseClient):
    async def list(
        self, request: TransactionRecordRequest
    ) -> List[TransactionHistoryElement]:
        payload = json.loads(request.json(by_alias=True))
        data = await self._client.post(Url.fundings, payload=payload)
        return [
            TransactionHistoryElement(**d)
            for d in data
            if d["referenceType"] == TransactionHistoryType.FUNDING.value
        ]

    async def in_flight(self) -> List[FundsInFlight]:
        """Returns the funds currently in flight."""
        data = await self._client.get(Url.fund_details)
        data = data.get("fundsInFlight")
        if not data:
            return []
        return [FundsInFlight(**d) for d in data]

    async def cash_available(self) -> CashAvailable:
        data = await self._client.get(Url.cash_available)
        return CashAvailable(**data)
