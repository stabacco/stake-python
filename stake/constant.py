from enum import Enum


class Url(str, Enum):
    """Contains all the visited urls."""

    account_balance: str = "cma/getAccountBalance"
    account_transactions: str = "users/accounts/accountTransactions"  # post
    cash_available: str = "users/accounts/cashAvailableForWithdrawal"
    create_session: str = "sessions/createSession"
    equity_positions: str = "users/accounts/equityPositions"
    fund_details: str = "fund/details"
    fundings: str = "utils/activityLog/fundingOnly"
    market_status: str = "api/utils/marketStatus"
    orders: str = "users/accounts/orders"
    quotes: str = "quotes/marketData/{symbols}"
    rate: str = "api/wallet/rate"
    transactions: str = "users/accounts/transactions"
    user: str = "user"


STAKE_URL = "https://prd-api.stake.com.au/api/"