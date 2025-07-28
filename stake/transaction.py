import enum
import json
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import UUID, UUID4

from stake.common import BaseClient, camelcase

__all__ = ["TransactionRecordRequest"]


class TransactionRecordEnumDirection(str, Enum):
    prev = "prev"
    next_ = "next"


class TransactionRecordRequest(BaseModel):
    to: datetime = Field(default_factory=lambda *_: datetime.now(timezone.utc))
    from_: datetime = Field(
        default_factory=lambda *_: datetime.now(timezone.utc) - timedelta(days=365),
        alias="from",
    )
    limit: int = 1000
    offset: Optional[datetime] = None
    direction: TransactionRecordEnumDirection = TransactionRecordEnumDirection.prev


class Instrument(BaseModel):
    id: UUID4
    symbol: str
    name: str


class Transaction(BaseModel):
    account_amount: float
    account_balance: float
    account_type: str
    comment: str
    dividend_tax: Optional[dict] = None
    dividend: Optional[dict] = None
    dnb: bool
    fee_base: int
    fee_exchange: int
    fee_sec: float
    fee_taf: float
    fee_xtra_shares: int
    fill_px: float
    fill_qty: float
    fin_tran_id: str = Field(alias="finTranID")
    fin_tran_type_id: str = Field(alias="finTranTypeID")
    instrument: Optional[Instrument] = None
    merger_acquisition: Optional[Dict] = None
    order_id: Optional[str] = Field(None, alias="orderID")
    order_no: Optional[str] = None
    position_delta: Optional[float] = None
    send_commission_to_inteliclear: bool
    symbol: Optional[str] = None
    system_amount: int
    tran_amount: float
    tran_source: str
    tran_when: datetime
    updated_reason: Optional[str] = None
    wlp_amount: int
    wlp_fin_tran_type_id: Optional[UUID] = Field(None, alias="wlpFinTranTypeID")
    model_config = ConfigDict(alias_generator=camelcase)


class TransactionHistoryType(str, enum.Enum):
    BUY = "Buy"
    CORPORATE_ACTION = "Corporate Action"
    DIVIDEND = "Dividend"
    DIVIDEND_TAX = "Dividend Tax"
    FUNDING = "Funding"
    SELL = "Sell"


class TransactionsClient(BaseClient):
    async def list(self, request: TransactionRecordRequest) -> List[Transaction]:
        """Returns the transactions executed by the user.

        Args:
            request (TransactionRecordRequest): specify the from+/to datetimes
              for the transaction collection.

        Returns:
            List[Transaction]: the transactions executed in the time frame.
        """
        payload = json.loads(request.model_dump_json(by_alias=True))

        data = await self._client.post(
            self._client.exchange.account_transactions, payload=payload
        )
        transactions = []
        for d in data:
            if d.get("instrument"):
                d["symbol"] = d.get("instrument")["symbol"]
            transactions.append(Transaction(**d))
        return transactions
