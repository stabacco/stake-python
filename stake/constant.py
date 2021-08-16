from enum import Enum


class Url(str, Enum):
    """Contains all the visited stake urls."""

    account_balance: str = "cma/getAccountBalance"
    account_transactions: str = "users/accounts/accountTransactions"
    cash_available: str = "users/accounts/cashAvailableForWithdrawal"
    create_session: str = "sessions/v2/createSession"
    equity_positions: str = "users/accounts/v2/equityPositions"
    fund_details: str = "fund/details"
    fundings: str = "utils/activityLog/fundingOnly"
    market_status: str = "utils/marketStatus"
    orders: str = "users/accounts/v2/orders"
    quotes: str = "quotes/marketData/{symbols}"
    rate: str = "wallet/rate"
    transactions: str = "users/accounts/transactions"
    user: str = "user"
    quick_buy: str = "purchaseorders/v2/quickBuy"
    sell_orders: str = "sellorders"
    cancel_order: str = "orders/cancelOrder/{orderId}"
    symbol: str = "products/searchProduct?symbol={symbol}&page=1&max=1"
    products_suggestions: str = "products/getProductSuggestions/{keyword}"
    watchlist_modify: str = "instruments/addRemoveInstrumentWatchlist"
    watchlist: str = "products/productsWatchlist/{userId}"
    ratings: str = "data/calendar/ratings?tickers={symbols}&pageSize={limit}"


STAKE_URL = "https://global-prd-api.hellostake.com/api/"
