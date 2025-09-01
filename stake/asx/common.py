from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeType(str, Enum):
    """The type of trade the user is requesting."""

    MARKET = "MARKET_TO_LIMIT"
    LIMIT = "LIMIT"
    STOP = "STOP"
