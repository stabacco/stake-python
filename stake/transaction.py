from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from stake.common import BaseClient
from stake.constant import Url
from stake.product import Product

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


class Transaction(BaseModel):
    accountAmount: float
    accountBalance: float
    accountType: str
    comment: str
    dnb: bool
    finTranID: str
    finTranTypeID: str
    fillQty: float
    fillPx: float
    tranAmount: float
    tranSource: str
    tranWhen: datetime
    instrument: Optional[dict]
    product: Optional[Product]
    dividend: Optional[dict]
    # dividendTax: Optional[str]
    mergerAcquisition: Optional[float]
    positionDelta: Optional[float]
    orderID: Optional[str]  # dwOrderId
    orderNo: Optional[str]
    symbol: str


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

        # # TODO: can this be done in pydantic?
        payload.update(
            {"to": payload["to"].isoformat(), "from": payload.pop("from_").isoformat()}
        )

        data = await self._client.post(Url.account_transactions, payload=payload)
        transactions = []
        # _cached_products: dict = {}
        for d in data:
            # this was an instrument, but i don't like it,
            # so i'm swapping it for the product.
            instrument = d.pop("instrument", None)

            if not instrument:
                continue  # TODO: need different types, divident etc...
            d["symbol"] = instrument["symbol"]

            ##
            # product = _cached_products.get(instrument["symbol"])
            # if not product:
            #     # print("getting symbol", instrument["symbol"])
            #     product = await self._client.products.get(instrument["symbol"])
            # d["product"] = product
            transactions.append(Transaction(**d))
        return transactions
