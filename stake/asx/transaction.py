import json
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from urllib.parse import urlencode

from pydantic import BaseModel, ConfigDict, Field

from stake.asx.common import Side
from stake.common import BaseClient, camelcase

__all__ = ["TransactionRecordRequest", "SortDirection", "Sort"]


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class Sort(BaseModel):
    attribute: str
    direction: SortDirection


class TransactionRecordRequest(BaseModel):
    """Example call:

    t = TransactionRecordRequest(sort=[Sort(attribute='insertedAt', direction='asc')])
    """

    sort: Optional[List[Sort]] = Field(
        None, description="Use this to sort the results."
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
        if data.get("sort", None):
            data["sort"] = [f"{d['attribute']},{d['direction']}" for d in data["sort"]]

        return (
            urlencode(data, doseq=True)
            .replace("limit", "size")
            .replace("offset", "page")
        )


class Transaction(BaseModel):
    average_price: Optional[float] = None
    broker_order_id: Optional[int] = None
    completed_timestamp: Optional[datetime] = None
    consideration: Optional[float] = None
    contract_note_number: Optional[int] = None
    contract_note_numbers: Optional[List[int]] = None
    contract_note_received: Optional[bool] = None
    effective_price: Optional[float] = None
    execution_date: Optional[date] = None
    instrument_id: Optional[str] = Field(None, alias="instrumentCode")
    limit_price: Optional[float] = None
    order_completion_type: Optional[str] = None
    order_status: Optional[str] = None
    placed_timestamp: Optional[datetime] = None
    side: Optional[Side] = None
    type: Optional[str] = None
    units: Optional[float] = None
    user_brokerage_fees: Optional[float] = None
    model_config = ConfigDict(alias_generator=camelcase)


class Transactions(BaseModel):
    transactions: Optional[List[Transaction]] = Field(None, alias="items")
    has_next: Optional[bool] = None
    page: Optional[int] = None
    total_items: Optional[int] = None
    model_config = ConfigDict(alias_generator=camelcase)


class TransactionsClient(BaseClient):
    async def list(self, request: TransactionRecordRequest) -> Transactions:
        """Returns the transactions executed by the user.

        Args:
            request (TransactionRecordRequest):
                used to filter the transactions we want to retrieve

        Returns:
            Transactions: The matching transactions
        """

        data: dict = await self._client.get(
            f"{self._client.exchange.trade_activity}?{request.as_url_params()}"
        )

        return Transactions(**data)
