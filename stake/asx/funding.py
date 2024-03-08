import json
from datetime import datetime
from enum import Enum
from typing import List, Optional
from urllib.parse import urlencode

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import UUID

from stake.asx.transaction import Sort
from stake.common import BaseClient, camelcase

__all__ = ["FundingRequest", "FundingStatus"]


class Action(str, Enum):
    DEPOSIT = "DEPOSIT"
    DIVIDEND_DEPOSIT = "DIVIDEND_DEPOSIT"
    SETTLEMENT = "SETTLEMENT"
    TRANSFER = "TRANSFER"
    WITHDRAWAL = "WITHDRAWAL"
    ADJUSTMENT = "ADJUSTMENT"


class Currency(str, Enum):
    AUD = "AUD"


class FundingSide(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class FundingStatus(str, Enum):
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    PENDING = "PENDING"
    RECONCILED = "RECONCILED"


class FundingRequest(BaseModel):
    """Example call:

    t = FundingRequest(
        statuses=[FundingStatus.RECONCILED, FundingStatus.PENDING],
        actions=[Action.DIVIDEND_DEPOSIT],
        sort=[Sort(attribute='insertedAt', direction='asc')])
    """

    statuses: Optional[List[FundingStatus]] = Field(
        [FundingStatus.RECONCILED], description="Used to filter the results."
    )
    sort: Optional[List[Sort]] = Field(
        None, description="Use this to sort the results."
    )
    actions: Optional[List[Action]] = Field(
        None, description="Used to filter the results. Only works for funding"
    )
    limit: int = 100
    offset: int = 0

    def as_url_params(self) -> str:
        """Returns the parameters for the GET request."""
        data = json.loads(
            self.model_dump_json(
                exclude_none=True,
            )
        )
        if data.get("sort"):
            data["sort"] = [f"{d['attribute']},{d['direction']}" for d in data["sort"]]

        return (
            urlencode(data, doseq=True)
            .replace("statuses", "status")
            .replace("actions", "action")
            .replace("limit", "size")
            .replace("offset", "page")
        )


class FundingRecord(BaseModel):
    action: Optional[Action] = None
    amount: Optional[float] = None
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    currency: Optional[Currency] = None
    customer_fee: Optional[int] = None
    id: Optional[UUID] = None
    inserted_at: Optional[datetime] = None
    reference: Optional[str] = None
    side: Optional[FundingSide] = None
    status: Optional[FundingStatus] = None
    updated_at: Optional[datetime] = None
    user_id: Optional[UUID] = None
    model_config = ConfigDict(alias_generator=camelcase)


class Fundings(BaseModel):
    fundings: Optional[List[FundingRecord]] = Field(None, alias="items")
    has_next: Optional[bool] = None
    page: Optional[int] = None
    total_items: Optional[int] = Field(None, alias="totalItems")
    model_config = ConfigDict(alias_generator=camelcase)


class CashAvailable(BaseModel):
    """Holds information about the cash available in your account."""

    buying_power: Optional[float] = None
    cash_available_for_transfer: Optional[float] = None
    cash_available_for_withdrawal_hold: Optional[float] = None
    cash_available_for_withdrawal: Optional[float] = None
    clearing_cash: Optional[float] = None
    pending_buys: Optional[int] = None
    pending_withdrawals: Optional[int] = None
    settled_cash: Optional[float] = None
    settlement_hold: Optional[int] = None
    trade_settlement: Optional[int] = None
    model_config = ConfigDict(alias_generator=camelcase)


class FundingsClient(BaseClient):
    async def list(self, request: FundingRequest) -> Fundings:
        """Returns the funding transactions executed by the user.

        Args:

            request (FundingRequest): the funding request.

        Returns:
            Fundings: the list of the fundings retrieved.
        """

        data: dict = await self._client.get(
            f"{self._client.exchange.transactions}?{request.as_url_params()}"
        )

        return Fundings(**data)

    async def in_flight(self) -> Fundings:
        """Returns the funds currently in flight."""
        request = FundingRequest(
            statuses=[FundingStatus.PENDING, FundingStatus.AWAITING_APPROVAL]
        )
        return await self.list(request=request)

    async def cash_available(self) -> CashAvailable:
        data = await self._client.get(self._client.exchange.cash_available)
        return CashAvailable(**data)
