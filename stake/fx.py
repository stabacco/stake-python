"""Currency conversion."""

from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic.types import UUID4

from stake.common import BaseClient, camelcase

__all__ = ["FxConversionRequest", "CurrencyEnum"]


class CurrencyEnum(str, Enum):
    AUD = "AUD"
    USD = "USD"


class FxConversionRequest(BaseModel):
    from_currency: CurrencyEnum
    to_currency: CurrencyEnum
    from_amount: float
    model_config = ConfigDict(alias_generator=camelcase, populate_by_name=True)


class FxConversion(BaseModel):
    from_currency: CurrencyEnum
    to_currency: CurrencyEnum
    from_amount: float
    to_amount: float
    rate: float
    quote: UUID4
    model_config = ConfigDict(alias_generator=camelcase)


class FxClient(BaseClient):
    async def convert(
        self, currency_conversion_request: FxConversionRequest
    ) -> FxConversion:
        """Converts from one currency to another."""
        data = await self._client.post(
            self._client.exchange.rate,
            payload=currency_conversion_request.model_dump(by_alias=True),
        )
        return FxConversion(**data)
