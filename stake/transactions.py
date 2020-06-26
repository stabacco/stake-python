from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel
from constant import Url
import weakref
from stake.product import Product


class TransactionRecordEnumDirection(str, Enum):
    prev: str = "prev"
    next_: str = "next"


class TransactionRecordRequest(BaseModel):
    to: datetime
    from_: datetime
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
    instrument: dict
    product: Product
    dividend: Optional[float]
    dividendTax: Optional[float]
    mergerAcquisition: Optional[float]
    positionDelta: Optional[float]
    orderID: str  # dwOrderId
    orderNo: str


class TransactionsClient:
    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def list(self, request: TransactionRecordRequest) -> List[Transaction]:
        """Returns the transactions executed by the user

        Args:
            request (TransactionRecordRequest): specify the from+/to datetimes 
              for the transaction collection.

        Returns:
            List[Transaction]: the transactions executed in the time frame.
        """
        payload = request.dict()

        # TODO: can this be done in pydantic? 
        payload.update({
            "endDate": request["endDate"].strftime("%d/%m/%Y"),
            "startDate": request["startDate"].strftime("%d/%m/%Y"),
        })

        data = await self._client._post(Url.account_transactions, payload=payload)

        transactions = []
        _cached_products = {}
        for d in data:
            # this was an instrument, but i don't like it, so i'm swapping it for the product
            instrument = d.pop["instrument"]
            product = _cached_products.get(instrument["symbol"])
            if not product:
                product = await self._client.products.get(instrument["symbol"])
            d["product"] = product
            transactions.append(Transaction(**d))
        return transactions


if __name__ == "__main__":
    from stake.client import StakeClient
    import asyncio
    c = StakeClient()
    request = TransactionRecordRequest(from_=datetime.today() - timedelta(days=365), to=datetime.today())
    result = asyncio.run( c.transactions.list(request))
    print(result)
