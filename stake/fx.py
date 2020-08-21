"Currency conversion"

import weakref
from enum import Enum

from pydantic import BaseModel
from pydantic.types import UUID

from common import camelcase
from stake.constant import Url

__all__ = ["FxConversionRequest", "CurrencyEnum"]


class CurrencyEnum(str, Enum):
    AUD: str = "AUD"
    USD: str = "USD"


class FxConversionRequest(BaseModel):
    from_currency: CurrencyEnum
    to_currency: CurrencyEnum
    from_amount: float


class FxConversion(BaseModel):
    from_currency: CurrencyEnum
    to_currency: CurrencyEnum
    from_amount: float
    to_amount: float
    rate: float
    quote: UUID

    class Config:
        alias_generator = camelcase


class FxClient:
    def __init__(self, client):
        self._client = weakref.proxy(client)

    async def convert(self,
                      currency_conversion_request: FxConversionRequest) -> FxConversion:
        """Converts from one currency to another."""

        payload = {
            "fromCurrency": currency_conversion_request.from_currency,
            "toCurrency": currency_conversion_request.to_currency,
            "fromAmount": currency_conversion_request.from_amount
        }
        data = await self._client.post(Url.rate,
                                       payload=payload)
        return FxConversion(**data)
