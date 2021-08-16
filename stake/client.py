import os
from typing import Optional, Union
from urllib.parse import urljoin

import aiohttp
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from stake import (
    constant,
    equity,
    funding,
    fx,
    market,
    order,
    product,
    ratings,
    trade,
    transaction,
    user,
    watchlist,
)
from stake.common import camelcase

load_dotenv()

__all__ = ["StakeClient", "CredentialsLoginRequest", "SessionTokenLoginRequest"]

global test_name


class CredentialsLoginRequest(BaseModel):
    username: str = Field(default_factory=lambda *_: os.getenv("STAKE_USER", ""))
    password: str = Field(default_factory=lambda *_: os.getenv("STAKE_PASS", ""))
    otp: Optional[str] = None  # This is the code for 2FA
    remember_me_days: int = 30
    platform_type: str = Field(
        default_factory=lambda *_: os.getenv("STAKE_PLATFORM_TYPE", "WEB_f5K2x3")
    )  # Note: find this in the login page

    class Config:
        alias_generator = camelcase
        allow_population_by_field_name = True


class SessionTokenLoginRequest(BaseModel):
    """Token based authentication, use this if 2FA is enabled."""

    token: str = Field(default_factory=lambda *_: os.getenv("STAKE_TOKEN", ""))


class Headers(BaseModel):
    accept: str = Field("application/json", alias="Accept")
    content_type: str = Field("application/json", alias="Content-Type")
    stake_session_token: Optional[str] = Field("", alias="Stake-Session-Token")


class HttpClient:
    """Handles http calls to the Stake API."""

    @staticmethod
    def url(endpoint: str) -> str:
        """Generates a stake api url.

        Args:
            endpoint (str): the final part of the url

        Returns:
            str: the full url
        """
        return urljoin(constant.STAKE_URL, endpoint, allow_fragments=True)

    @staticmethod
    async def get(url: str, payload: dict = None, headers: dict = None) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.get(
                HttpClient.url(url), headers=headers, json=payload
            )
            return await response.json()

    @staticmethod
    async def post(url: str, payload: dict, headers: dict = None) -> dict:

        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.post(
                HttpClient.url(url), headers=headers, json=payload
            )
            return await response.json()

    @staticmethod
    async def delete(url: str, payload: dict = None, headers: dict = None) -> bool:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.delete(
                HttpClient.url(url), headers=headers, json=payload
            )
            return response.status <= 399


class InvalidLoginException(Exception):
    pass


class StakeClient:
    """The main client to interact with the Stake API."""

    def __init__(
        self, request: Union[CredentialsLoginRequest, SessionTokenLoginRequest] = None
    ):
        self.user: Optional[user.User] = None

        self.headers = Headers()
        self.http_client = HttpClient

        # register all the clients
        self.equities = equity.EquitiesClient(self)
        self.fx = fx.FxClient(self)
        self.fundings = funding.FundingsClient(self)
        self.market = market.MarketClient(self)
        self.orders = order.OrdersClient(self)
        self.products = product.ProductsClient(self)
        self.trades = trade.TradesClient(self)
        self.transactions = transaction.TransactionsClient(self)
        self.watchlist = watchlist.WatchlistClient(self)
        self.ratings = ratings.RatingsClient(self)

        self._login_request = request or SessionTokenLoginRequest()

    async def get(self, url: str, payload: dict = None) -> dict:
        """Performs an HTTP get operation.

        Args:
            url (str): the current endpoint
            payload (dict): The request's body.

        Returns:
            dict: the json response
        """

        return await self.http_client.get(
            url, payload=payload, headers=self.headers.dict(by_alias=True)
        )

    async def post(self, url: str, payload: dict) -> dict:
        """Performs an HTTP post operation.

        Args:
            url (str): the current endpoint
            payload (dict): The request's body.

        Returns:
            dict: the json response
        """

        return await self.http_client.post(
            url, payload=payload, headers=self.headers.dict(by_alias=True)
        )

    async def delete(self, url: str, payload: dict = None) -> bool:
        """Performs an HTTP delete operation.

        Args:
            url (str): the current endpoint
            payload (dict, optional): The request's body. Defaults to None.

        Returns:
            bool: True if the deletion was successful.
        """
        return await self.http_client.delete(
            url, headers=self.headers.dict(by_alias=True), payload=payload
        )

    async def login(
        self, login_request: Union[CredentialsLoginRequest, SessionTokenLoginRequest]
    ) -> user.User:
        """Authenticates to the stake api.

        Args:
            login_request (Union[CredentialsLoginRequest, SessionTokenLoginRequest]):
            you can authenticate either with your credentials(username, password)
            or with an existing session token.

        Returns:
            user.User: the authenticated user.
        """
        if isinstance(login_request, CredentialsLoginRequest):
            try:
                data = await self.post(
                    constant.Url.create_session,
                    payload=login_request.dict(by_alias=True),
                )

                self.headers.stake_session_token = data["sessionKey"]
            except aiohttp.client_exceptions.ClientResponseError as error:
                raise InvalidLoginException("Invalid Login Credentials") from error
        else:
            self.headers.stake_session_token = login_request.token
        try:
            user_data = await self.get(constant.Url.user)
        except aiohttp.client_exceptions.ClientResponseError as error:
            raise InvalidLoginException("Invalid Session Token") from error

        self.user = user.User(**user_data)
        return self.user

    async def __aenter__(self):
        await self.login(self._login_request)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass
