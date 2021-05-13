from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from stake.common import BaseClient, SideEnum, camelcase
from stake.constant import Url


class EquityCategory(str, Enum):
    ETF = "ETF"
    STOCK = "Stock"


class EquityPosition(BaseModel):
    available_for_trading_qty: float
    average_price: float = Field(alias="avgPrice")
    category: Optional[EquityCategory] = None
    cost_basis: float
    daily_return_value: float
    encoded_name: str
    instrument_id: UUID = Field(alias="instrumentID")
    last_trade: float
    market_value: float
    market_price: float = Field(alias="mktPrice")
    name: str
    open_qty: float
    period: str
    prior_close: float
    side: SideEnum
    symbol: str
    unrealized_day_pl: float = Field(alias="unrealizedDayPL")
    unrealized_day_pl_percent: float = Field(alias="unrealizedDayPLPercent")
    unrealized_pl: float = Field(alias="unrealizedPL")
    url_image: str
    yearly_return_percentage: Optional[float] = None
    yearly_return_value: Optional[float] = None
    ask_price: Optional[float] = None
    bid_price: Optional[float] = None
    return_on_stock: Optional[float] = None

    class Config:
        alias_generator = camelcase


class EquityPositions(BaseModel):
    """Represents the user's portforlio, with the list of the currently
    available equities."""

    equity_positions: List[EquityPosition]
    equity_value: float
    prices_only: bool

    class Config:
        alias_generator = camelcase


class EquitiesClient(BaseClient):
    async def list(self) -> EquityPositions:
        """Displays the contents of your portfolio.

        Returns:
            EquityPositions: The list of your equities.
        """
        data = await self._client.get(Url.equity_positions)
        return EquityPositions(**data)
