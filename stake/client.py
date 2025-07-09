import logging
import os
from typing import Optional, Union

import aiohttp
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from stake import (
    asx,
    constant,
    equity,
    funding,
    fx,
    market,
    order,
    product,
    ratings,
    statement,
    trade,
    transaction,
    user,
    watchlist,
)
from stake.common import camelcase

load_dotenv()

logger = logging.getLogger(__name__)

__all__ = ["StakeClient", "CredentialsLoginRequest", "SessionTokenLoginRequest"]


class CredentialsLoginRequest(BaseModel):
    username: str = Field(default_factory=lambda *_: os.getenv("STAKE_USER", ""))
    password: str = Field(default_factory=lambda *_: os.getenv("STAKE_PASS", ""))
    otp: Optional[str] = None  # This is the code for 2FA
    remember_me_days: int = 30
    platform_type: str = Field(
        default_factory=lambda *_: os.getenv("STAKE_PLATFORM_TYPE", "WEB_f5K2x3")
    )  # Note: find this in the login page
    model_config = ConfigDict(alias_generator=camelcase, populate_by_name=True)


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
            endpoint (str): the  full url

        Returns:
            str: the full url
        """
        logger.debug("Endpoint %s", endpoint)
        return endpoint

    @staticmethod
    async def get(
        url: str, payload: dict | None = None, headers: dict | None = None
    ) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.get(
                HttpClient.url(url), headers=headers, json=payload
            )
            return await response.json()

    @staticmethod
    async def post(url: str, payload: dict, headers: dict | None = None) -> dict:

        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            logger.debug("POST %s %s", url, payload)
            response = await session.post(
                HttpClient.url(url), headers=headers, json=payload
            )
            return await response.json()

    @staticmethod
    async def delete(
        url: str, payload: dict | None = None, headers: dict | None = None
    ) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.delete(
                HttpClient.url(url), headers=headers, json=payload
            )
            return await response.json()


class InvalidLoginException(Exception):
    pass


class StakeClient:
    """The main client to interact with the Stake API."""

    def __init__(
        self,
        request: Union[CredentialsLoginRequest, SessionTokenLoginRequest, None] = None,
        exchange: Union[constant.NYSEUrl, constant.ASXUrl] = constant.NYSE,
    ):
        """

        Args:
            request (Union[CredentialsLoginRequest,
                SessionTokenLoginRequest], optional):
                The authentication method: either a session token or credentials.
                Defaults to None.
            exchange (constant.BaseUrl, optional):
                the stock exchange to be used.
                Defaults to constant.NYSE.
        """
        self.user: Optional[user.User] = None
        self.set_exchange(exchange=exchange)
        self.headers = Headers()
        self.http_client = HttpClient
        self._login_request = request or SessionTokenLoginRequest()

    def set_exchange(self, exchange: Union[constant.NYSEUrl, constant.ASXUrl]) -> None:
        self.exchange = exchange

        self.watchlist: watchlist.WatchlistClient = watchlist.WatchlistClient(self)

        if exchange == constant.ASX:
            self.equities: Union[asx.equity.EquitiesClient, equity.EquitiesClient] = (
                asx.equity.EquitiesClient(self)
            )
            self.fundings: Union[asx.funding.FundingsClient, funding.FundingsClient] = (
                asx.funding.FundingsClient(self)
            )
            self.market: Union[asx.market.MarketClient, market.MarketClient] = (
                asx.market.MarketClient(self)
            )
            self.orders: Union[asx.order.OrdersClient, order.OrdersClient] = (
                asx.order.OrdersClient(self)
            )
            self.products: Union[asx.product.ProductsClient, product.ProductsClient] = (
                asx.product.ProductsClient(self)
            )
            self.trades: Union[asx.trade.TradesClient, trade.TradesClient] = (
                asx.trade.TradesClient(self)
            )
            self.transactions: Union[
                asx.transaction.TransactionsClient, transaction.TransactionsClient
            ] = asx.transaction.TransactionsClient(self)
            # ratings is unsupported.
            # statements is unsupported.
        else:
            self.equities = equity.EquitiesClient(self)
            self.fundings = funding.FundingsClient(self)
            self.fx = fx.FxClient(self)
            self.market = market.MarketClient(self)
            self.orders = order.OrdersClient(self)
            self.products = product.ProductsClient(self)
            self.ratings = ratings.RatingsClient(self)
            self.trades = trade.TradesClient(self)
            self.transactions = transaction.TransactionsClient(self)
            self.statements = statement.StatementClient(self)

    async def get(self, url: str, payload: dict | None = None) -> dict:
        """Performs an HTTP get operation.

        Args:
            url (str): the current endpoint
            payload (dict): The request's body.

        Returns:
            dict: the json response
        """

        return await self.http_client.get(
            url, payload=payload, headers=self.headers.model_dump(by_alias=True)
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
            url, payload=payload, headers=self.headers.model_dump(by_alias=True)
        )

    async def delete(self, url: str, payload: dict | None = None) -> dict:
        """Performs an HTTP delete operation.

        Args:
            url (str): the current endpoint
            payload (dict, optional): The request's body. Defaults to None.

        Returns:
            bool: True if the deletion was successful.
        """
        return await self.http_client.delete(
            url, headers=self.headers.model_dump(by_alias=True), payload=payload
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
                    constant.NYSE.create_session,
                    payload=login_request.model_dump(by_alias=True),
                )

                self.headers.stake_session_token = data["sessionKey"]
            except aiohttp.client_exceptions.ClientResponseError as error:
                raise InvalidLoginException("Invalid Login Credentials") from error
        else:
            self.headers.stake_session_token = login_request.token
        try:
            user_data = await self.get(self.exchange.users)
        except aiohttp.client_exceptions.ClientResponseError as error:
            raise InvalidLoginException("Invalid Session Token") from error

        self.user = user.User(**user_data)
        return self.user

    async def __aenter__(self):
        await self.login(self._login_request)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass
