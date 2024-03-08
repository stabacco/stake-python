from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from stake.common import BaseClient, camelcase

__all__ = ["EquityPositions"]


class EquityPosition(BaseModel):
    available_for_trading_qty: Optional[int] = None
    average_price: Optional[str] = None
    instrument_id: Optional[str] = None
    market_value: Optional[str] = None
    mkt_price: Optional[str] = None
    name: Optional[str] = None
    open_qty: Optional[int] = None
    prior_close: Optional[str] = None
    recent_announcement: Optional[bool] = None
    sensitive: Optional[bool] = None
    symbol: Optional[str] = None
    unrealized_day_pl_percent: Optional[float] = Field(
        None, alias="unrealizedDayPLPercent"
    )
    unrealized_day_pl: Optional[float] = Field(None, alias="unrealizedDayPL")
    unrealized_pl_percent: Optional[float] = Field(None, alias="unrealizedPLPercent")
    unrealized_pl: Optional[float] = Field(None, alias="unrealizedPL")
    model_config = ConfigDict(alias_generator=camelcase)


class EquityPositions(BaseModel):
    """Represents the user's portforlio, with the list of the currently
    available equities."""

    page_num: Optional[int] = None
    has_next: Optional[bool] = None
    equity_positions: Optional[List[EquityPosition]] = None
    model_config = ConfigDict(alias_generator=camelcase)


class EquitiesClient(BaseClient):
    async def list(self) -> EquityPositions:
        """Displays the contents of your portfolio.

        Returns:
            EquityPositions: The list of your equities.
        """
        data = await self._client.get(self._client.exchange.equity_positions)
        return EquityPositions(**data)
