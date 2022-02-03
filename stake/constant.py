from enum import Enum


class Url(str, Enum):
    """Contains all the visited stake urls."""

    account_balance: str = "cma/getAccountBalance"
    account_transactions: str = "users/accounts/accountTransactions"
    cancel_order: str = "orders/cancelOrder/${orderId}"
    cash_available: str = "users/accounts/cashAvailableForWithdrawal"
    create_session: str = "sessions/v2/createSession"
    equity_positions: str = "users/accounts/v2/equityPositions"
    fund_details: str = "fund/details"
    market_status: str = "utils/marketStatus"
    orders: str = "users/accounts/v2/orders"
    products_suggestions: str = "products/getProductSuggestions/${keyword}"
    quick_buy: str = "purchaseorders/v2/quickBuy"
    quotes: str = "quotes/marketData/${symbols}"
    rate: str = "wallet/rate"
    ratings: str = "data/calendar/ratings?tickers=${symbols}&pageSize=${limit}"
    sell_orders: str = "sellorders"
    symbol: str = "products/searchProduct?symbol=${symbol}&page=1&max=1"
    transaction_history: str = "users/accounts/transactionHistory"
    transaction_details: str = (
        "users/accounts/transactionDetails?"
        "reference=${reference}&referenceType=${reference_type}"
    )
    transactions: str = "users/accounts/transactions"
    user: str = "user"
    watchlist_modify: str = "instruments/addRemoveInstrumentWatchlist"
    watchlist: str = "products/productsWatchlist/${userId}"


STAKE_URL = "https://global-prd-api.hellostake.com/api/"
