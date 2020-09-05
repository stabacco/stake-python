"""Currency conversion."""
from enum import Enum

from pydantic import BaseModel
from pydantic.types import UUID4

from stake.common import BaseClient, camelcase
from stake.constant import Url

__all__ = ["FxConversionRequest", "CurrencyEnum"]


class CurrencyEnum(str, Enum):
    AUD: str = "AUD"
    USD: str = "USD"


class FxConversionRequest(BaseModel):
    from_currency: CurrencyEnum
    to_currency: CurrencyEnum
    from_amount: float

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class FxConversion(BaseModel):
    from_currency: CurrencyEnum
    to_currency: CurrencyEnum
    from_amount: float
    to_amount: float
    rate: float
    quote: UUID4

    class Config:
        alias_generator = camelcase


class FxClient(BaseClient):
    async def convert(
        self, currency_conversion_request: FxConversionRequest
    ) -> FxConversion:
        """Converts from one currency to another."""
        data = await self._client.post(
            Url.rate, payload=currency_conversion_request.dict(by_alias=True)
        )
        return FxConversion(**data)
