from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TransactionRecordEnumDirection(str, Enum):
    prev: str = "prev"
    next_: str = "next"


class TransactionRecordRequest(BaseModel):
    to: datetime
    from_: datetime
    limit: int
    offset: Optional[int]
    direction: TransactionRecordEnumDirection = TransactionRecordEnumDirection.prev


class Transaction(BaseModel):
    {
        "accountAmount": 170.83,
        "accountBalance": 6118.58,
        "accountType": "LIVE",
        "comment": "Sell 1 shares of VHT at 170.83 PART fill",
        "dnb": false,
        "finTranID": "HB.7724cf49-f006-42cd-8825-c1954344edc5",
        "finTranTypeID": "SSAL",
        "feeSec": 0,
        "feeTaf": 0,
        "feeBase": 0,
        "feeXtraShares": 0,
        "feeExchange": 0,
        "fillQty": 1,
        "fillPx": 170.83,
        "sendCommissionToInteliclear": false,
        "systemAmount": 0,
        "tranAmount": 170.83,
        "tranSource": "EMS",
        "tranWhen": "2020-02-28T15:04:09.541Z",
        "wlpAmount": 0,
        "wlpFinTranTypeID": null,
        "instrument": {
            "id": "6ce8fef7-8933-4b8e-9556-e55134797851",
            "symbol": "VHT",
            "name": "Health Care Vanguard ETF",
        },
        "dividend": null,
        "dividendTax": null,
        "mergerAcquisition": null,
        "positionDelta": null,
        "orderID": "HB.80e95687-6d88-4f14-8848-b37b9dbfc09d",
        "orderNo": "HBWU011781",
    },


class TransactionsClient:
    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def list(self, request: TransactionRecordRequest) -> List[Transaction]:
        payload = {
            "endDate": request.endDate.strftime("%d/%m/%Y"),
            "startDate": request.startDate.strftime("%d/%m/%Y"),
        }
        data = await self._client._post(Url.fundings, payload=payload)

        return [Funding(**d) for d in data]
