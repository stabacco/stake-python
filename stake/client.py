import os
from typing import Union
from urllib.parse import urljoin

from aiohttp_requests import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from stake import constant
from stake import equity
from stake import funding
from stake import order
from stake import product
from stake import trade
from stake import transaction
from stake import user

load_dotenv()

__all__ = ["StakeClient", "CredentialsLoginRequest", "SessionTokenLoginRequest"]


class CredentialsLoginRequest(BaseModel):

    username: str = os.getenv("STAKE_USER", "")
    password: str = os.getenv("STAKE_PASS", "")
    rememberMeDays: str = "30"


class SessionTokenLoginRequest(BaseModel):
    """Token based authentication, use this if 2FA is enabled."""

    token: str = os.getenv("STAKE_TOKEN", "")


class HttpClient:
    """Handles http calls to the Stake API."""

    @staticmethod
    def url(endpoint: str) -> str:
        """Generates an url.

        Args:
            endpoint (str): the final part of the enpoint

        Returns:
            str: the full url
        """
        return urljoin(constant.STAKE_URL, endpoint, allow_fragments=True)

    @staticmethod
    async def get(url: str, headers: dict = None) -> dict:
        response = await requests.get(HttpClient.url(url), headers=headers)
        response.raise_for_status()
        return await response.json()

    @staticmethod
    async def post(url, payload: dict, headers: dict = None) -> dict:
        response = await requests.post(
            HttpClient.url(url), headers=headers, json=payload
        )
        response.raise_for_status()
        return await response.json()

    @staticmethod
    async def delete(url, payload: dict = None, headers: dict = None) -> bool:
        response = await requests.delete(
            HttpClient.url(url), headers=headers, json=payload
        )
        return response.status <= 399


class _StakeClient:
    def __init__(self):
        self.user = None
        self.headers = {
            "Accept": "application/json",
            "Host": "prd-api.stake.com.au",
            "Origin": constant.STAKE_URL,
            "Referer": constant.STAKE_URL,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Content-Type": "application/json",
        }
        self.httpClient = HttpClient
        self.fundings = funding.FundingsClient(self)
        self.products = product.ProductsClient(self)
        self.trades = trade.TradesClient(self)
        self.orders = order.OrdersClient(self)
        self.equities = equity.EquitiesClient(self)
        self.transactions = transaction.TransactionsClient(self)

    #
    # @staticmethod
    # def url(endpoint: str) -> str:
    #     """Generates an url.
    #
    #     Args:
    #         endpoint (str): the final part of the enpoint
    #
    #     Returns:
    #         str: the full url
    #     """
    #     return urljoin(constant.STAKE_URL, endpoint, allow_fragments=True)
    #
    async def get(self, url: str) -> dict:
        return await self.httpClient.get(url, headers=self.headers)

    async def post(self, url: str, payload: dict) -> dict:
        return await self.httpClient.post(url, payload=payload, headers=self.headers)

    async def delete(self, url: str, payload: dict = None) -> bool:
        return await self.httpClient.delete(url, headers=self.headers, payload=payload)

    async def login(
        self, login_request: Union[CredentialsLoginRequest, SessionTokenLoginRequest]
    ) -> user.User:

        if isinstance(login_request, CredentialsLoginRequest):
            data = await self.httpClient.post(
                constant.Url.create_session, payload=login_request.dict()
            )
            self.headers.update({"Stake-Session-Token": data["sessionKey"]})
        else:
            self.headers.update({"Stake-Session-Token": login_request.token})

        user_data = await self.httpClient.get(constant.Url.user, headers=self.headers)
        self.user = user.User(**user_data)
        return self.user


async def StakeClient(
    request: Union[CredentialsLoginRequest, SessionTokenLoginRequest] = None
) -> _StakeClient:
    """Returns a logged in _StakeClient.

    Args:
        request: the login request. credentials or token
    Returns:
        an instance of the _StakeClient
    """
    c = _StakeClient()
    request = request or SessionTokenLoginRequest()
    await c.login(request)
    return c
