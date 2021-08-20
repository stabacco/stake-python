from datetime import datetime
from typing import List, Optional

import pydantic

from stake.common import BaseClient
from stake.constant import Url

__all__ = ["RatingsRequest"]


class RatingsRequest(pydantic.BaseModel):
    """Request for retrieving the ratings for the given symbols."""

    symbols: List[str]
    limit: Optional[int] = 50


class Rating(pydantic.BaseModel):
    id: Optional[str] = None
    symbol: Optional[str] = pydantic.Field(alias="ticker")
    exchange: Optional[str] = None
    name: Optional[str] = None
    analyst: Optional[str] = None
    currency: Optional[str] = None
    url: Optional[str] = None
    importance: Optional[int] = None
    notes: Optional[str] = None
    updated: Optional[datetime] = None
    action_pt: Optional[str] = None
    action_company: Optional[str] = None
    rating_current: Optional[str] = None
    pt_current: Optional[float] = None
    rating_prior: Optional[str] = None
    pt_prior: Optional[float] = None
    url_calendar: Optional[str] = None
    url_news: Optional[str] = None
    analyst_name: Optional[str] = None

    @pydantic.validator("pt_prior", "rating_prior", pre=True)
    def pt_prior_blank_string(value, field):
        if value == "":
            return None
        return value


class RatingsClient(BaseClient):
    """This client is in charge listing the experts' ratings for symbols."""

    async def list(self, request: RatingsRequest) -> List[Rating]:
        """Lists all the ratings for the symbols specified in the request.

        Returns:
            List[Rating]: The list of ratings.
        """
        data = await self._client.get(
            Url.ratings.format(
                symbols=",".join(request.symbols), limit=request.limit
            )  # type: ignore
        )

        if data == {"message": "No data returned"}:
            return []

        return [Rating(**d) for d in data["ratings"]]
