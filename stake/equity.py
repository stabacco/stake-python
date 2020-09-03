import weakref
from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import UUID4

from stake.common import BaseClient
from stake.common import camelcase
from stake.common import SideEnum
from stake.constant import Url


class EquityCategory(str, Enum):
    ETF = "ETF"
    STOCK = "Stock"


class EquityPosition(BaseModel):
    available_for_trading_qty: float
    average_price: float = Field(alias="avgPrice")
    category: EquityCategory
    cost_basis: float
    daily_return_value: float
    encoded_name: str
    instrument_id: UUID4
    last_trade: float
    market_value: float
    market_price: float = Field(alias="mktPrice")
    name: str
    open_qty: float
    period: str
    prior_close: float
    side: SideEnum
    symbol: str
    unrealized_day_pl: float
    unrealized_day_pl_percent: float
    unrealized_pl: float
    url_image: str
    yearly_return_percentage: float
    yearly_return_value: float
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
        data = await self._client.get(Url.equity_positions)
        return EquityPositions(**data)
