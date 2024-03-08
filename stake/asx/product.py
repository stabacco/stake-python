from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from stake.common import BaseClient, camelcase

__all__ = ["ProductSearchByName"]


class ProductSearchByName(BaseModel):
    """Request used to search for Products by their name or description."""

    keyword: str


class Instrument(BaseModel):

    instrument_id: str
    symbol: str
    name: Optional[str] = None
    type: str
    recent_announcement: Optional[bool] = None
    sensitive: Optional[bool] = None
    model_config = ConfigDict(alias_generator=camelcase)


class Product(BaseModel):
    symbol: Optional[str] = None
    out_of_market_quantity: Optional[int] = None
    out_of_market_surplus: Optional[int] = None
    market_status: Optional[str] = None
    last_traded_exchange: Optional[str] = None
    last_traded_timestamp: Optional[int] = None
    last_trade: Optional[str] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    prior_close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    points_change: Optional[float] = None
    percentage_change: Optional[float] = None
    out_of_market_price: Optional[float] = None
    model_config = ConfigDict(alias_generator=camelcase)


class ProductsClient(BaseClient):
    async def get(self, symbol: str) -> Optional[Product]:
        """Given a symbol it will return the matching product.

        Examples:
            coles_product = self.get("COL")
        """
        data = await self._client.get(
            self._client.exchange.symbol.format(symbol=symbol)
        )

        return Product(**data)

    async def search(self, request: ProductSearchByName) -> List[Instrument]:
        products = await self._client.get(
            self._client.exchange.products_suggestions.format(keyword=request.keyword)
        )
        return [Instrument(**product) for product in products["instruments"]]

    async def product_from_instrument(
        self, instrument: Instrument
    ) -> Optional[Product]:
        return await self.get(instrument.symbol)
