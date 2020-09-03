from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from stake.common import BaseClient, camelcase
from stake.constant import Url

__all__ = ["TransactionRecordRequest"]


class TransactionRecordEnumDirection(str, Enum):
    prev: str = "prev"
    next_: str = "next"


class TransactionRecordRequest(BaseModel):
    to: datetime = Field(default_factory=datetime.utcnow)
    from_: datetime = Field(
        default_factory=lambda *_: datetime.utcnow() - timedelta(days=365)
    )
    limit: int = 100
    offset: Optional[int]
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
    dnb: bool
    fin_tran_id: str = Field(alias="finTranID")
    fin_tran_type_id: str = Field(alias="finTranTypeID")
    fee_sec: float
    fee_taf: float
    fee_base: int
    fee_xtra_shares: int
    fee_exchange: int
    fill_qty: float
    fill_px: float
    send_commission_to_inteliclear: bool
    system_amount: int
    tran_amount: float
    tran_source: str
    tran_when: datetime
    wlp_amount: int
    wlp_fin_tran_type_id: UUID4 = Field(None, alias="wlpFinTranTypeID")
    dividend: Optional[float] = None
    dividend_tax: float = None
    merger_acquisition: Optional[float] = None
    position_delta: Optional[float] = None
    order_id: str = Field(alias="orderID")
    order_no: str
    instrument: Optional[Instrument] = None
    symbol: Optional[str]

    class Config:
        alias_generator = camelcase


class TransactionsClient(BaseClient):
    async def list(self, request: TransactionRecordRequest) -> List[Transaction]:
        """Returns the transactions executed by the user.

        Args:
            request (TransactionRecordRequest): specify the from+/to datetimes
              for the transaction collection.

        Returns:
            List[Transaction]: the transactions executed in the time frame.
        """
        payload = request.dict()
        payload.update(
            {"to": payload["to"].isoformat(), "from": payload.pop("from_").isoformat()}
        )

        data = await self._client.post(Url.account_transactions, payload=payload)
        transactions = []
        for d in data:
            if d.get("instrument"):
                d["symbol"] = d.get("instrument")["symbol"]
            transactions.append(Transaction(**d))
        return transactions
