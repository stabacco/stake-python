import uuid
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic.fields import Field

from stake.common import BaseClient, camelcase

if TYPE_CHECKING:
    from stake.client import StakeClient
    from stake.ratings import Rating
    from stake.statement import Statement

__all__ = ["ProductSearchByName"]


class ProductSearchByName(BaseModel):
    """Request used to search for Products by their name or description."""

    keyword: str


class Instrument(BaseModel):
    encoded_name: Optional[str] = None
    image_url: Optional[str] = None
    instrument_id: str
    name: str
    symbol: str
    model_config = ConfigDict(alias_generator=camelcase)


class Product(BaseModel):
    id: uuid.UUID
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
    monthly_return: float
    yearly_return_percentage: Optional[float] = None
    yearly_return_value: Optional[float] = None
    popularity: int
    watched: int
    news: int
    bought: int
    viewed: int
    product_type: str
    trade_status: Optional[int] = None
    encoded_name: str
    period: str
    inception_date: Optional[datetime] = None
    instrument_tags: List[Any]
    child_instruments: List[Instrument]
    _client: "StakeClient" = PrivateAttr()
    model_config = ConfigDict(alias_generator=camelcase)

    def model_post_init(self, context: Any | None = None) -> None:
        if context:
            self._client = context.get("client")
            assert self._client

    async def ratings(self) -> "List[Rating]":
        from stake import RatingsRequest

        return await self._client.ratings.list(RatingsRequest(symbols=[self.symbol]))

    async def statements(self, start_date: date | None = None) -> "List[Statement]":
        from stake.statement import StatementRequest

        return await self._client.statements.list(
            StatementRequest(
                symbol=self.symbol,
                start_date=start_date or (date.today() - timedelta(days=365)),
            )
        )


class ProductsClient(BaseClient):
    async def get(self, symbol: str) -> Optional[Product]:
        """Given a symbol it will return the matching product.

        Examples:
            tesla_product = self.get("TSLA")
        """
        data = await self._client.get(
            self._client.exchange.symbol.format(symbol=symbol)
        )

        return (
            Product.model_validate(
                data["products"][0], context=dict(client=self._client)
            )
            if data["products"]
            else None
        )

    async def search(self, request: ProductSearchByName) -> List[Instrument]:
        products = await self._client.get(
            self._client.exchange.products_suggestions.format(keyword=request.keyword)
        )
        return [
            Instrument.model_validate(product) for product in products["instruments"]
        ]

    async def product_from_instrument(
        self, instrument: Instrument
    ) -> Optional[Product]:
        return await self.get(instrument.symbol)
