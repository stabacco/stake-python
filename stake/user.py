from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    userId: str
    firstName: str
    lastName: str
    emailAddress: str
    macStatus: str
    accountType: str
    regionIdentifier: str
    dw_AccountNumber: Optional[str]
    canTradeOnUnsettledFunds: Optional[bool]
    username: Optional[str]
