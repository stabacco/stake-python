from typing import Any, List, Optional

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import UUID4

from stake.common import BaseClient, camelcase
from stake.constant import Url

__all__ = ["ProductSearchByName"]


class ProductSearchByName(BaseModel):
    """Request used to search for Products by their name or description."""

    keyword: str


class Instrument(BaseModel):
    encoded_name: str
    image_url: str
    instrument_id: str
    name: str
    symbol: str

    class Config:
        alias_generator = camelcase


class Product(BaseModel):
    id: UUID4
    instrument_type_id: Optional[str] = Field(None, alias="instrumentTypeID")
    symbol: str
    description: str
    category: Optional[str] = None
    currency_id: Optional[str] = Field(None, alias="currencyID")
    url_image: str
    sector: Optional[str] = None
    parent_id: Optional[str] = Field(None, alias="parentID")
    name: str
    daily_return: float
    daily_return_percentage: float
    last_traded: float
    monthly_return: int
    yearly_return_percentage: Optional[float] = None
    yearly_return_value: Optional[float] = None
    popularity: int
    watched: int
    news: int
    bought: int
    viewed: int
    product_type: str
    trade_status: Optional[int]
    encoded_name: str
    period: str
    inception_date: Optional[str]
    instrument_tags: List[Any]
    child_instruments: List[Instrument]

    class Config:
        alias_generator = camelcase


class ProductsClient(BaseClient):
    async def get(self, symbol: str) -> Optional[Product]:
        """Given a symbol it will return the matching product.

        Examples:
            tesla_product = self.get("TSLA")
        """
        data = await self._client.get(Url.symbol.format(symbol=symbol))  # type: ignore

        if not data["products"]:
            return None

        return Product(**data["products"][0])

    async def search(self, request: ProductSearchByName) -> List[Instrument]:
        products = await self._client.get(
            Url.products_suggestions.format(keyword=request.keyword)  # type: ignore
        )
        return [Instrument(**product) for product in products["instruments"]]

    async def product_from_instrument(
        self, instrument: Instrument
    ) -> Optional[Product]:
        return await self.get(instrument.symbol)
