import pytest

from stake import CredentialsLoginRequest, SessionTokenLoginRequest, StakeClient
from stake.client import InvalidLoginException


def test_credentials_login_serializing():

    request = CredentialsLoginRequest(
        username="unknown@user.com",
        remember_me_days=15,
        password="WeirdPassword",
    )

    assert request.dict(by_alias=True) == {
        "username": "unknown@user.com",
        "password": "WeirdPassword",
        "platformType": "WEB_f5K2x3",
        "rememberMeDays": 15,
        "otp": None,
    }


@pytest.mark.asyncio
async def test_credentials_login():
    request = CredentialsLoginRequest(
        username="unknown@user.com", password="WeirdPassword"
    )

    with pytest.raises(InvalidLoginException):
        async with StakeClient(request=request) as client:
            assert client

    request = SessionTokenLoginRequest(token="invalidtoken002")
    with pytest.raises(InvalidLoginException):
        async with StakeClient(request=request) as client:
            assert client
