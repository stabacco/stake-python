from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeType(str, Enum):
    """The type of trade the user is requesting."""

    MARKET: str = "MARKET_TO_LIMIT"
    LIMIT: str = "LIMIT"
