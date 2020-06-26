import asyncio
import os
from enum import Enum
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urljoin

from aiohttp_requests import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from stake import equity
from stake import funding
from stake import product
from stake import report
from stake import trade
from stake import user

STAKE_URL = "https://prd-api.stake.com.au/api/"

load_dotenv()

__all__ = ["StakeClient", "CredentialsLoginRequest", "SessionTokenLoginRequest"]


class EndPoints(str, Enum):
    equity_positions: str = "users/accounts/equityPositions"
    transactions: str = "users/accounts/transactions"
    orders: str = "users/accounts/orders"
    cash_available: str = "users/accounts/cashAvailableForWithdrawal"
    quotes: str = "quotes/marketData/{symbols}"
    user: str = "user"
    fundings: str = "utils/activityLog/fundingOnly"
    fund_details: str = "fund/details"
    account_balance: str = "cma/getAccountBalance"
    rate: str = "api/wallet/rate"
    account_transactions: str = "users/accounts/accountTransactions"  # post
    market_status: str = "api/utils/marketStatus"


class CredentialsLoginRequest(BaseModel):

    username: str = os.getenv("STAKE_USER")
    password: str = os.getenv("STAKE_PASS")
    rememberMeDays: str = "30"


class SessionTokenLoginRequest(BaseModel):
    """Token based authentication, use this if 2FA is enabled.
    """

    token: str = os.getenv("STAKE_TOKEN")


class _StakeClient:
    def __init__(self):
        self.user = None
        self.headers = {
            "Accept": "application/json",
            "Host": "prd-api.stake.com.au",
            "Origin": "https://stake.com.au",
            "Referer": "https://stake.com.au",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Content-Type": "application/json",
        }

        self.fundings = funding.FundingsClient(self)
        self.products = product.ProductsClient(self)
        self.trades = trade.TradesClient(self)

    @staticmethod
    def _url(endpoint: str) -> str:
        """Generates an url

        Args:
            endpoint (str): the final part of the enpoint

        Returns:
            str: the full url
        """
        return urljoin(STAKE_URL, endpoint, allow_fragments=True)

    async def _get(self, url: str) -> dict:
        response = await requests.get(self._url(url), headers=self.headers)
        response.raise_for_status()
        return await response.json()

    async def _post(self, url, payload: dict) -> dict:
        response = await requests.post(
            self._url(url), headers=self.headers, json=payload
        )
        response.raise_for_status()
        return await response.json()

    async def _delete(self, url, payload: dict = None) -> bool:
        response = await requests.delete(
            self._url(url), headers=self.headers, json=payload or {}
        )
        return response.status <= 399

    async def login(
        self, login_request: Union[CredentialsLoginRequest, SessionTokenLoginRequest]
    ) -> user.User:

        if isinstance(login_request, CredentialsLoginRequest):
            data = await self._post(
                self._url("sessions/createSession"), login_request.dict()
            )
            self.headers.update({"Stake-Session-Token": data["sessionKey"]})
        else:
            self.headers.update({"Stake-Session-Token": login_request.token})

        user_data = await self._get(self._url("user/"))
        self.user = user.User(**user_data)
        return self.user

    # async def get_fundings(
    #     self, start_date: str = None, end_date: str = None
    # ) -> List[funding.Funding]:
    #     start_date = start_date or last_year()
    #     end_date = end_date or today()
    #
    #     payload = {"endDate": end_date, "startDate": start_date}
    #     data = await self._post("utils/activityLog/fundingOnly", payload=payload)
    #
    #     return [funding.Funding(**d) for d in data]

    # async def get_funds_in_flight(self) -> dict:
    #     return await self._get("fund/details")

    async def get_equities(self) -> equity.EquityPositions:
        data = await self._get("users/accounts/equityPositions")
        return equity.EquityPositions(**data)

    # async def get_product(self, symbol: str) -> Optional[Product]:
    #     """Returns the matching product"""
    #     data = await self._get(f"products/searchProduct?symbol={symbol}&page=1&max=1")
    #
    #     if not data["products"]:
    #         return None
    #
    #     return Product(**data["products"][0])

    async def get_market_status(self) -> dict:
        return await self._get("utils/marketStatus")

    async def get_marked_data(self, symbols: List[str]) -> Optional[dict]:

        if not symbols:
            return None

        return await self._get(self._url(f"quotes/marketData/{'.'.join(symbols)}"))

    async def sell_order(self):
        {
            "userId": self.user.userId,
            "itemId": "a45b1c39-d1a4-4a90-a388-c34b1257503a",
            "itemType": "instrument",
            "orderType": "stop",
            "quantity": "8.16321243",
            "stopPrice": "4.9",
            "limitPrice": "",
            "comments": "",
        }

    async def download_report(self, request: report.ReportRequest) -> dict:
        {
            "dateStart": "2020-05-22T07:20:20.057Z",
            "dateEnd": "2020-06-22T07:20:20.057Z",
            "reportFormat": "XLS",
            "reportName": "OrderTrans",
        }


async def StakeClient(
    request: Union[CredentialsLoginRequest, SessionTokenLoginRequest] = None
) -> _StakeClient:
    """ Returns a logged in _StakeClient.

    Args:
        request: the login request. credentials or token
    Returns:
        an instance of the _StakeClient

    """
    c = _StakeClient()
    request = request or SessionTokenLoginRequest()
    await c.login(request)
    return c


async def main():

    client = await StakeClient()
    user = client.user
    fundings, funds_in_flight, equities = await asyncio.gather(
        client.products.search(["Technology"]),
        client.products.get("AAPL"),
        client.fundings.list(funding.FundingRequest()),
    )

    buy_apple = await client.trades.buy(
        "AAPL", trade.LimitBuyRequest(limitPrice=300, quantity=1)
    )

    import time

    time.sleep(30)
    # cancel buy
    cancelbuy = await client.trades.cancel(buy_apple.dwOrderId)
    # print(client.user)
    return fundings, funds_in_flight, equities


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fundings, in_flight, market_status = loop.run_until_complete(main())
    import pprint

    # pprint.pprint(fundings)
