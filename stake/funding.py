"""Your current fundings."""
import asyncio
import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from stake.common import BaseClient, camelcase
from stake.transaction import TransactionHistoryType, TransactionRecordRequest


class Funding(BaseModel):
    iof: Optional[str] = None
    vet: Optional[str] = None
    bsb: Optional[str] = None
    account_number: Optional[str] = None
    insert_date: Optional[datetime] = None
    channel: Optional[str] = None
    amount_to: Optional[float] = None
    amount_from: Optional[float] = None
    status: Optional[str] = None
    speed: Optional[str] = None
    fx_fee: Optional[float] = None
    express_fee: Optional[int] = None
    total_fee: Optional[float] = None
    spot_rate: Optional[float] = None
    reference: Optional[str] = None
    w8_fee: Optional[int] = None
    currency_from: Optional[str] = None
    currency_to: Optional[str] = None

    class Config:
        alias_generator = camelcase


class CashSettlement(BaseModel):
    utc_time: datetime
    cash: float

    class Config:
        alias_generator = camelcase


class CashAvailable(BaseModel):
    buying_power: Optional[float] = None
    cash_available_for_transfer: Optional[float] = None
    cash_available_for_withdrawal_hold: Optional[float] = None
    cash_available_for_withdrawal: Optional[float] = None
    clearing_cash: Optional[float] = None
    pending_buys: Optional[int] = None
    pending_withdrawals: Optional[int] = None
    settled_cash: Optional[float] = None
    settlement_hold: Optional[float] = None
    trade_settlement: Optional[float] = None

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
    async def list(self, request: TransactionRecordRequest) -> List[Funding]:
        payload = json.loads(request.json(by_alias=True))
        # looks like there is no way to pass filter the transactions here
        data = await self._client.post(
            self._client.exchange.transaction_history, payload=payload
        )

        funding_transactions = [
            d
            for d in data
            if d["referenceType"] == TransactionHistoryType.FUNDING.value
        ]

        details = await asyncio.gather(
            *[
                self._client.get(
                    self._client.exchange.transaction_details.format(
                        reference=funding_transaction["reference"],
                        reference_type=funding_transaction["referenceType"],
                    ),
                )
                for funding_transaction in funding_transactions
            ]
        )
        return [Funding(**d) for d in details]

    async def in_flight(self) -> List[FundsInFlight]:
        """Returns the funds currently in flight."""
        data = await self._client.get(self._client.exchange.fund_details)
        data = data.get("fundsInFlight")
        return [FundsInFlight(**d) for d in data] if data else []

    async def cash_available(self) -> CashAvailable:
        data = await self._client.get(self._client.exchange.cash_available)
        return CashAvailable(**data)
