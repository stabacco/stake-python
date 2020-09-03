from typing import List, Optional

from pydantic import BaseModel

from stake.common import BaseClient
from stake.constant import Url

__all__ = ["ProductSearchByName"]


class ProductSearchByName(BaseModel):
    """Request used to search for Products by their name or description."""

    keyword: str


class Instrument(BaseModel):
    encodedName: str
    imageUrl: str
    instrumentId: str
    name: str
    symbol: str


class Product(BaseModel):
    name: str
    symbol: str
    encodedName: str
    id: str
    dailyReturn: float
    dailyReturnPercentage: float
    monthlyReturn: float
    bought: int
    category: str
    childInstruments: list
    currencyID: Optional[str]
    description: str
    inceptionDate: Optional[str]
    instrumentTags: list
    instrumentTypeID: Optional[str]
    lastTraded: float
    news: int
    parentID: Optional[str]
    period: str
    popularity: float
    productType: str
    sector: Optional[str]
    tradeStatus: int
    urlImage: str
    viewed: int
    watched: int
    yearlyReturnPercentage: Optional[float]
    yearlyReturnValue: Optional[float]


class ProductsClient(BaseClient):
    async def get(self, symbol: str) -> Optional[Product]:
        """Given a symbol it will return the matching product.

        Examples:
            tesla_product = self.get("TSLA")
        """
        data = await self._client.get(Url.symbol.format(symbol=symbol))

        if not data["products"]:
            return None

        return Product(**data["products"][0])

    async def search(self, request: ProductSearchByName) -> List[Instrument]:
        products = await self._client.get(
            Url.products_suggestions.format(keyword=request.keyword)
        )
        return [Instrument(**product) for product in products["instruments"]]

    async def product_from_instrument(
        self, instrument: Instrument
    ) -> Optional[Product]:
        return await self.get(instrument.symbol)
