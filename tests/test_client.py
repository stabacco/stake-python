import pytest
from aioresponses import aioresponses

from stake import CredentialsLoginRequest
from stake import SessionTokenLoginRequest
from stake import StakeClient
from stake.client import HttpClient
from stake.client import InvalidLoginException
from stake.constant import Url


def test_credentials_login_serializing():

    request = CredentialsLoginRequest(
        username="unknown@user.com", remember_me_days=15, password="WeirdPassword",
    )

    assert request.dict(by_alias=True) == {
        "username": "unknown@user.com",
        "password": "WeirdPassword",
        "rememberMeDays": 15,
    }


@pytest.mark.asyncio
async def test_credentials_login():
    request = CredentialsLoginRequest(
        username="unknown@user.com", password="WeirdPassword"
    )
    with aioresponses() as m:
        m.post(
            HttpClient.url(Url.create_session),
            payload=request.dict(by_alias=True),
            status=400,
            body={
                "error_description": "Invalid username or password",
                "error": "invalid_grant",
            },
        )
        with pytest.raises(InvalidLoginException):
            async with StakeClient(request=request) as client:
                assert client

    request = SessionTokenLoginRequest(token="invalidtoken002")
    with pytest.raises(InvalidLoginException):
        async with StakeClient(request=request) as client:
            assert client
