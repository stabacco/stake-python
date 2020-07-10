import weakref
from typing import List
from typing import Optional

from pydantic import BaseModel

from stake.constant import Url


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


class ProductsClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

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

    async def product_from_instrument(self, instrument: Instrument) -> Product:
        return await self.get(instrument.symbol)

    # async def search(self, keywords: List[str], max_results: int = 30) -> List[Product]:
    #     """Searches products by keywords.

    #     Args:
    #         keywords:
    #         max_results: number of paginated results.

    #     Returns:
    #         the list of `Product` matching the query

    #     Examples:
    #         technology_products = self.search(["Technology"])
    #     """

    #     products = await self._client.get(
    #         self._client.httpClient.url(
    #             f"products/searchProduct?keywords={'+'.join(keywords)}"
    #             f"&orderBy=dailyReturn&productType=10&page=1&max={max_results}"
    #         )
    #     )
    #     return [Product(**product) for product in products["products"]]
