from enum import Enum
from typing import Type

import pydantic

STAKE_URL = "https://global-prd-api.hellostake.com/api/"
class NYSERoutes(str, Enum):
    """Contains all the visited stake urls."""

    account_balance: str = STAKE_URL + "cma/getAccountBalance"
    account_transactions: str = STAKE_URL +"users/accounts/accountTransactions"
    cancel_order: str = STAKE_URL +"orders/cancelOrder/{orderId}"
    cash_available: str = STAKE_URL +"users/accounts/cashAvailableForWithdrawal"
    create_session: str = STAKE_URL +"sessions/v2/createSession"
    equity_positions: str =STAKE_URL + "users/accounts/v2/equityPositions"
    fund_details: str = STAKE_URL +"fund/details"
    fundings: str = STAKE_URL +"utils/activityLog/fundingOnly"
    market_status: str = STAKE_URL +"utils/marketStatus"
    orders: str = STAKE_URL +"users/accounts/v2/orders"
    products_suggestions: str = STAKE_URL +"products/getProductSuggestions/{keyword}"
    quick_buy: str = STAKE_URL +"purchaseorders/v2/quickBuy"
    quotes: str = STAKE_URL +"quotes/marketData/{symbols}"
    rate: str = STAKE_URL +"wallet/rate"
    ratings: str = STAKE_URL +"data/calendar/ratings?tickers={symbols}&pageSize={limit}"
    sell_orders: str = STAKE_URL +"sellorders"
    symbol: str = STAKE_URL +"products/searchProduct?symbol={symbol}&page=1&max=1"
    transactions: str = STAKE_URL +"users/accounts/transactions"
    user: str = STAKE_URL +"user"
    watchlist_modify: str = STAKE_URL +"instruments/addRemoveInstrumentWatchlist"
    watchlist: str = STAKE_URL +"products/productsWatchlist/{userId}"





class NYSE(pydantic.BaseModel):
    base_url: str = STAKE_URL
    routes: Type[NYSERoutes] = NYSERoutes


STAKE_ASX_URL = "https://global-prd-api.hellostake.com/api/asx/"


class ASXRoutes(str, Enum):
    """Contains all the visited stake urls."""

    account_balance: str = STAKE_ASX_URL + "cma/getAccountBalance"
    account_transactions: str = STAKE_ASX_URL +"users/accounts/accountTransactions"
    cancel_order: str = STAKE_ASX_URL +"orders/cancelOrder/{orderId}"
    cash_available: str = STAKE_ASX_URL +"users/accounts/cashAvailableForWithdrawal"
    create_session: str = STAKE_ASX_URL +"sessions/v2/createSession"
    equity_positions: str = STAKE_ASX_URL +"instrument/equityPositions"
    fund_details: str = STAKE_ASX_URL +"fund/details"
    fundings: str = STAKE_ASX_URL +"transactions?status=RECONCILED&size=100&sort=insertedAt,desc&page=0"
    market_status: str = STAKE_ASX_URL +"utils/marketStatus"
    orders: str = STAKE_ASX_URL +"users/accounts/v2/orders"
    products_suggestions: str = STAKE_ASX_URL +"products/getProductSuggestions/{keyword}"
    quick_buy: str = STAKE_ASX_URL +"purchaseorders/v2/quickBuy"
    quotes: str = STAKE_ASX_URL +"quotes/marketData/{symbols}"
    rate: str = STAKE_ASX_URL +"wallet/rate"
    ratings: str = STAKE_ASX_URL +"data/calendar/ratings?tickers={symbols}&pageSize={limit}"
    sell_orders: str = STAKE_ASX_URL +"sellorders"
    symbol: str = STAKE_ASX_URL +"products/searchProduct?symbol={symbol}&page=1&max=1"
    transactions: str = STAKE_ASX_URL +"users/accounts/transactions"
    user: str = STAKE_URL +"user"
    watchlist_modify: str = STAKE_ASX_URL +"instruments/addRemoveInstrumentWatchlist"
    watchlist: str = STAKE_ASX_URL + "products/productsWatchlist/{userId}"


class ASX(pydantic.BaseModel):
    base_url: str = STAKE_ASX_URL
    routes: Type[ASXRoutes] = ASXRoutes
