import pytest
from aioresponses import aioresponses

from stake import CredentialsLoginRequest, SessionTokenLoginRequest, StakeClient
from stake.client import HttpClient, InvalidLoginException
from stake.constant import Url


def test_credentials_login_serializing():

    request = CredentialsLoginRequest(
        username="unknown@user.com", remember_me_days=15, password="WeirdPassword",
    )

    assert request.dict(by_alias=True) == {
        "username": "unknown@user.com",
        "password": "WeirdPassword",
        "rememberMeDays": 15,
        "otp": None,
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
