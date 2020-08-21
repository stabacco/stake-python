import os
from typing import Optional
from typing import Union
from urllib.parse import urljoin

from aiohttp_requests import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field

from stake import constant
from stake import equity
from stake import fx
from stake import funding
from stake import market
from stake import order
from stake import product
from stake import trade
from stake import transaction
from stake import user
from stake import watchlist

load_dotenv()

__all__ = ["StakeClient", "CredentialsLoginRequest", "SessionTokenLoginRequest"]


class CredentialsLoginRequest(BaseModel):
    username: str = Field(default_factory=lambda *_: os.getenv("STAKE_USER", ""))
    password: str = Field(default_factory=lambda *_: os.getenv("STAKE_PASS", ""))
    rememberMeDays: str = "30"


class SessionTokenLoginRequest(BaseModel):
    """Token based authentication, use this if 2FA is enabled."""

    token: str = Field(default_factory=lambda *_: os.getenv("STAKE_TOKEN", ""))


class Headers(BaseModel):
    accept: str = Field("application/json", alias="Accept")
    content_type: str = Field("application/json", alias="Content-Type")
    stake_session_token: Optional[str] = Field(None, alias="Stake-Session-Token")


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

        self.headers = Headers()
        self.httpClient = HttpClient

        self.fx = fx.FxClient(self)
        self.fundings = funding.FundingsClient(self)
        self.products = product.ProductsClient(self)
        self.trades = trade.TradesClient(self)
        self.orders = order.OrdersClient(self)
        self.equities = equity.EquitiesClient(self)
        self.transactions = transaction.TransactionsClient(self)
        self.market = market.MarketClient(self)
        self.watchlist = watchlist.WatchlistClient(self)

    #
    async def get(self, url: str) -> dict:
        return await self.httpClient.get(url, headers=self.headers.dict(by_alias=True))

    async def post(self, url: str, payload: dict) -> dict:
        return await self.httpClient.post(
            url, payload=payload, headers=self.headers.dict(by_alias=True)
        )

    async def delete(self, url: str, payload: dict = None) -> bool:
        return await self.httpClient.delete(
            url, headers=self.headers.dict(by_alias=True), payload=payload
        )

    async def login(
        self, login_request: Union[CredentialsLoginRequest, SessionTokenLoginRequest]
    ) -> user.User:

        if isinstance(login_request, CredentialsLoginRequest):
            data = await self.httpClient.post(
                constant.Url.create_session, payload=login_request.dict()
            )
            self.headers.stake_session_token = data["sessionKey"]
        else:
            self.headers.stake_session_token = login_request.token

        user_data = await self.get(constant.Url.user)
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
