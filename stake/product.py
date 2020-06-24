import weakref
from typing import List
from typing import Optional

from pydantic import BaseModel


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
    def __init__(self, client: "_StakeClient"):
        self._client = weakref.proxy(client)

    async def get(self, symbol: str) -> Optional[Product]:
        """Given a symbol it will return the matching product.

        Examples:
            tesla_product = self.list("TSLA")
        """
        data = await self._client._get(
            f"products/searchProduct?symbol={symbol}&page=1&max=1"
        )

        if not data["products"]:
            return None

        return Product(**data["products"][0])

    async def search(self, keywords: List[str], max_results: int = 30) -> List[Product]:
        """ Searches products by keywords.

        Args:
            keywords:
            max_results: number of paginated results.

        Returns:
            the list of `Product` matching the query

        Examples:
            technology_products = self.search(["Technology"])

        """
        products = await self._client._get(
            self._client._url(
                f"products/searchProduct?keywords={'+'.join(keywords)}"
                f"&orderBy=dailyReturn&productType=10&page=1&max={max_results}"
            )
        )
        return [Product(**product) for product in products["products"]]
