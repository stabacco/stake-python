from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from stake.common import BaseClient, SideEnum, camelcase

__all__ = ["EquityCategory"]


class EquityCategory(str, Enum):
    ETF = "ETF"
    STOCK = "Stock"


class EquityPosition(BaseModel):
    ask_price: Optional[float] = None
    available_for_trading_qty: float
    average_price: float = Field(alias="avgPrice")
    bid_price: Optional[float] = None
    category: Optional[EquityCategory] = None
    cost_basis: float
    daily_return_value: float
    encoded_name: str
    instrument_id: UUID = Field(alias="instrumentID")
    last_trade: float
    market_price: float = Field(alias="mktPrice")
    market_value: float
    name: str
    open_qty: float
    period: str
    prior_close: float
    return_on_stock: Optional[float] = None
    side: SideEnum
    symbol: str
    unrealized_day_pl_percent: float = Field(alias="unrealizedDayPLPercent")
    unrealized_day_pl: float = Field(alias="unrealizedDayPL")
    unrealized_pl: float = Field(alias="unrealizedPL")
    url_image: str
    yearly_return_percentage: Optional[float] = None
    yearly_return_value: Optional[float] = None
    model_config = ConfigDict(alias_generator=camelcase)


class EquityPositions(BaseModel):
    """Represents the user's portforlio, with the list of the currently
    available equities."""

    equity_positions: List[EquityPosition]
    equity_value: float
    prices_only: bool
    model_config = ConfigDict(alias_generator=camelcase)


class EquitiesClient(BaseClient):
    async def list(self) -> EquityPositions:
        """Displays the contents of your portfolio.

        Returns:
            EquityPositions: The list of your equities.
        """
        data = await self._client.get(self._client.exchange.equity_positions)
        return EquityPositions(**data)
