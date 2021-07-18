from typing import List, Optional

import pydantic
from pydantic import BaseModel

from stake.common import BaseClient, camelcase
from stake.constant import Url

__all__ = ["RatingsRequest"]


class RatingsRequest(BaseModel):
    """Request for retrieving the ratings for the given symbols."""

    symbols: List[str]
    limit: Optional[int] = 50


class Rating(pydantic.BaseModel):
    id: Optional[str] = None
    ticker: Optional[str] = None
    exchange: Optional[str] = None
    name: Optional[str] = None
    analyst: Optional[str] = None
    currency: Optional[str] = None
    url: Optional[str] = None
    importance: Optional[int] = None
    notes: Optional[str] = None
    updated: Optional[int] = None
    action_pt: Optional[str] = None
    action_company: Optional[str] = None
    rating_current: Optional[str] = None
    pt_current: Optional[float] = None
    rating_prior: Optional[str] = None
    pt_prior: Optional[float] = None
    url_calendar: Optional[str] = None
    url_news: Optional[str] = None
    analyst_name: Optional[str] = None

    class Config:
        alias_generator = camelcase


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
        return [Rating(**d) for d in data]
