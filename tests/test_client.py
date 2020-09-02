import pytest

from stake import CredentialsLoginRequest
from stake import SessionTokenLoginRequest
from stake import StakeClient
from stake.client import InvalidLoginException
from stake.client import StakeSession

request = CredentialsLoginRequest(
    username="unknown@user.com",
    remember_me_days=15,
    password="WeirdPassword",
)

def test_credentials_login_serializing():
    print(request)
    assert request.dict(by_alias=True) == {"username": "unknown@user.com", 'password': 'WeirdPassword', 'rememberMeDays': 15}


@pytest.mark.asyncio
async def test_invalid_login(tracing_client):
    request = CredentialsLoginRequest(
        username="unknown@user.com", password="WeirdPassword"
    )
    with pytest.raises(InvalidLoginException):
        await StakeClient(request=request)

    request = SessionTokenLoginRequest(token="invalidtoken002")
    with pytest.raises(InvalidLoginException):
        await StakeClient(request=request)


@pytest.mark.asyncio
async def test_contextmanager(tracing_client):
    request = CredentialsLoginRequest(
        username="tabacco.stefano@gmail.com", password="Stegala74"
    )
    async with StakeSession(request=request) as client:
        print(client)
