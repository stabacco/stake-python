# sourcery skip: use-fstring-for-concatenation
from urllib.parse import urljoin

from pydantic import BaseModel


class BaseUrl(BaseModel):
    """Contains all the visited stake urls for the NYSE."""

    STAKE_URL: str = "https://global-prd-api.hellostake.com/api/"
    account_balance: str = urljoin(
        STAKE_URL, "cma/getAccountBalance", allow_fragments=True
    )
    account_transactions: str = urljoin(
        STAKE_URL, "users/accounts/accountTransactions", allow_fragments=True
    )
    cancel_order: str = urljoin(
        STAKE_URL, "orders/cancelOrder/{orderId}", allow_fragments=True
    )
    cash_available: str = urljoin(
        STAKE_URL, "users/accounts/cashAvailableForWithdrawal", allow_fragments=True
    )
    create_session: str = urljoin(
        STAKE_URL, "sessions/v2/createSession", allow_fragments=True
    )
    equity_positions: str = urljoin(
        STAKE_URL, "users/accounts/v2/equityPositions", allow_fragments=True
    )
    fund_details: str = urljoin(STAKE_URL, "fund/details", allow_fragments=True)
    market_status: str = urljoin(STAKE_URL, "utils/marketStatus", allow_fragments=True)
    orders: str = urljoin(STAKE_URL, "users/accounts/v2/orders", allow_fragments=True)
    products_suggestions: str = urljoin(
        STAKE_URL, "products/getProductSuggestions/{keyword}", allow_fragments=True
    )
    quick_buy: str = urljoin(
        STAKE_URL, "purchaseorders/v2/quickBuy", allow_fragments=True
    )
    quotes: str = urljoin(
        STAKE_URL, "quotes/marketData/{symbols}", allow_fragments=True
    )
    rate: str = urljoin(STAKE_URL, "wallet/rate", allow_fragments=True)
    ratings: str = urljoin(
        STAKE_URL,
        "data/calendar/ratings?tickers={symbols}&pageSize={limit}",
        allow_fragments=True,
    )
    sell_orders: str = urljoin(STAKE_URL, "sellorders", allow_fragments=True)
    symbol: str = urljoin(
        STAKE_URL,
        "products/searchProduct?symbol={symbol}&page=1&max=1",
        allow_fragments=True,
    )
    transaction_history: str = urljoin(
        STAKE_URL, "users/accounts/transactionHistory", allow_fragments=True
    )
    transaction_details: str = urljoin(
        STAKE_URL,
        (
            "users/accounts/transactionDetails?"
            "reference={reference}&referenceType={reference_type}"
        ),
        allow_fragments=True,
    )
    transactions: str = urljoin(
        STAKE_URL, "users/accounts/transactions", allow_fragments=True
    )
    users: str = urljoin(STAKE_URL, "user", allow_fragments=True)

    # deprecated, use update_watchlist instead
    watchlist_modify: str = urljoin(
        STAKE_URL, "instruments/addRemoveInstrumentWatchlist", allow_fragments=True
    )
    # deprecated, use read_watchlist instead
    watchlist: str = urljoin(
        STAKE_URL, "products/productsWatchlist/{userId}", allow_fragments=True
    )

    watchlists: str = "https://api.prd.stakeover.io/us/instrument/watchlists"
    create_watchlist: str = "https://api.prd.stakeover.io/us/instrument/watchlist"
    read_watchlist: str = (
        "https://api.prd.stakeover.io/us/instrument/watchlist/{watchlist_id}"
    )
    update_watchlist: str = read_watchlist + "/items"


# The New York Stock Exchange
NYSE = BaseUrl()
