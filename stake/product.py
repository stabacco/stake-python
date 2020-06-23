from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    bought: int
    category: str
    childInstruments: list
    currencyID: Optional[str]
    dailyReturn: float
    dailyReturnPercentage: float
    description: str
    encodedName: str
    id: str
    inceptionDate: Optional[str]
    instrumentTags: list
    instrumentTypeID: Optional[str]
    lastTraded: float
    monthlyReturn: float
    name: str
    news: int
    parentID: Optional[str]
    period: str
    popularity: float
    productType: str
    sector: str
    symbol: str
    tradeStatus: int
    urlImage: str
    viewed: int
    watched: int
    yearlyReturnPercentage: float
    yearlyReturnValue: float
